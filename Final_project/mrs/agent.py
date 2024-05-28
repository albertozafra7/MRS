#!/usr/bin/python
# -*- coding: UTF-8 -*-
from multiprocessing import Process, Value, Array, Lock
import numpy as np
import time     # import the time library for the timestamp
from datetime import datetime
from formation_control_class import formation_control # Our controller class
import utils as ut
import Communication as comm

class agent:

    def __init__(self, num_robots, num_groups, uid, idL, initial_poseL, shapeL, idG, initial_poseG, shapeG, initial_poseT, dir_file, comm_file, rotationL=False, rotationG=False, dt=0.01, KcL=15, KgL=10, KcG=15, KgG=10):

        # ++++++++++++ Custom Properties ++++++++++++
        # Constants
        self.uid = uid                                          # Unique identifier of the agent (int)
        self.nL = num_robots                                    # Number of robots in the group (int)
        self.nG = num_groups                                    # Number of groups (int)
        self.idG = idG                                          # Group identifier of the agent (int)
        self.idL = idL                                          # Local identifier of the agent (int)

        # Local properties
        self.qL = np.zeros((self.nL,3))                         # We generate the initial q array nx(x,y,t)
        self.qL[idL,:] = np.append(initial_poseL, time.time())  # We add the inital pose of the current agent and its timestamp (x,y,t)
        self.formationL = formation_control(num_agents=self.nL, id=idL, initial_pose=self.qL[:,:2], shape=shapeL, shape_center=initial_poseG, Kc=KcL, Kg=KgL, dt=dt, rotation=rotationL)

        # Global properties
        self.qG = np.zeros((self.nG,3))
        self.qG[idG,:] = np.append(initial_poseG, time.time())
        self.formationG = formation_control(num_agents=self.nG, id=idG, initial_pose=self.qG[:,:2], shape=shapeG, shape_center=initial_poseT, Kc=KcG, Kg=KgG, dt=dt, rotation=rotationG)

        # Target properties
        self.qT = initial_poseT

        # General control of the program
        self.stop_flag = False                                  # To enable safe deletion of the object

        # Communication properties
        self.com = comm.Communication(self.nL, self.nG, self.idG, self.idL, ut.readIP(self.uid,dir_file), ut.readPort(self.uid,dir_file), ut.read_directions(self.uid,comm_file,dir_file))


        # ++++++++++++ Methods initialization ++++++++++++
        # We update the new computed position to the communication system
        # self.com.start_servers()
        
        # time.sleep(1)
        self.com.update_position(self.idG, self.idL, self.qL[self.idL,:])

        # We start the simulation
        self.simulate()


    # Control simulation
    def simulate(self):
        while not self.com.finished.value:

            # -------- Global Control -------- 

            # We get all the global positions
            qGs = self.com.get_global_positions()

            self.qT = qGs[-1,:] # We update the target positions
            self.qG[:,:] = qGs[:self.nG,:]  # We update the group positions

            # We update the global control
            self.formationG.update_center(self.qT[:2])  # We update the center position within the global formation
            self.formationG.update_poses(self.qG[:,:2]) # We update the group positions within the global formation

            # We execute the global control
            self.formationG.execute_control()
            self.qG[self.idG,:] = np.append(self.formationG.get_agent_pose(),time.time()) # We update the current group position

            # -------- Local Control -------- 

            # We get all the local positions
            self.qL = self.com.get_local_positions(group_id=self.idG)

            # We update the local control
            self.formationL.update_center(self.qG[self.idG,:2]) # We update the center position within the local formation
            self.formationL.update_poses(self.qL[:,:2])         # We update the agent positions within the local formation 

            # We execute the local control
            self.formationL.execute_control()
            self.qL[self.idL,:] = np.append(self.formationL.get_agent_pose(), time.time()) # We update the current agent position

            # We update the new computed position to the communication system
            self.com.update_position(self.idG, self.idL, self.qL[self.idL,:])
            
            # print("A: Agent " + str(self.uid) + " has the following qs")
            # print("qL = " + str(self.com.get_local_positions(group_id=self.idG)))
            # print("qG = " + str(self.com.get_global_positions()))

            # Maybe here a pause is needed???
            time.sleep(0.02)
            



    def get_agent_pos(self):
         return self.qL[self.idL,:2]