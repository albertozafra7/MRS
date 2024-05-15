import numpy as np
import matplotlib.pyplot as plt
import argparse
import random

class Simulator:
    def __init__(self, height, width, bot_size, random_cols=False):
        self.height = height
        self.width = width
        self.bot_size = bot_size
        self.fig = None
        self.q = None
        self.n = None
        self.stop_flag = False
        self.random_cols = random_cols
        self.colors = []  # List to store colors for each robot

        plt.ion()
        self.fig = plt.gcf().number
        
        print("Number of robots = " + str(self.n))

    def random_color(self):
            # Generate a random color
            return (random.random(), random.random(), random.random())

    def update_robots(self, positions):
        self.n = len(positions) // 2
        self.q = np.array(positions).reshape(self.n, 2)
        
        if not self.colors and self.random_cols:
            self.colors = [self.random_color() for _ in range(self.n)]

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
        for i in range(self.n):
            if self.random_cols:
                plt.plot(self.q[i, 0], self.q[i, 1], 'o', color=self.colors[i],ms=self.bot_size)
            else:
                plt.plot(self.q[i, 0], self.q[i, 1], 'bo', ms=self.bot_size)

        # Update the current figure number
        self.fig = plt.gcf().number

        # Update the figure and do a micro-pause
        plt.draw()
        plt.pause(0.001)

def load_positions_from_file(filename):
    with open(filename, 'r') as file:
        lines = file.readlines()
        
    time_positions = []
    for line in lines:
        parts = list(map(float, line.split()))
        global_time = parts[0]
        positions = parts[1:]
        time_positions.append((global_time, positions))
    return time_positions

# Example usage:
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--file_path', dest='file_path', required=True, type=str, help='File path where the positions where written')
    parser.add_argument('--random_colors', dest='rand_col', type=bool, help='Define if you want to use random colors for the visualizator')
    args = parser.parse_args()
    handler = Simulator(height=250, width=250, bot_size=1, random_cols=args.rand_col)
    time_positions = load_positions_from_file(args.file_path)

    for global_time, positions in time_positions:
        print(f"Global Time: {global_time}")
        handler.update_robots(positions)
        handler.plot_evolution()
        if handler.stop_flag:
            break
