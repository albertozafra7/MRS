from __future__ import absolute_import, division, print_function, unicode_literals
import random
import numpy as np  # Make numpy available using np.
from matplotlib import pyplot as plt # Plotting of the graph

class bot:
    # def __init__(self,n_agents=4,link_list=np.array([[0, 1], [0, 2], [1,2], [2, 3]]),sx0=[0,1,2,3],sy0=[0,3,2,4],undirected=True,alpha=0.004):
    def __init__(self,id,connections,pos,update_period,step_size):
        
        self.id = id
        self.neighbors = connections
        self.pos = pos
        self.update_period = update_period
        self.step_size = step_size

    def get_id(self):
        return self.id

    def set_neighbors(self,connections):
        self.neighbors = connections
        
    def add_neighbor(self,neighbor):
        if not np.isin(neighbor,self.neighbors):
            self.neighbors.append(neighbor)
        
    def get_neighbors(self):
        return self.neighbors
        
    def get_random_neighbor(self):
        return random.choice(self.neighbors)
    
    def move(self,pose):
        self.pos = pose
        
    def get_pos(self):
        return self.pos
    
    def step_rendevous(self):
        neigh = self.get_random_neighbor()
    
        [pos1,pos2] = self.compute_step_rendevous(self.get_pos(),neigh.get_pos(),self.step_size)

        self.move(pos1)
        neigh.move(pos2)
        return self.id, pos1, neigh.get_id(), pos2
        
    def compute_step_rendevous(self,pos1,pos2,step_size):
        pos1[0] = pos1[0]+step_size*(pos2[0]-pos1[0])
        pos1[1] = pos1[1]+step_size*(pos2[1]-pos1[1])
        pos2[0] = pos2[0]+step_size*(pos1[0]-pos2[0])
        pos2[1] = pos2[1]+step_size*(pos1[1]-pos2[1])
        
        return pos1, pos2
    
    def step_line(self,offset):
        neigh = self.get_random_neighbor()
        
        offset_bot1 = offset*self.id
        offset_bot2 = offset*neigh.get_id()
        
        [pos1,pos2] = self.compute_step_line(self.get_pos(),neigh.get_pos(),self.step_size,offset_bot1,offset_bot2)
        
        self.move(pos1)
        neigh.move(pos2)
        
    def compute_step_line(pos1,pos2,step_size,offset1,offset2):
        pos1[0] = pos1[0]+step_size*(pos2[0]-pos1[0])+offset1[0]
        pos1[1] = pos1[1]+step_size*(pos2[1]-pos1[1])+offset1[1]
        pos2[0] = pos2[0]+step_size*(pos1[0]-pos2[0])+offset2[0]
        pos2[1] = pos2[1]+step_size*(pos1[1]-pos2[1])+offset2[1]
        
        return pos1, pos2
        
        