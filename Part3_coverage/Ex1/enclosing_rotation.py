import threading

import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnnotationBbox

def imscatter(x, y, image, ax=None, zoom=1):
    if ax is None:
        ax = plt.gca()
    plt.xlim(-50,50)
    plt.ylim(-50,50)
    im = OffsetImage(image, zoom=zoom)
    x, y = np.atleast_1d(x, y)
    artists = []
    for x0, y0 in zip(x, y):
        ab = AnnotationBbox(im, (x0, y0), xycoords='data', frameon=False)
        artists.append(ax.add_artist(ab))
    return artists

class EnclosingRotation:
    def __init__(self, qi_x, qi_y, ci_x, ci_y, plot_results=False):
        self.lock = threading.Lock()

        # Robots qi positions, qn is assumed to be the target
        self.qi = np.array([qi_x,qi_y]).T

        self.num_pos = self.qi.shape[0]

        # Useless things for fancyness
        self.dog = plt.imread('./dog.png')
        self.sheep = plt.imread('./sheep.png')

        # Desired robot location
        self.ci = np.array([ci_x,ci_y]).T


        # Simulation params
        self.iters = 300
        self.K_c = 10
        self.K_g = 2
        self.delta_t = 0.01
        self.random_x = 1
        self.random_y = 1

        # Gather information to plot results
        self.plot_results = plot_results
        self.record_x = np.zeros((self.num_pos, self.iters))
        self.record_y = np.zeros((self.num_pos, self.iters))

        print("Starting de algorithm:\nStarting positions: \n{}\nDesired positions: \n{}\n".format(self.qi.T, self.ci.T))
        plt.ion()
        self.run()

    def run(self):

        for iteration in range(self.iters):
            # Run the algorithm
            Q = self.compute_inter_positions(self.qi)
            C = self.compute_inter_positions(self.ci)
            A = C.T @ Q
            U, S, V_t = np.linalg.svd(A)
            d = np.sign(np.linalg.det(V_t.T @ U.T))
            D = np.array([[1,0],[0,d]])
            R = V_t.T @ D @ U.T
            q_Ni = -Q[self.num_pos-1::self.num_pos]
            c_Ni = -C[self.num_pos-1::self.num_pos]
            #print("Shapes:\nQ: {}\nC: {}\nA: {}\nR: {}\nq_Ni: {}\nc_Ni: {}".format(Q.shape, C.shape, A.shape, R.shape, q_Ni.shape, c_Ni.shape))

            # Compute control
            q_dot = np.zeros((self.num_pos, 2))
            for agent in range(self.num_pos-1):
                q_dot[agent,:] = self.K_c * (q_Ni[agent,:] - R @ c_Ni[agent,:]) - self.K_g * (self.qi[agent+1,:] - self.qi[agent,:])            
            q_dot[self.num_pos-2,:] = self.K_c * (q_Ni[self.num_pos-2,:] - R @ c_Ni[self.num_pos-2,:]) - self.K_g * (self.qi[0,:] - self.qi[self.num_pos-2,:])            
            
            # Random movement of the prey
            if np.random.uniform(0,1) > 0.99:
                self.random_x = np.random.uniform(-5,5)
                self.random_y = np.random.uniform(-5,5)
            #q_dot[self.num_pos-1, :] += [self.random_x, self.random_y]

            # Apply control
            self.qi += q_dot * self.delta_t
            
            self.record_x[:,iteration] = self.qi[:,0]
            self.record_y[:,iteration] = self.qi[:,1]

            self.plot_robots()

        if self.plot_results:
            
            x_axis = np.arange(self.iters)

            plt.figure()
            plt.ioff()
            for iter_record in range(self.num_pos):
                plt.plot(x_axis, self.record_x[iter_record,:])
            plt.legend(['Hunter 1', 'Hunter 2', 'Hunter 3', 'Hunter 4','Hunter 5', 'Hunter 6', 'Hunter 7', 'Prey'])

            plt.draw()

            plt.figure()
            plt.ioff()
            for iter_record in range(self.num_pos):
                plt.plot(x_axis, self.record_y[iter_record,:])
            plt.legend(['Hunter 1', 'Hunter 2', 'Hunter 3', 'Hunter 4','Hunter 5', 'Hunter 6', 'Hunter 7', 'Prey'])

            plt.draw()
            print("Close windows to finish...")
            
            plt.show(block=True)

       
    def compute_inter_positions(self, positions):
    
        rel_pos = np.zeros((self.num_pos*self.num_pos, 2))
        # Compute inter-robot relative positions
        for i in range(self.num_pos):
            for j in range(self.num_pos):
                #print("Position {} with {}".format(i,j))
                rel_pos[i + self.num_pos*j, 0] = positions[j,0] - positions[i,0]
                rel_pos[i + self.num_pos*j, 1] = positions[j,1] - positions[i,1]
        return rel_pos

    def plot_robots(self):
        plt.clf()
        plt.xlim(-50,50)
        plt.ylim(-50,50)
        for i in range(self.num_pos-1):
                #plt.plot(self.qi[i,0],self.qi[i,1],'bo')
                imscatter(self.qi[i,0],self.qi[i,1],self.dog,zoom=0.05)

        #plt.plot(self.qi[self.num_pos-1,0],self.qi[self.num_pos-1,1],'ro')
        imscatter(self.qi[self.num_pos-1,0],self.qi[self.num_pos-1,1],self.sheep,zoom=0.025)

        plt.draw()
        plt.pause(0.01)

if __name__ == "__main__":

    qx = [-6.1,8.7,-4.7, 3.9, 5.1, 3.3, -5, 1]
    qy = [-4,-4.4,4.2, 4.5, 3.2, -6, -3.6, 1]
    cx = [2,-2,0,0,0]
    cy = [0,0,2,-2,0]

    cx = []
    cy = []
    radius = 5
    angle = 360/(len(qx)-1)
    angles = np.arange(0,360,angle) * 2 * np.pi / 360
    print(angles)
    for a in angles-1:
        cx.append(np.cos(a) * radius)
        cy.append(np.sin(a) * radius)

    cx.append(0)
    cy.append(0)
    #cx = [0,2,-2,0,0]
    #cy = [2,-2,-2,-2,0]
    enc = EnclosingRotation(qx,qy,cx,cy, True)