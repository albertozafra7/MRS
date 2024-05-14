import threading
import argparse
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from numpy.core.shape_base import block
from print_colors import bcolors

class point2d:
    def __init__(self,poses):
        
        self.poses = np.array([poses])
    
    
        
def generate_robot_positions(shape, num_robots):
    if shape not in ["line", "circle", "grid", "square", "star", "hexagon"]:
        raise ValueError("Invalid shape. Choose from 'line', 'circle', 'grid', 'square', 'star' or 'hexagon'.")
    positions = []
    num_robots -= 1

    if shape == "line":
        # Place robots in a straight line along the x-axis
        mid_point = (0 + (num_robots - 1)) / 2
        for i in range(num_robots):
            positions.append([i - mid_point, 0])
        

    elif shape == "circle":
        # Place robots in a circle with radius 1
        for i in range(num_robots):
            angle = 2 * np.pi * i / num_robots
            x = np.cos(angle)
            y = np.sin(angle)
            positions.append([x, y])

    elif shape == "grid":
        # Place robots in a grid with roughly equal rows and columns
        side_length = np.ceil(np.sqrt(num_robots))
        offset = (side_length-1)/2
        for i in range(num_robots):
            row = i // side_length
            col = i % side_length
            positions.append([col-offset, row-offset])
            
    elif shape == "square":
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

    elif shape == "star":
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
            
    elif shape == "hexagon":
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

    positions.append([0,0])
    return np.array(positions)

class Formation:
    def __init__(self, q, c, rotate=False):
        
        self.lock = threading.Lock()

        self.q = q  # initial robot positions

        self.n = q.shape[0]

        self.c = c  # goal formation
        
        self.rotation_control = rotate  # Rotation control [True,False]
        
        self.stop_flag = False  # to stop the execution

        self.num_iters = 200
        self.Kc = 15    # Control gain
        self.Kg = 10    # Rotation Control gain
        self.dt = 0.01
        self.enclosed_vel = np.random.rand(2,1)-0.5
        self.desired_vel = 15
        self.vel_update_rate = 50

        # Printing the robot positions and its desired positions
        print(bcolors.HEADER + "[Starting robot positions] -> [Desired robot positions]" + bcolors.CEND)
        self.print_robot_positions()
        
        
        # Making the plot interactive
        plt.ion()
        
        # Current window number tracker
        self.fig = plt.gcf().number
        
        # Start the simulation
        self.run()
                

    def run(self):
        
        for iteration in range(self.num_iters):
            
            # If the simulation is stopped -> break
            if self.stop_flag:
                break
            

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
            q_dot = np.zeros((self.n, 2))
            for agent in range(self.n):
                # If orbiting control is not selected each of the robot is going to converge to its desired shape position
                if not self.rotation_control:
                    q_dot[agent,:] = self.Kc * (q_Ni[agent,:] - R @ c_Ni[agent,:])
                    
                # If orbiting control is selected each of the robot is going to follow the next robot based on a Control gain (Kg)
                else: 
                    if agent < self.n-1:
                        q_dot[agent,:] = self.Kc * (q_Ni[agent,:] - R @ c_Ni[agent,:]) - self.Kg * (q_Ni[agent+1,:] - q_Ni[agent,:]) 
                    else:
                        q_dot[self.n-2,:] = self.Kc * (q_Ni[self.n-2,:] - R @ c_Ni[self.n-2,:]) - self.Kg * (q_Ni[0,:] - q_Ni[self.n-2,:])
                    
            
            # Enclosed robot movement
            if iteration % self.vel_update_rate == 0:
                self.enclosed_vel = np.random.rand(1,2)-0.5
            q_dot[self.n-1, :] += self.desired_vel*self.enclosed_vel[0]

            # Apply control
            self.q += q_dot * self.dt
            

            self.plot_evolution()
        

    def compute_inter_robot_positions(self, positions):
    
        rel_pos = np.zeros((self.n*self.n, 2))
        # Compute inter-robot relative positions
        for i in range(self.n):
            for j in range(self.n):
                #print("Position {} with {}".format(i,j))
                rel_pos[i + self.n*j, 0] = positions[j,0] - positions[i,0]
                rel_pos[i + self.n*j, 1] = positions[j,1] - positions[i,1]
        return rel_pos


    def print_robot_positions(self):
        # Printing the current position of the robot at the left and the desired position of the robot at the right
        # Such as: robot X [current pos] --> [desired pos]
        for i in range(self.n - 1):
            print(bcolors.CBLUEBG + f"blue robot {i+1} [{self.q[i, 0]:.2f},{self.q[i, 1]:.2f}] --> [{self.c[i, 0]:.2f},{self.c[i, 1]:.2f}]" + bcolors.CEND)
        print(bcolors.CREDBG + f"red robot [{self.q[self.n - 1, 0]:.2f},{self.q[self.n - 1, 1]:.2f}] --> [{self.c[self.n - 1, 0]:.2f},{self.c[self.n - 1, 1]:.2f}]" + bcolors.CEND)


    def plot_evolution(self):
        
        # Close the plot window to stop the simulation
        if not plt.fignum_exists(self.fig):
            print("Plot window closed.")
            self.stop_flag = True
        
            
        plt.clf() # Close existing figure
        # Set the limits of the figure
        plt.xlim(-10,10)
        plt.ylim(-10,10)
        
        # Plot the robots that will follow the formation as a blue dot
        for i in range(self.n-1):
                plt.plot(self.q[i,0],self.q[i,1],'bo')

        # Plot the enclosed robot as a red dot
        plt.plot(self.q[self.n-1,0],self.q[self.n-1,1],'ro')
        
        # Update the current figure number
        self.fig = plt.gcf().number

        # Update the figure and do a micro-pause
        plt.draw()
        plt.pause(0.001)




if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('--n_robots', dest='n', type=int, help='Number of Robots')
    parser.add_argument('--shape', dest='shape', type=str, help='You can select between "line", "circle", "grid", "square", "star" or "hexagon"')
    parser.add_argument('--rotate', dest='rot', type=bool, help='Perform rotation [True,False]')
    
    args = parser.parse_args()

    q = np.random.rand(args.n,2) * 10
    q[-1] = np.array([0,0])
    if args.rot:
        print(bcolors.HEADER + "Executing the orbiting enclosing algorithm" + bcolors.CEND)
    else:
        print(bcolors.HEADER + "Executing the standard enclosing algorithm" + bcolors.CEND)

    c = generate_robot_positions(args.shape,args.n)

    enc = Formation(q,c,args.rot)