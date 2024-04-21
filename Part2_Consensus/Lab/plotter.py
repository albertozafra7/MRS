from __future__ import absolute_import, division, print_function, unicode_literals
import random
from PIL import Image
import numpy as np  # Make numpy available using np.
from matplotlib import pyplot as plt # Plotting of the graph
import imageio
import os

def remove_all_images(folder_path):
  for filename in os.listdir(folder_path):
    if os.path.isfile(os.path.join(folder_path, filename)):
      # Check for image extensions (modify as needed)
      if filename.endswith(".jpg") or filename.endswith(".png") or filename.endswith(".jpeg"):
        os.remove(os.path.join(folder_path, filename))
    print(f"Deleted images")

def plot_evolutionxy_video(robot_evolution_x, robot_evolution_y):
    plt.switch_backend('Agg')
    # Define plot limits (adjust as needed)
    x_min, x_max = -10, 10 #-2.5, 17.5 
    y_min, y_max = -10, 10
    (n, num_iter)=robot_evolution_x.shape
    # Function to generate a single plot frame
    def generate_plot(frame_num):
        plt.clf()  # Clear previous plot
        plt.xlim(x_min, x_max)
        plt.ylim(y_min, y_max)
        plt.xlabel("X")
        plt.ylabel("Y")
        plt.title(f"Robot Positions - Frame {frame_num}")

        # Plot robots based on their positions at the current frame
        for i in range(n):
            x = robot_evolution_x[i,frame_num]
            y = robot_evolution_y[i,frame_num]
            plt.plot(x, y, 'o')  # Marker 'o' for circle

    # Create the GIF animation
    frames = []
    for i in range(num_iter):  # Assuming all robots have same number of positions
        if i%50==0:
            print(i*100/num_iter,"%")
        plt.clf()  # Clear previous plot
        generate_plot(i)
        filename = f"imgs/frame_{i}.png"
        plt.savefig(filename)
        frames.append(imageio.imread(filename))

    imageio.mimsave('robot_movement.gif', frames, duration=20)  # Save the animation as GIF

    remove_all_images("./imgs")

    print("Robot movement GIF created!")

def plot_evolutionxy(robot_evolution_x,robot_evolution_y):
    plt.title("Evolution of the x,y coordinates of each node")
    plt.xlabel("x axis")
    plt.ylabel("y axis")

    (n, num_iter)=robot_evolution_x.shape
    for i in range(n):
        v_x=robot_evolution_x[i,:]
        v_y=robot_evolution_y[i,:]
        plt.plot(v_x,v_y, marker='.',)
        # Special markers for the first and last values
        plt.plot(v_x[0],v_y[0],marker='x')
        plt.plot(v_x[-1],v_y[-1],marker='o')
    plt.show()

def plot_evolutionx(states_x_iter):
    (n, num_iter)=states_x_iter.shape
    plt.figure
    plt.title("Evolution of the x-coordinates along the iterations")
    plt.xlabel("Iterations")
    plt.ylabel("x-coordinate")
    v_x=np.arange(0,num_iter)
    for i in range(n):
        v_y=states_x_iter[i,:]
        plt.plot(v_x,v_y, marker='.',)
        # Special markers for the first and last values
        plt.plot(v_x[0],v_y[0],marker='x')
        plt.plot(v_x[-1],v_y[-1],marker='o')
    plt.show()

def plot_evolutiony(states_y_iter):
    (n, num_iter)=states_y_iter.shape
    plt.figure
    plt.title("Evolution of the y-coordinates along the iterations")
    plt.xlabel("Iterations")
    plt.ylabel("y-coordinate")
    v_x=np.arange(0,num_iter)
    for i in range(n):
        v_y=states_y_iter[i,:]
        plt.plot(v_x,v_y, marker='.',)
        # Special markers for the first and last values
        plt.plot(v_x[0],v_y[0],marker='x')
        plt.plot(v_x[-1],v_y[-1],marker='o')
    plt.show()