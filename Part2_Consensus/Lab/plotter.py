from __future__ import absolute_import, division, print_function, unicode_literals
import random
import numpy as np  # Make numpy available using np.
from matplotlib import pyplot as plt # Plotting of the graph

def plot_evolutionxy(states_x_iter,states_y_iter):
    plt.title("Evolution of the x,y coordinates of each node")
    plt.xlabel("x axis")
    plt.ylabel("y axis")

    (n, num_iter)=states_x_iter.shape
    for i in range(n):
        v_x=states_x_iter[i,:]
        v_y=states_y_iter[i,:]
        plt.plot(v_x,v_y, marker='.',)
        # Special markers for the first and last values
        plt.plot(v_x[0],v_y[0],marker='x')
        plt.plot(v_x[-1],v_y[-1],marker='o')
        # alternative if we want to use arrows instead of lines.
        #x_ini=v_x[k]
        #y_ini=v_y[k]
        #dx= v_x[k+1] -x_ini
        #dy= v_y[k+1] -y_ini
        #plt.arrow(x_ini, y_ini, dx, dy, head_length=0.1,length_includes_head=True, head_width=0.05)
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