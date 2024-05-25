#!/usr/bin/python
# -*- coding: UTF-8 -*-
from multiprocessing import Process, Value, Array, Lock
import numpy as np
import time     # import the time library for the timestamp
from datetime import datetime
import utils as ut
import matplotlib
import matplotlib.pyplot as plt
import random

class Simulator:

    def __init__(*, self, conn_file, dir_file, pos_file, shape_file, height=60, width=60, bot_size=5, group_cols=True, random_cols=False):


        # ++++++++++++++ Custom Properties ++++++++++++++

        # Filepaths
        self.conn_file = self.readFile(conn_file)   # Connections file path (string) -> Contains the connection graph structure as (uid,idL,idG,uid1,uid2,...)
        self.dir_file = self.readFile(dir_file)     # IP directions file path (string) -> Contains the IPS of each robot 
        self.pos_file = self.readFile(pos_file)     # Initial positions file path (string) -> Contains the Intial positions of each robot as (uid,x,y)
        self.shapes_file = self.readFile(shape_file)# Shapes file path (string) -> Contains the list of shapes that we want to reconstruct as (shape(string),rotation(bool))

        # General control properties
        self.stop_flag = False                      # Stop flag to end the simulation
        self.nG = ut.numGroups(self.conn_file)      # Number of groups in the simulation (int)
        self.nL = []                                # Number of robots in each group (array(int))
        
        # We store the number of robots of each group
        for i in range(self.nG):
            self.nL.append(ut.numRobsInGroup(i,self.conn_file))

        self.nR = sum(self.nL)                      # Total number of robots in the simulation, without counting the target (int)

        # We read the initial positions of the robots and target
        initial_qs = ut.readInitialPositions(self.pos_file)
        self.q = initial_qs[:self.nR]               # Currrent robot positions during the simulation, without counting the target (array)
        self.qT = initial_qs[-1]                    # Current target position during the simulation (array) (x,y)
        self.agents = []                            # List of active agents performing operations
        shapes = ut.readShape(self.shape_file)
        self.shapeG = shapes[0]                     # Global formation shape (string)
        self.shapeL = shapes[1:]                    # Local formations within the group
        rotations = ut.readRotations(self.shape_file)
        self.rotationG = rotations[0]               # Global rotation of the formation (bool)
        self.rotationL = rotations[1:]              # Local rotation of the formations (bool)

        # General plot properties
        self.plt_height = height                    # Height of the plot window (int)
        self.plt_width = width                      # Width of the plot window (int)
        self.plt_bot_size = bot_size                # Bot size within the simulation (int)
        self.plt_group_cols = group_cols            # Stablish if we want to group the local robots with a representative color per group (bool)
        self.plt_random_cols = random_cols          # Stablish if we want to have random colors for each robot (bool)
        self.plt_colors = []                        # Colors to paint the robots within the plot (array)

        # Threading properties
        self.agent_lock = Lock()                    # Locks the memory of the thread


        # ++++++++++++++ Methods Initialization ++++++++++++++
        self.initialize_robots()
        
        self.execute_simulation()
      
      
            
    def execute_simulation(self):
        while not self.stop_flag:
            self.update_poses()
            
            self.plot_evolution()
        
        print("Terminating simulation")
        
            
    def initialize_robots(self,dirsF):
        ips = ut.readIps(dirsF)
        print("Initializing simulation")
        
        uid = 0
        start_group_id = 0
        for idG in range(self.nG):
            qG = np.array([np.mean(self.q[start_group_id:start_group_id+self.nL[idG],0]),np.mean(self.q[start_group_id:start_group_id+self.nL[idG],1])])
            for idL in range(self.nL[idG]):
                # TODO: CHANGEEEEEEE
                self.agents.append(Process(target=agent(num_robots=self.nL[idG], num_groups=self.nG, uid=uid, idL=idL, initial_poseL=self.q[uid], shapeL=self.shapeL[idG], idG=idG, initial_poseG=qG, shapeG=self.shapeG, initial_poseT=self.qT, rotationL=self.rotationL[idG], rotationG=self.rotationG)))
                self.agents[-1].start()
                uid += 1
                
            start_group_id += self.nL[idG]
            
        
    def update_pose(self,uid):
        # --- locked part ---
        self.agent_lock.aquire()
        self.q[uid,:] = self.agents[uid].get_agent_pos()
        self.agent_lock.release()
        # --- locked part ---
    
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

    def random_color(self):
        # Generate a random color
        return (random.random(), random.random(), random.random())

    def group_colors(self, n_robots):
        # Divide robots into quarters
        colors = [self.random_color()] * n_robots        
        return colors

    def colorize_robots(self):
        
        if not self.plt_colors and self.plt_group_cols:
            self.plt_colors = [(0,0,1)] * (self.nR+1)
            start_id = 0
            # Groupd colors
            for i in range(self.nG):
                self.plt_colors[start_id:start_id+self.nL[i]] = self.group_colors()
                start_id += self.nL[i]

            # The target color
            self.plt_colors[-1] = [self.random_color()]

        elif not self.plt_colors and self.plt_random_cols:
            self.plt_colors = [self.random_color() for _ in range(self.nR+1)]

    def plot_evolution(self):
        # Close the plot window to stop the simulation
        if not plt.fignum_exists(self.fig):
            print("Plot window closed.")
            self.stop_flag = True
            return

        plt.clf()  # Clear existing figure
        # Set the limits of the figure
        plt.xlim(-self.width, self.width)
        plt.ylim(-self.height, self.height)

        # Plot the robots that will follow the formation as a blue dot
        for i in range(self.nR):
            if self.plt_group_cols or self.plt_random_cols:
                plt.plot(self.q[i, 0], self.q[i, 1], 'o', color=self.plt_colors[i],ms=self.bot_size)
            else:
                plt.plot(self.q[i, 0], self.q[i, 1], 'bo', ms=self.bot_size)

        if self.plt_group_cols or self.plt_random_cols:
            plt.plot(self.qT[0], self.qT[1], 'o', color=self.plt_colors[-1],ms=self.bot_size)
        else:
            plt.plot(self.qT[0], self.qT[1], 'ro', ms=self.bot_size)
        # Update the current figure number
        self.fig = plt.gcf().number

        # Update the figure and do a micro-pause
        plt.draw()
        plt.pause(0.001)

