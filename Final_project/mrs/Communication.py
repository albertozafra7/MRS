import socket
import json
import time
import numpy as np
from multiprocessing import Process, Value, Array, Lock


class Communication:
    def __init__(self, id, nL, nG, port, dirs):

        # ++++++++++++++++ Custom Properties ++++++++++++++++

        self.id = id
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
        self.initialize_socket()
        
        self.lis = Process(target=self.listener, args=())
        self.lis.start()

        self.tal = Process(target=self.talker, args=())
        self.tal.start()

        print("Listening")

        print("aaaaaaaaaaaaaaaaaaaaa")
        print(self.get_global_positions())

    def initialize_socket(self):
        # Define port to listen on
        PORT = self.port  # Replace with the same port number used by sender

        # Create a socket object
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Bind the socket to the port
        self.sock.bind(("", PORT))

        # Listen for incoming connections
        self.sock.listen(1)
        print("Listening in port", PORT)

    def listener(self):

        while not self.finished.value:

            # Accept a connection
            conn, addr = self.sock.accept()

            print("Connected by", addr)

            # Receive data from the client
            data = conn.recv(1024).decode()

            # Decode JSON data
            try:
                json_data = json.loads(data)
                print("Received JSON data:", json_data)

                # Prepare a reply message (modify as needed)
                reply = {"id": self.id, "positions": self.get_global_positions().tolist()}
                json_data = json.dumps(reply)

                # Encode and send the reply
                conn.sendall(json_data.encode())
            except json.JSONDecodeError:
                print("Error decoding JSON data:", data)
                reply = "Error: Invalid JSON data received"
                conn.sendall(reply.encode())

            # Close the connection
            conn.close()
        print("Closing lock")
        self.sock.close()

    def talker(self):

        numDirs = len(self.dirs)

        i = 0
        while not self.finished.value:
            # Create a socket object
            comm = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            HOST = self.dirs[i].host
            PORT = self.dirs[i].port
            print("talking to: ",HOST,":",PORT)

            # Sample JSON data
            data = {"id": self.id, "positions": self.get_global_positions().tolist()}

            # Encode data to JSON string
            json_data = json.dumps(data)

            # Send the JSON string
            try:
                # Connect to the server
                comm.connect((HOST, PORT))
                comm.sendall(json_data.encode())
                print("Sent JSON data:", json_data)
                # Receive reply from the listener
                reply = comm.recv(1024).decode()
                try:
                    json_data = json.loads(reply)
                    print(f"Received reply: ", json_data)

                except json.JSONDecodeError:
                    print("Error decoding JSON data:", reply)
                    
                # Close the socket
                comm.close()
            except:
                print("Connection refused:",HOST,":",PORT)

            i = (i + 1) % numDirs

            time.sleep(2)

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