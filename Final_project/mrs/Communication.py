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

        # print("C:","Initializing communications...")

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
        self.finished = False
        
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
        # print("C:","Server listening on port:",self.port)
        
        self.srv = Process(target=self.service, args=())
        self.srv.start()
        # print("C:","srv")
        
        self.tal = Process(target=self.talker, args=())
        self.tal.start()
        # print("C:","Talking")

    def service(self):
        cont = True
        while cont:
            # # print("DEB: HR")
            self.RPCserver.handle_request()
            cont = not self.finished
        # self.RPCserver.serve_forever()

    def RPC_get_positions(self):
        # # print("DEB: RPC_get_positions")
        with self.comm_lock:
            return self.posesTo2Darray().tolist()
    
    def RPC_get_position(self):
        print("DEB: RPC_get_position")
        with self.comm_lock:
            return self.poses[self.idG,self.idL,:2].tolist()

    def RPC_finish(self):
        # # print("DEB: RPC_finish")
        self.finish()
        return "ACK"

    def RPC_get_poses(self,p):
        # # print("DEB: RPC_get_poses")
        # # print("Hola, estoy en getposes me han pasado ", p)
        self.update_positions(np.array(p))
        return "ACK"

    def start_connections(self):
        # # print("DEB: start_connections")
        dirs_left = np.ones(len(self.dirs))

        self.server = [None for _ in range(len(dirs_left))]
        for i in range(len(dirs_left)):
            self.server[i] = xmlrpc.client.Server("http://"+self.dirs[i].host+":"+str(self.dirs[i].port))

            # print("C:",int(len(dirs_left)-np.sum(dirs_left)),"/",len(dirs_left)," Connected to: ",self.dirs[i].host,":",str(self.dirs[i].port))


    def talker(self):
        # # print("DEB: talker")
        # # print("T: Hemos llegado al talker")
        numDirs = len(self.dirs)
        cont = True
        my_poses = np.zeros((self.nG,self.nL,3))
        try:
            i = 0
            # # print("C: Initial finished value:", self.finished.value)
            while cont:
                # Create a socket object
                # comm = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

                HOST = self.dirs[i].host
                PORT = self.dirs[i].port
                # # print("C:","T:talking to: ",HOST,":",PORT)

                try:
                    # Create a server proxy object  
                    # with self.comm_lock:
                    # # print("C: Getting poses from server", HOST, PORT)
                    with self.comm_lock:
                        np.copyto(my_poses, self.poses)

                    res = self.server[i].RPC_get_poses(my_poses.tolist())
                    # # print("C: Received new poses:", new_poses)
                    # np.copyto(self.poses, new_poses)  # Copy the new data into the existing shared array
                    # # print("C: Updated poses array:", self.poses)

                except Exception as e:
                    print("C:","exception: ",e)

                i = (i + 1) % numDirs

                time.sleep(0.01)
                # with self.comm_lock:
                cont = not self.finished
        except Exception as e:
            print("C: talker exception: ", e)
            pass
        # print("C:","exiting")        
        self.finished = False

    def update_positions(self,p):
        """
            [x,y,t]
        """
        # # print("C:","updating...")
        # --- locked part ---
        # # print("DEB: update_positions1",self.port)
        with self.comm_lock:
            # # print("DEB: update_positions2",self.port)
            mask = np.array(self.poses[:,:,2] < p[:,:,2])
            self.poses[mask] = p[mask]
        # --- locked part ---

    def update_position(self,group_id, robot_id, pose):
        """
            [x,y,t]
        """
        # --- locked part ---
        # # print("DEB: update_position1",self.port)
        with self.comm_lock:
            # # print("DEB: update_position2",self.port)
            self.poses[group_id,robot_id,:] = pose
            
            # # print("C:","Robot " + str(robot_id) + " is at " + str(pose))
            # # print("C:",self.poses)
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
        # # print("DEB: get_local_positions1",self.port)
        with self.comm_lock:
            # # print("DEB: get_local_positions2",self.port)
            qLs = self.poses[group_id,:,:] # We store all the robot positions
            # # print("C:","positions2:",self.poses)
        # --- locked part ---

        return qLs

    def get_global_positions(self):
        """
            [[[x,y,t],[x,y,t],[x,y,t]],[[x,y,t],[x,y,t],[x,y,t]],[[x,y,t],[x,y,t],[x,y,t]]]
             [...]
            [x,y,t]
            [xT,yT,tT]
        """
        # # print("C: sending global positions")
        # We generate the array for storing the group positions
        qGs = np.zeros((self.nG+1,3))

        # --- locked part ---
        with self.comm_lock:
            # # print("DEB: get_global_positions")
            # We compute the middle point of the robots (group position) by averaging all the robot positions
            for i in range(self.nG):
                qGs[i,:] = np.array([np.mean(self.poses[i,:,0]),np.mean(self.poses[i,:,1]),np.max(self.poses[i,:,2])])

            # We add the target position at the end
            qGs[i+1,:] = self.qT
        # --- locked part ---

        # print(qGs)
        return qGs

    def posesTo2Darray(self):
        # # print("DEB: posesTo2Darray")
        pos = np.zeros((self.nL*self.nG,2))
        start_id = 0

        for i in range(self.nG):
            pos[start_id:start_id+self.nL,:] = self.poses[i,:,:1]
            start_id += self.nL
        
        return pos

    def stop_servers(self):
        # # print("DEB: stop_servers")
        if self.server:
            self.server.shutdown()
            self.server.server_close()
            # print(f"Server stopped on {self.ip}:{self.port}")
    
    def finish(self):
        # # print("DEB: finish")
        self.finished = True
        # print("C:","Robot with ip: "+ str(self.ip) + " has been killed")
