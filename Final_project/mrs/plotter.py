#!/usr/bin/python
# -*- coding: UTF-8 -*-
import numpy as np
import utils as ut
import matplotlib
import matplotlib.pyplot as plt
import random
import argparse

class Plotter:

    def __init__(self, conn_file, logs_file, height=60, width=60, bot_size=5, group_cols=True, random_cols=False):


        # ++++++++++++++ Custom Properties ++++++++++++++

        # Filepaths
        self.conn_file = self.readFile(conn_file)   # Connections file path (string) -> Contains the connection graph structure as (uid,idL,idG,uid1,uid2,...)
        self.logs = logs_file

        # General control properties
        self.stop_flag = False                      # Stop flag to end the simulation
        self.nG = ut.numGroups(self.conn_file)      # Number of groups in the simulation (int)
        self.nL = []                                # Number of robots in each group (array(int))
        
        # We store the number of robots of each group
        for i in range(self.nG):
            self.nL.append(ut.numRobsInGroup(i,self.conn_file))

        self.nR = sum(self.nL)                      # Total number of robots in the simulation, without counting the target (int)
        

        # General plot properties
        self.plt_height = height                    # Height of the plot window (int)
        self.plt_width = width                      # Width of the plot window (int)
        self.plt_bot_size = bot_size                # Bot size within the simulation (int)
        self.plt_group_cols = group_cols            # Stablish if we want to group the local robots with a representative color per group (bool)
        self.plt_random_cols = random_cols          # Stablish if we want to have random colors for each robot (bool)
        self.plt_colors = []                        # Colors to paint the robots within the plot (array)
        
        plt.ion()
        self.fig = plt.gcf().number



        # ++++++++++++++ Methods Initialization ++++++++++++++
        self.read_robot_positions()
        self.colorize_robots()
        self.plot_evolution()
      
      
            
    def read_robot_positions(self):
        data = self.readFile(self.logs)
        self.q = []
        self.qT = []
        self.n_iters = 0

        for line in data:
            line = line.strip()  # Remove any leading/trailing whitespace
            if not line:
                continue  # Skip empty lines

            self.n_iters +=1
            try:
                robots, target = line.split('|')
                robot_coords = [tuple(map(float, coord.split(','))) for coord in robots.split(';') if coord]
                target_coord = tuple(map(float, target.split(',')))

                if robot_coords:
                    self.q.append(robot_coords)
                if target_coord:
                    self.qT.append(target_coord)
            except ValueError as e:
                print(f"Error processing line: '{line}'. Error: {e}")
                continue

        self.q = np.array(self.q)
        self.qT = np.array(self.qT)
    
 
    
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
                self.plt_colors[start_id:start_id+self.nL[i]] = self.group_colors(self.nL[i])
                start_id += self.nL[i]

            # The target color
            self.plt_colors[-1] = self.random_color()

        elif not self.plt_colors and self.plt_random_cols:
            self.plt_colors = [self.random_color() for _ in range(self.nR+1)]

    def plot_evolution(self):
        for iters in range(self.n_iters):
            # Close the plot window to stop the simulation
            if not plt.fignum_exists(self.fig):
                print("S:Plot window closed.")
                self.stop_flag = True
                return

            print("Iteration " + str(iters))
            plt.clf()  # Clear existing figure
            # Set the limits of the figure
            plt.xlim(-self.plt_width, self.plt_width)
            plt.ylim(-self.plt_height, self.plt_height)

            # Plot the robots that will follow the formation as a blue dot
            for i in range(self.nR):
                # print(self.q[iters, i,0], self.q[iters, i,1])
                if self.plt_group_cols or self.plt_random_cols:
                    plt.plot(self.q[iters, i, 0], self.q[iters, i, 1], 'o', color=self.plt_colors[i],ms=self.plt_bot_size)
                else:
                    plt.plot(self.q[iters, i, 0], self.q[iters, i, 1], 'bo', ms=self.plt_bot_size)

            # if self.plt_group_cols or self.plt_random_cols:
            #     plt.plot(self.qT[iters, 0], self.qT[iters, 1], 'o', color=self.plt_colors[-1],ms=self.plt_bot_size)
            # else:
                plt.plot(self.qT[iters, 0], self.qT[iters, 1], 'ro', ms=self.plt_bot_size)
            # Update the current figure number
            self.fig = plt.gcf().number

            # Update the figure and do a micro-pause
            plt.draw()
            plt.pause(0.01)


if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--conn_file', dest='conn_file', type=str, help='Connection file path')
    parser.add_argument('--logs_file', dest='logs_file', type=str, help='Logs file path')
    parser.add_argument('--w_height', dest='height', type=int, help='Plot window height')
    parser.add_argument('--w_width', dest='width', type=int, help='Plot window width')
    parser.add_argument('--bot_size', dest='bot_size', type=int, help='Bot size in the plot')
    
    args = parser.parse_args()
    
    plotter = Plotter(conn_file=args.conn_file, logs_file=args.logs_file, height=args.height, width=args.width, bot_size=args.bot_size)