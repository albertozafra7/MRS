from __future__ import absolute_import, division, print_function, unicode_literals
import random
import numpy as np  # Make numpy available using np.
from matplotlib import pyplot as plt # Plotting of the graph
from matplotlib import animation


def plot_evolutionxy_video(robot_evolution_x, robot_evolution_y):
    fig, ax = plt.subplots()  # Create a figure and an axes object

    # Set plot labels and title
    ax.set_title("Evolution of the x,y coordinates of each node")
    ax.set_xlabel("x axis")
    ax.set_ylabel("y axis")

    (n, num_iter) = robot_evolution_x.shape  # Get the number of nodes and iterations

    # Initialize empty line objects for animation
    lines = [ax.plot([], [], marker='.')[0] for i in range(n)]  # Create lines for each node

    # Function to update the animation frame
    def animate(i):

        for j in range(n):
            lines[j].set_data(robot_evolution_x[j, :i], robot_evolution_y[j, :i])  # Update line data

        # Special markers for the first and last values (outside the loop for efficiency)
        ax.plot(robot_evolution_x[0, :i], robot_evolution_y[0, :i], marker='x')
        ax.plot(robot_evolution_x[-1, :i], robot_evolution_y[-1, :i], marker='o')

        return lines

    # Create animation object
    anim = animation.FuncAnimation(fig, animate, frames=num_iter, interval=10)  # Adjust interval for animation speed
    writergif = animation.PillowWriter(fps=30)
    # Save animation as video (replace 'animation.mp4' with your desired filename)
    anim.save('animation', writer=writergif)  # You may need to install ffmpeg for this to work

    plt.close(fig)  # Close the plot

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