from xmlrpc.server import SimpleXMLRPCServer
import xmlrpc.client
import json
import time
import numpy as np
from multiprocessing import Process, Value, Array, Lock

class MyServer(SimpleXMLRPCServer):
    def __init__(self, addr, logRequests=False):
        super().__init__(addr, logRequests)
        self.should_stop = False

    def serve_forever(self):
        while not self.should_stop:
            self.handle_request()

class Communication:
    def __init__(self, nL, nG, idG, idL, ip, port, dirs):

        print("C:","Initializing communications...")

        # ++++++++++++++++ Custom Properties ++++++++++++++++
        self.ip = ip
        self.nL = nL
        self.nG = nG
        self.port = port
        self.dirs = dirs
        self.idG = idG
        self.idL = idL

        # Robot positions nGxnLx3 --> nGxnLx(x,y,t)
        # self.poses = [[[None,None,-1] for _ in range(self.nL)] for _ in range(self.nG)]
        
        self.shared_array = Array('d', nG * nL * 3)
        # Reshape the flat array to the desired shape
        self.poses = np.frombuffer(self.shared_array.get_obj()).reshape(nG, nL, 3)

        self.qT = Array('d', 3)                      # Target pose

        # Locks and stop control
        self.comm_lock = Lock()
        self.finished = Value('b',0)
        
        self.start_connections()
        
        
    def start_servers(self):
        # +++++++++++++ Methods Initialization ++++++++++++++
        # Create a server instance with a listening port
        self.RPCserver = SimpleXMLRPCServer((self.ip, self.port))
        # Register the function as a service
        self.RPCserver.register_introspection_functions()  # Optional for introspection
        self.RPCserver.register_function(self.RPC_get_positions, "RPC_get_positions")
        self.RPCserver.register_function(self.RPC_get_position, "RPC_get_position") 
        self.RPCserver.register_function(self.RPC_finish, "RPC_finish") 
        self.RPCserver.register_function(self.RPC_get_poses, "RPC_get_poses") 
        # Print a message and start serving requests
        print("C:","Server listening on port:",self.port)
        
        self.srv = Process(target=self.service, args=())
        self.srv.start()
        print("C:","srv")
        
        self.tal = Process(target=self.talker, args=())
        self.tal.start()
        print("C:","Talking")

    def service(self):
        cont = True
        while cont:
            self.RPCserver.handle_request()
            with self.comm_lock:
                cont = not self.finished.value
        # self.server.serve_forever()

    def RPC_get_positions(self):
        with self.comm_lock:
            return self.posesTo2Darray().tolist()
    
    def RPC_get_position(self):
        with self.comm_lock:
            return self.poses[self.idG,self.idL,:2].tolist()

    def RPC_finish(self):
        self.finish()
        return "ACK"

    def RPC_get_poses(self,p):
        print("Hola, estoy en getposes me han pasado ", p)
        positions = self.update_positions(np.array(p))
        return positions.tolist()

    def start_connections(self):
        dirs_left = np.ones(len(self.dirs))

        self.server = [None for _ in range(len(dirs_left))]
        for i in range(len(dirs_left)):
            self.server[i] = xmlrpc.client.Server("http://"+self.dirs[i].host+":"+str(self.dirs[i].port))

            print("C:",int(len(dirs_left)-np.sum(dirs_left)),"/",len(dirs_left)," Connected to: ",self.dirs[i].host,":",str(self.dirs[i].port))


    def talker(self):
        print("T: Hemos llegado al talker")
        numDirs = len(self.dirs)
        cont = True
        try:
            i = 0
            print("C: Initial finished value:", self.finished.value)
            while cont:
                # Create a socket object
                # comm = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

                HOST = self.dirs[i].host
                PORT = self.dirs[i].port
                print("C:","T:talking to: ",HOST,":",PORT)

                try:
                    # Create a server proxy object  
                    with self.comm_lock:
                        print("C: Getting poses from server", HOST, PORT)
                        new_poses = np.array(self.server[i].RPC_get_poses(self.poses.tolist()))
                        print("C: Received new poses:", new_poses)
                        np.copyto(self.poses, new_poses)  # Copy the new data into the existing shared array
                        print("C: Updated poses array:", self.poses)

                except Exception as e:
                    print("C:","exception: ",e)

                i = (i + 1) % numDirs

                time.sleep(0.1)
                with self.comm_lock:
                    cont = not self.finished.value
        except Exception as e:
            print("C: talker exception: ", e)
            pass
        print("C:","exiting")        
        self.finished.value = False

    def update_positions(self,p):
        """
            [x,y,t]
        """
        returned_p = []
        # print("C:","updating...")
        # --- locked part ---
        with self.comm_lock:
            mask = np.array(self.poses[:,:,2] < p[:,:,2])
            self.poses[mask] = p[mask]
            returned_p = self.poses
        # --- locked part ---
        
        return returned_p

    def update_position(self,group_id, robot_id, pose):
        """
            [x,y,t]
        """
        # --- locked part ---
        with self.comm_lock:
            self.poses[group_id,robot_id,:] = pose
            
            # print("C:","Robot " + str(robot_id) + " is at " + str(pose))
            # print("C:",self.poses)
        # --- locked part ---

    def get_local_positions(self,group_id):
        """
            [x,y,t]
             [...]
            [x,y,t]
        """
        # We generate the array for storing the agent positions
        qLs = np.zeros((self.nL,3))

        # --- locked part ---
        with self.comm_lock:
            qLs = self.poses[group_id,:,:] # We store all the robot positions
            # print("C:","positions2:",self.poses)
        # --- locked part ---

        return qLs

    def get_global_positions(self):
        """
            [[[x,y,t],[x,y,t],[x,y,t]],[[x,y,t],[x,y,t],[x,y,t]],[[x,y,t],[x,y,t],[x,y,t]]]
             [...]
            [x,y,t]
            [xT,yT,tT]
        """
        # print("C: sending global positions")
        # We generate the array for storing the group positions
        qGs = np.zeros((self.nG+1,3))

        # --- locked part ---
        with self.comm_lock:
            # We compute the middle point of the robots (group position) by averaging all the robot positions
            for i in range(self.nG):
                qGs[i,:] = np.array([np.mean(self.poses[i,:,0]),np.mean(self.poses[i,:,1]),np.max(self.poses[i,:,2])])

            # We add the target position at the end
            qGs[i+1,:] = self.qT
        # --- locked part ---

        # print(qGs)
        return qGs

    def posesTo2Darray(self):
        pos = np.zeros((self.nL*self.nG,2))
        start_id = 0

        for i in range(self.nG):
            pos[start_id:start_id+self.nL,:] = self.poses[i,:,:1]
            start_id += self.nL
        
        return pos

    def stop_servers(self):
        if self.server:
            self.server.shutdown()
            self.server.server_close()
            print(f"Server stopped on {self.ip}:{self.port}")
    
    def finish(self):
        with self.comm_lock:
            self.finished.value = True
            print("C:","Robot with ip: "+ str(self.ip) + " has been killed")
