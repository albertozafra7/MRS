from xmlrpc.server import SimpleXMLRPCServer
import xmlrpc.client
import json
import time
import numpy as np
from multiprocessing import Process, Value, Array, Lock
import pudb


class Communication:
    def __init__(self, nL, nG, ip, port, dirs):

        # ++++++++++++++++ Custom Properties ++++++++++++++++

        self.nL = nL
        self.nG = nG
        self.port = port
        self.dirs = dirs

        # Robot positions nGxnLx3 --> nGxnLx(x,y,t)
        self.poses = np.zeros((self.nG,self.nL,3))  # All poses
        self.qT = np.zeros(3)                       # Target pose

        # Locks and stop control
        self.comm_lock = Lock()
        self.finished = Value('b',0)


        # +++++++++++++ Methods Initialization ++++++++++++++
        if port == 60001:
            # self.initialize_socket()
            # self.lis = Process(target=self.listener, args=())
            # self.lis.start()

            # Create a server instance with a listening port
            server = SimpleXMLRPCServer((ip, port))
            # Register the function as a service
            server.register_introspection_functions()  # Optional for introspection
            server.register_function(self.RPC_get_poses, "RPC_get_poses") 
            # Print a message and start serving requests
            print("Server listening on port:",port)
            server.serve_forever()
        else:
            self.tal = Process(target=self.talker, args=())
            self.tal.start()    
            print("Talking")

    def RPC_get_poses(self,p):
        self.update_positions(np.array(p))
        return self.poses.tolist()
        

    # def initialize_socket(self):
    #     # Define port to listen on
    #     PORT = self.port  # Replace with the same port number used by sender

    #     # Create a socket object
    #     self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    #     # Bind the socket to the port
    #     self.sock.bind(("", PORT))

    #     # Listen for incoming connections
    #     self.sock.listen(1)
    #     print("Listening in port", PORT)

    # def listener(self):

    #     # try:
    #     while not self.finished.value:

    #         # Accept a connection
    #         conn, addr = self.sock.accept()

    #         print("L:Connected by", addr)

    #         # Receive data from the client
    #         data = conn.recv(1024).decode()

    #         # Decode JSON data
    #         try:
    #             json_data = json.loads(data)
    #             print("L:Received JSON data:", json_data)
    #             self.update_positions(np.array(json_data["positions"]))

    #             # Prepare a reply message (modify as needed)
    #             reply = {"positions": self.poses.tolist()}
    #             json_data = json.dumps(reply)

    #             # Encode and send the reply
    #             conn.sendall(json_data.encode())
    #         except json.JSONDecodeError:
    #             print("L:Error decoding JSON data:", data)
    #             reply = "Error: Invalid JSON data received"
    #             conn.sendall(reply.encode())

    #         # Close the connection
    #         conn.close()
    #     # except:
    #     #     print("closing")
    #     self.sock.close()
    #     self.finished.value = False
    

    def talker(self):

        numDirs = len(self.dirs)
        try:
            i = 0
            while not self.finished.value:
                # Create a socket object
                # comm = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

                HOST = self.dirs[i].host
                PORT = self.dirs[i].port
                print("T:talking to: ",HOST,":",PORT)
                
                try:
                    # Create a server proxy object
                    server = xmlrpc.client.Server("http://"+HOST+":"+str(PORT))
                    self.update_positions(np.array(server.RPC_get_poses(self.poses.tolist())))
                except Exception as e:
                    print("exception: ",e)
                # # Sample JSON data
                # data = {"positions": self.poses.tolist()}

                # # Encode data to JSON string
                # json_data = json.dumps(data)

                # # Send the JSON string
                # try:
                #     # Connect to the server
                #     comm.connect((HOST, PORT))
                #     comm.sendall(json_data.encode())
                #     print("T:Sent JSON data:", json_data)
                #     # Receive reply from the listener
                #     reply = comm.recv(1024).decode()
                #     try:
                #         json_data = json.loads(reply)
                #         print(f"T:Received reply: ", json_data)
                #         self.update_positions(np.array(json_data["positions"]))

                #     except json.JSONDecodeError:
                #         print("Error decoding JSON data:", reply)
                        
                #     # Close the socket
                #     comm.close()
                # except:
                #     print("Connection refused:",HOST,":",PORT)

                i = (i + 1) % numDirs

                time.sleep(2)
        except:
            print("exiting")
        # comm.close()
        
        self.finished.value = False

    def update_positions(self,p):
        """
            [x,y,t]
        """
        print("updating...")
        # --- locked part ---
        time.sleep(2)
        self.comm_lock.acquire()
        mask = np.array(self.poses[:,:,2] < p[:,:,2])
        self.poses[mask] = p[mask]
        self.comm_lock.release()
        # --- locked part ---

    def update_position(self,group_id, robot_id, pose):
        """
            [x,y,t]
        """
        # --- locked part ---
        self.comm_lock.acquire()
        self.poses[group_id,robot_id,:] = pose
        self.comm_lock.release()
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
        self.comm_lock.acquire()
        qLs = self.poses[group_id,:,:] # We store all the robot positions
        self.comm_lock.release()
        # --- locked part ---

        return qLs

    def get_global_positions(self):
        """
            [[[x,y,t],[x,y,t],[x,y,t]],[[x,y,t],[x,y,t],[x,y,t]],[[x,y,t],[x,y,t],[x,y,t]]]
             [...]
            [x,y,t]
            [xT,yT,tT]
        """
        # We generate the array for storing the group positions
        qGs = np.zeros((self.nG+1,3))

        # --- locked part ---
        self.comm_lock.acquire()
        # We compute the middle point of the robots (group position) by averaging all the robot positions
        for i in range(self.nG):
            qGs[i,:] = np.array([np.mean(self.poses[i,:,0]),np.mean(self.poses[i,:,1]),np.max(self.poses[i,:,2])])

        # We add the target position at the end
        qGs[i+1,:] = self.qT
        self.comm_lock.release()
        # --- locked part ---

        return qGs

    def finish(self):
        self.comm_lock.acquire()
        self.finished = True
        self.comm_lock.release()