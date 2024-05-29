#!/usr/bin/python
# -*- coding: UTF-8 -*-
from multiprocessing import Process, Value, Array, Lock
import numpy as np

class formation_control:

    # Maybe it is necessary to send the initial/current center pose
    def __init__(self, num_agents, id, initial_pose, shape, shape_center, Kc=15, Kg=10, dt=0.01, rotation=False):

        # ++++++++++++ Custom Properties ++++++++++++
        # Agent dependant
        self.n = num_agents +1                          # Number of agents, including the targer (int)
        self.id = id                                    # Id of the current agent (int)


        # Shape formation
        self.shape = shape                              # Desired formation pose (string)
        self.center = shape_center                      # The center of the shape that we want to formate (x,y)

        # Poses --> Take care of this!!
        self.q = np.zeros((self.n,2))                 # Current pose (n+1)x(x,y)
        self.q[:num_agents,:] = initial_pose
        self.q[-1,:] = shape_center

        self.c = self.generate_robot_positions()        # Desired pose (n+1)x(x,y)

        # Robot control params
        self.Kc = Kc                                    # Control gain (float)
        self.Kg = Kg                                    # Rotation Control gain (float)
        self.dt = dt                                    # Timestep (float)
        self.rotate = rotation                          # If we want to rotate around the center of the shape (bool)


    # Returns the current pose of the agent
    def get_agent_pose(self):
        return self.q[self.id,:]
    
    # Updates all the stored poses
    def update_poses(self,new_q):
        self.q = np.vstack((new_q,self.center)) # NOT sure
        # self.q[:self.n-1] = new_q

    # Updates the center of the formation
    def update_center(self,new_center):
        # self.q[-1] = new_center
        self.center = new_center

    def get_desired_agent_pose(self):
        return self.c[self.id,:]

    # Enclosing control law (Kabsch algorithm)
    def execute_control(self):
       
        Q = self.compute_inter_robot_positions(self.q) # Current positions
        C = self.compute_inter_robot_positions(self.c) # Desired relative position between the robots

        # Kabsch algorithm
        A = C.T @ Q
        U, S, V_t = np.linalg.svd(A)
        d = np.sign(np.linalg.det(V_t.T @ U.T))
        D = np.array([[1,0],[0,d]]) # This is because we are working in 2D
        # Compute the rotation matrix
        R = V_t.T @ D @ U.T


        q_Ni = -Q[self.n-1::self.n] # Current distance between the robot and the target
        c_Ni = -C[self.n-1::self.n] # Desired distance between the robot and the target
        
        # Compute the control loop
        q_dot = np.zeros(2)
        # If orbiting control is not selected each of the robot is going to converge to its desired shape position
        if not self.rotate:
            q_dot[:] = self.Kc * (q_Ni[self.id,:] - R @ c_Ni[self.id,:])
            
        # If orbiting control is selected each of the robot is going to follow the next robot based on a Control gain (Kg)
        else: 
            if self.id < self.n-2:
                q_dot[:] = self.Kc * (q_Ni[self.id,:] - R @ c_Ni[self.id,:]) - self.Kg * (q_Ni[self.id+1,:] - q_Ni[self.id,:]) 
            else:
                q_dot[:] = self.Kc * (q_Ni[self.id,:] - R @ c_Ni[self.id,:]) - self.Kg * (q_Ni[0,:] - q_Ni[self.id,:])
            

        # Apply control
        self.q[self.id,:] += q_dot[:] * self.dt


    def compute_inter_robot_positions(self, positions):
    
        rel_pos = np.zeros((self.n*self.n, 2))
        # Compute inter-robot relative positions
        for i in range(self.n):
            for j in range(self.n):
                #print("Position {} with {}".format(i,j))
                rel_pos[i + self.n*j, 0] = positions[j,0] - positions[i,0]
                rel_pos[i + self.n*j, 1] = positions[j,1] - positions[i,1]
        return rel_pos


    def generate_robot_positions(self):
        if self.shape not in ["line", "circle", "grid", "square", "star", "hexagon"]:
            raise ValueError("Invalid shape. Choose from 'line', 'circle', 'grid', 'square', 'star' or 'hexagon'.")
        positions = []
        num_robots = self.n
        num_robots -= 1

        if self.shape == "line":
            # Place robots in a straight line along the x-axis
            mid_point = (0 + (num_robots - 1)) / 2
            for i in range(num_robots):
                positions.append([i - mid_point, 0])
            

        elif self.shape == "circle":
            # Place robots in a circle with radius 1
            for i in range(num_robots):
                angle = 2 * np.pi * i / num_robots
                x = np.cos(angle)
                y = np.sin(angle)
                positions.append([x, y])

        elif self.shape == "grid":
            # Place robots in a grid with roughly equal rows and columns
            side_length = np.ceil(np.sqrt(num_robots))
            offset = (side_length-1)/2
            for i in range(num_robots):
                row = i // side_length
                col = i % side_length
                positions.append([col-offset, row-offset])
                
        elif self.shape == "square":
            # Place robots in a square
            side_length = np.ceil(num_robots/4)
            for i in range(num_robots):
                if i<side_length:
                    row = 0
                    col = i % side_length
                elif i<2*side_length:
                    row = i % side_length
                    col = side_length
                elif i<3*side_length:
                    row = side_length
                    col = side_length - (i % side_length)
                else:
                    row = side_length - (i % side_length)
                    col = 0
                positions.append([col, row])
            # Center the square
            center_offset = (side_length)/2
            for pos in positions:
                pos[0] -= center_offset
                pos[1] -= center_offset

        elif self.shape == "star":
            # Place robots in a star shape (5-pointed star for simplicity)
            star_points = 5
            inner_radius = 0.5
            outer_radius = 1
            star_vertices = []
            
            for i in range(star_points):
                outer_angle = 2 * np.pi * i / star_points
                inner_angle = 2 * np.pi * (i + 0.5) / star_points
                star_vertices.append([outer_radius * np.cos(outer_angle), outer_radius * np.sin(outer_angle)])
                star_vertices.append([inner_radius * np.cos(inner_angle), inner_radius * np.sin(inner_angle)])

            for i in range(len(star_vertices)):
                positions.append(star_vertices[i])

            if num_robots > len(star_vertices):
                # Distribute remaining robots along the edges of the star
                remaining_robots = num_robots - len(star_vertices)
                edges = len(star_vertices)
                robots_per_edge = remaining_robots // edges
                extra_robots = remaining_robots % edges
                edge_points = []

                for i in range(edges):
                    start_point = np.array(star_vertices[i])
                    end_point = np.array(star_vertices[(i + 1) % edges])
                    for j in range(1, robots_per_edge + 1):
                        t = j / (robots_per_edge + 1)
                        point = (1 - t) * start_point + t * end_point
                        edge_points.append(point.tolist())

                # If there are extra robots, distribute them along the edges
                for i in range(extra_robots):
                    start_point = np.array(star_vertices[i])
                    end_point = np.array(star_vertices[(i + 1) % edges])
                    point = (start_point + end_point) / 2
                    edge_points.append(point.tolist())

                positions.extend(edge_points[:remaining_robots])
                
        elif self.shape == "hexagon":
            # Place robots in a hexagon with radius 1
            hexagon_points = 6
            radius = 1
            for i in range(hexagon_points):
                angle = 2 * np.pi * i / hexagon_points
                x = radius * np.cos(angle)
                y = radius * np.sin(angle)
                positions.append([x, y])

            if num_robots > hexagon_points:
                # Distribute remaining robots along the edges
                remaining_robots = num_robots - hexagon_points
                robots_per_edge = remaining_robots // hexagon_points
                extra_robots = remaining_robots % hexagon_points
                edge_points = []

                for i in range(hexagon_points):
                    start_angle = 2 * np.pi * i / hexagon_points
                    end_angle = 2 * np.pi * (i + 1) / hexagon_points
                    start_point = np.array([np.cos(start_angle), np.sin(start_angle)])
                    end_point = np.array([np.cos(end_angle), np.sin(end_angle)])

                    for j in range(1, robots_per_edge + 1):
                        t = j / (robots_per_edge + 1)
                        point = (1 - t) * start_point + t * end_point
                        edge_points.append(point.tolist())

                # If there are extra robots, distribute them along the edges
                for i in range(extra_robots):
                    start_angle = 2 * np.pi * i / hexagon_points
                    end_angle = 2 * np.pi * (i + 1) / hexagon_points
                    start_point = np.array([np.cos(start_angle), np.sin(start_angle)])
                    end_point = np.array([np.cos(end_angle), np.sin(end_angle)])
                    point = (start_point + end_point) / 2
                    edge_points.append(point.tolist())

                positions.extend(edge_points[:remaining_robots])

        # positions.append([0,0])
        # return np.array(positions)
        positions += self.center
        positions.append([self.center[0], self.center[1]])
        return np.array(positions)
    