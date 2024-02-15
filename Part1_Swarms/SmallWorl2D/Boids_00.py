## A solution to the Boids exercise
## Version: YYYYMMDD
## Author: YOU
## License: CC-BY-SA

from time import time, localtime, strftime
from random import uniform
import numpy as np
from point2d import Point2D 
# YOU MIGHT FIND USEFUL FUNCTIONS IN shapely, Point2D, AND gadgETs
from SmallWorl2D import Space, KPIdataset, Obstacle, MoBody, Mobot, Soul

class Boid(Soul):

    # YOUR AUXILIARY FUNCTIONS

    def __init__(self,body,T,dd):  # ADD YOUR ARGUMENTS
        self.dd=dd
        # YOUR BOID INIT CODE
        super().__init__(body,T)

    def update(self):
        if super().update():
            b=self.body
            i=b.index()
            s=b.space
            # YOUR BOID UPDATE CODE

def init():

    ## Create Data Structures
    name='Boids_'+strftime("%Y%m%d%H%M", localtime())
    global s, N
    dd=1 # or whatever
    s=Space(name,...)
    KPIdataset(name,s,...)
        # 0 simulation time scale -- recommended "default" KPI
        # 1 Fraction remaining
        # 2 Fraction in largest group
        # ...

    ## Populate the world

    # N Mobots
    N=25
    i=0
    while i<N:
        new=Mobot(s,'m'+str(i),...)
        if s.fits(new,...):
            s.bodies.append(new)
            # YOUR BOID PARAMETRIZATION, DIFFERENT KINDS?
            Boid(new,...)
            i += 1

    # and several Obstacles, or Killers, or whatever

    # init distances matrix and connections graph
    s.dist=np.zeros((len(s.bodies),len(s.bodies))) # distances between centroids in a np.matrix
    s.update_dist()
    s.update_conn()

    # WHATEVER ELSE YOU WANT TO DO INITIALLY, E.G., REPORT ON LOG

init()
end=False
while not end: # THE loop 
    s.step()

    # COLLISION MANAGEMENT
    ko=[]
    # YOUR COLLISION DETECTION CODE 
    s.remobodies(ko,'collision')

    # KPIs
    KPI=[s.time/(time()-s.t0),...]
    # YOUR KPI COMPUTATIONS
    s.KPIds.update(KPI)

    end=s.has_been_closed() or s.KPIds.KPI[1]==0 or s.time>60 # or whatever
s.close()