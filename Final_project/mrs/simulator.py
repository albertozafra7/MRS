#!/usr/bin/python
# -*- coding: UTF-8 -*-
from multiprocessing import Process, Value, Array, Lock
import numpy as np
import time     # import the time library for the timestamp
from datetime import datetime
import xmlrpc.client
import utils as ut
import random
import subprocess

class Simulator:

    def __init__(self, conn_file, dir_file, pos_file, shape_file, logs_file, max_iters=1000, height=60, width=60, bot_size=5, group_cols=True, random_cols=False):


        # ++++++++++++++ Custom Properties ++++++++++++++

        # Filepaths
        self.conn_file = self.readFile(conn_file)   # Connections file path (string) -> Contains the connection graph structure as (uid,idL,idG,uid1,uid2,...)
        self.dir_file = self.readFile(dir_file)     # IP directions file path (string) -> Contains the IPS of each robot 
        self.pos_file = self.readFile(pos_file)     # Initial positions file path (string) -> Contains the Intial positions of each robot as (uid,x,y)
        self.shapes_file = self.readFile(shape_file)# Shapes file path (string) -> Contains the list of shapes that we want to reconstruct as (shape(string),rotation(bool))
        self.logs = logs_file                       # Logs file path (string)

        # General control properties
        self.stop_flag = False                      # Stop flag to end the simulation
        self.nG = ut.numGroups(self.conn_file)      # Number of groups in the simulation (int)
        self.nL = []                                # Number of robots in each group (array(int))
        
        # We store the number of robots of each group
        for i in range(self.nG):
            self.nL.append(ut.numRobsInGroup(i,self.conn_file))

        self.nR = sum(self.nL)                      # Total number of robots in the simulation, without counting the target (int)
        
        # We read the initial positions of the robots and target
        initial_qs = ut.readIntialPositions(self.pos_file)
        self.q = initial_qs[:self.nR]               # Currrent robot positions during the simulation, without counting the target (array)

        self.qT = initial_qs[-1]                    # Current target position during the simulation (array) (x,y)
        self.agents = []                            # List of active agents performing operations
        
        shapes = ut.readShape(self.shapes_file)
        self.shapeG = shapes[0]                     # Global formation shape (string)
        self.shapeL = shapes[1:]                    # Local formations within the group
        rotations = ut.readRotations(self.shapes_file)
        self.rotationG = rotations[0]               # Global rotation of the formation (bool)
        self.rotationL = rotations[1:]              # Local rotation of the formations (bool)

        # General plot properties
        self.plt_height = height                    # Height of the plot window (int)
        self.plt_width = width                      # Width of the plot window (int)
        self.plt_bot_size = bot_size                # Bot size within the simulation (int)
        self.plt_group_cols = group_cols            # Stablish if we want to group the local robots with a representative color per group (bool)
        self.plt_random_cols = random_cols          # Stablish if we want to have random colors for each robot (bool)
        self.plt_colors = []                        # Colors to paint the robots within the plot (array)
        
        # General log properties
        self.log_max_iters = max_iters              # Maximum number of iters that the system is going to be running (int)

        # Threading properties
        self.agent_lock = Lock()                    # Locks the memory of the thread


        # ++++++++++++++ Methods Initialization ++++++++++++++
        self.initialize_robots(self.dir_file)
        print("S:Started")
        time.sleep(3)
        print("S:Simulating...")
        self.execute_simulation()
      
      
            
    def execute_simulation(self):
        
        n_iters = 0
        print("ITERATION: 0")
        while not self.stop_flag:
                
            self.update_poses()
            
            # TODO: En lugar de plot evolution, guardar en txt las poses
            # self.plot_evolution()
            self.log_evolution()
            
            if n_iters > self.log_max_iters:
                self.stop_flag = True

            n_iters += 1
            if n_iters%100==0: print("ITERATION: ",n_iters)
            
            time.sleep(0.02)

        print("S:Terminating simulation")
        self.kill_agents()
        
        
            
    def initialize_robots(self,dirsF):
        self.ips = ut.readIPs(dirsF)
        print("S:Initializing simulation")
        
        uid = 0
        start_group_id = 0
        for idG in range(self.nG):
            qG = np.array([np.mean(self.q[start_group_id:start_group_id+self.nL[idG],0]),np.mean(self.q[start_group_id:start_group_id+self.nL[idG],1])])
            for idL in range(self.nL[idG]):
                # We store all the processes
                # self.start_robot(self.ips[uid], self.nL[idG],
                #                     self.nG, uid, idL, self.q[uid], self.shapeL[idG], idG,
                #                     qG, self.shapeG, self.qT, self.rotationL[idG], self.rotationG)
                self.agents.append(Process(target=self.start_robot, args=(self.ips[uid], self.nL[idG],
                                    self.nG, uid, idL, self.q[uid], self.shapeL[idG], idG,
                                    qG, self.shapeG, self.qT, self.rotationL[idG], self.rotationG)))
                
                uid += 1
                
            start_group_id += self.nL[idG]

        
        for process in self.agents:
            process.start()
        print("S:Starting...")
        
        # for process in self.agents:
        #     process.join()

        self.start_connections()
    
 

    def start_robot(self, ip, num_robots, num_groups, uid, idL, initial_poseL, shapeL, idG, initial_poseG, shapeG, initial_poseT, rotationL, rotationG):
        """
        Starts a specified number of robots using a remote SSH call.

        Args:
            num_robots (int): Number of robots in group.
            num_groups (int): Number of groups the robots belong to.
            uid (list): List of unique robot IDs.
            idL (list): List of leader robot IDs (if applicable).
            initial_poseL (list): List of initial poses for leader robots.
            shapeL (list): List of shapes for leader robots.
            idG (list): List of group IDs for robots.
            initial_poseG (list): List of initial poses for group robots.
            shapeG (list): List of shapes for group robots.
            initial_poseT (list): List of initial poses for target robots (if applicable).
            rotationL (list): List of rotations for leader robots.
            rotationG (list): List of rotations for group robots.

        Raises:
            RuntimeError: If the SSH call fails.
        """

        # Construct the complete command string with argument formatting
        command = f"ssh a876628@{ip.host} python3 ./mrs/bot_initializer.py --nL={str(num_robots)} --nG={str(num_groups)} --shapeL={shapeL} --qGx={str(initial_poseG[0])} --qGy={str(initial_poseG[1])} --shapeG={shapeG} --qTx={str(initial_poseT[0])} --qTy={str(initial_poseT[1])} --dirsF=./mrs/params/ips.txt --connF=./mrs/params/connections.txt --qx={str(initial_poseL[0])} --qy={str(initial_poseL[1])} --idG={str(idG)} --idL={str(idL)} --uid={str(uid)}"
        print("$: ",command)
        # if rotationL:
        #     command += " --rotaionL=True"
        # if rotationG:
        #     command += " --rotationG=True"


        # Execute the SSH call with error handling
        try:
            subprocess.run(command.split(), check=True)
            print(f"SSH call successful")  # Print output if desired
        except subprocess.CalledProcessError as e:
            print(f"SSH call failed: {e}")
            raise RuntimeError("Failed to start robots using SSH")

    def start_connections(self):
        dirs_left = np.ones(len(self.ips))

        self.server = [None for _ in range(len(dirs_left))]
        for i in range(len(dirs_left)):
            self.server[i] = xmlrpc.client.Server("http://"+self.ips[i].host+":"+str(self.ips[i].port))

            print("S:Connected to: ",self.ips[i].host,":",str(self.ips[i].port))

    def kill_agents(self):
        # We kill all the agents
        for srv in self.server:
            srv.RPC_finish()

    def update_pose(self,uid):
        self.q[uid,:] = np.array(self.server[uid].RPC_get_position())
    
    def update_group_poses(self,idG):
        start_index = 0
        
        for i in range(self.nG):
            if i == idG:
                break
            else:
                start_index += self.nL[i]
                
        # --- locked part ---
        self.agent_lock.aquire()
        self.q[start_index:start_index+self.nL[idG],:] = self.agents[start_index:start_index+self.nL[idG]].get_agent_pos()
        self.agent_lock.release()
        # --- locked part ---
    
    def update_poses(self):
        # self.q = np.array(self.server[0].RPC_get_positions())
        for uid in range(self.nR):
            self.update_pose(uid)
    
    # TODO: Move target
    
    def readFile(self,file_path):
        try:
            with open(file_path, 'r') as file:
                file_output = file.readlines()
                return file_output
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {file_path}")


    def log_evolution(self):
        with open(self.logs, 'a') as file:
            # file.write(str(self.q))
            # x1,y1;x2,y2;x3,y3; .... |xT,yT\n
            for i in range(self.nR):
                file.write(str(self.q[i,0])+","+str(self.q[i,1]))
                if i < self.nR:
                    file.write(";")
            
            file.write("|"+str(self.qT[0])+","+str(self.qT[1]))
            file.write("\n")