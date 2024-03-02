## A solution to the PFSM exercise
## Version: YYYYMMDD
## Author: YOU
## License: CC-BY-SA

from time import time, localtime, strftime
from random import random, uniform
from shapely.geometry import Point
from point2d import Point2D 
from gadgETs import pipi
import numpy as np

from SmallWorl2D import Space, KPIdataset, Obstacle, Nest, Mobot, Soul, GoTo, Knowledge

time_limit = 60

## A couple of functions related to quadrants

def qdrnt(body): # in which quadrant am I?
    """ Quadrant identifier """
    if body.pos.x>0:
        if body.pos.y>0:
            return 1
        else:
            return 4
    else: 
        if body.pos.y>0:
            return 2
        else:
            return 3

def center(s, qdrnt): # a destination to go towards a quadrant
    if qdrnt==1:
        return Point(s.W/2,s.H/2)
    elif qdrnt==2:
        return Point(-s.W/2,s.H/2)
    elif qdrnt==3:
        return Point(-s.W/2,-s.H/2)
    elif qdrnt==4:
        return Point(s.W/2,-s.H/2)
    else: # or towards the center of the Space
        return Point(0,0)

def cmykdrn(qdrnt): # quadrant colors: CMYK
    cmyk=[(0,1,1),(1,0,1),(1,1,0),(0,0,0)]
    return cmyk[qdrnt-1]

class GoToZ(GoTo):
    """ A specialization of the GoTo Soul that zigzags randomly, perhaps towards a destination. """

    def __init__(self,body,T):
        super().__init__(body,T,nw='zigzag',obstalikes=Obstacle,bumper=body.r_encl*10,p=0.001) # Mobots only avoid Obstacles
        self.destination=None # Point or None

    def set_dest(self,destination):
        """ To go towards quadrant q (in Space s): GoToZ.set_dest(center(s,q)) """
        """ To go towards Body b: GoToZ.set_dest(b.pos) """
        self.destination=destination # Point or None

    def update(self):
        """ Relatively more or less often than random changes of direction, it points approx. towards the destination """
        if super().update():
            if not self.destination==None and random()<0.5*self.p: # 0.5? for "relatively more or less" often... ADJUST?    
                arrow=Point2D(self.destination.x-self.body.pos.x,self.destination.y-self.body.pos.y)
                self.body.teleport(th=pipi(uniform(0.9,1.1)*arrow.a)) # +/- 0.1? for "approx." ADJUST?
            return True
        else: return False

class MyState(Knowledge): # CHANGE FOR YOURS
    """ This is not what is actually required, 
        it is merely an integer state that informs of the integer quadrant were there is a Nest (1:4),
        0 when no Nest known
    """

    def __init__(self,body,qdrnt=[-1.0,-1.0,-1.0,-1.0]):
        super().__init__(body,state=qdrnt)

class BiB(Soul): # Bigger is Better, CHANGE FOR YOURS
    """ This is not what is actually required,
        it merely makes robots stay by their discovered Nest (the Demo in the course slides)
    """
    
    # Modifications for the Nest program
    nestSize = [0.0,0.0] # The size of the nest that we have info


    def __init__(self,body,T=0): # YOU CAN HAVE DIFFERENT T, etc, IF YOU WISH
        GoToZ(body,T) # requires a GoToZ soul in the same body
        self.GoToZ=body.souls[-1] # this way it knows how to call it
        self.size = -1
        self.last_id = -1
        MyState(body) # this Soul needs a Mind in its Body to work
        super().__init__(body,T)

    def update(self):
        if super().update():
            current=self.body.knows.tell_state()
            # if current==0:  # If we haven't detected any nest
            b=self.body
            i=b.index()
            s=b.space
            nest = s.incontact(i,Nest)
            if nest and nest.area > self.size:
                self.size = nest.area
                current=qdrnt(b)
                b.knows.set_state(current) # I've been in one!
            else:
                neighs=s.nearby(i,type(b),s.R)
                neigh = min(neighs[:].knows.tell_communications())
                
                # for n in neigh:
                #     current=n.knows.tell_state()
                #     if n.getSize() > self.size:
                #         self.size = n.soul[-1].getSize()
                #         b.knows.set_state(current) # If some neigh is aware of Nests, then so I am
                #         break
            if current>0: # changes color and set destination to quadrant
                b.fc=cmykdrn(current) # this is NOT the usual way to show a soul, but it looks nice here
                self.GoToZ.set_dest(center(s,current))

                
            
            return True
        else: return False
    
    # Modifications for the Nest program
    def updateSize(self,size):
        self.nestSize = size
    
    def getSize(self):
        return self.nestSize
    
    def getCommunications(self):
        return self.ctn_comm
    
    def incrComm(self):
        self.ctn_comm = self.ctn_comm + 1
    
    def getLastId(self):
        return self.last_id
    
    def updateLastId(self,id):
        self.last_id = id
## MAIN

def init():
    
    global time_limit

    ## Create Data Structures
    name='BiB_'+strftime("%Y%m%d%H%M", localtime())
    global s, NM
    s=Space(name,R=2,limits='hv',visual=True,showconn=True)
    KPIdataset(name,s,[1,1,0],[(0,'.y'),(1,'.k'),(2,'.g')])
        # 0 simulation time scale -- recommended "default" KPI
        # 1 Fraction remaining
        # 2 Fraction discovered Nest

    ## Populate the world
    NM=50; random()

    # two Nests
    i=0
    while i<2:
        new=Nest(s,'N'+str(i),pos=((-1)**i*uniform(0.2*s.W,0.8*s.W),uniform(0.2*s.H,0.8*s.H)),area=uniform(2,4)+4*i)
        if s.fits(new,s.room,safe=s.R):
            s.bodies.append(new)
            new.fc=cmykdrn(qdrnt(new))
            i += 1

    # several Obstacles
    i=0
    j=0
    while j<50:
        new=Obstacle(s,'O'+str(i),pos=(uniform(-s.W,s.W),uniform(-s.H,s.H)),area=uniform(0.05,0.5),fc=(0.6,0.6,0.6))
        if s.fits(new,s.room,safe=new.r_encl*10):
            s.bodies.append(new)
            i += 1
            j=0
        else: j += 1

    # and N Mobots
    i=0
    while i<NM:
        new=Mobot(s,'m'+str(i),pos=(uniform(-s.W,s.W),uniform(-s.H,s.H)),th=uniform(-np.pi,np.pi),fc=(0.8,0.8,1),v=1,v_max=s.vN/2,w_max=s.wN)
        if s.fits(new,s.room,safe=new.r_encl*5):
            s.bodies.append(new)
            BiB(new)
            i += 1

    # init distances matrix and connections graph
    s.dist=np.zeros((len(s.bodies),len(s.bodies))) # distances between centroids in a np.matrix
    s.update_dist()
    s.update_conn()

    if s.loginfo:
        s.logprint('N={:d}\n'.format(NM))
        for b in s.bodies: s.logprint(repr(b)+'\n')

init()
end=False
while not end: # THE loop
    s.step()

    ko=[] # collision management, Mobots collide with Obstacles (not among them)
    for b in s.bodies:
        i=b.index()
        if i>=0 and isinstance(b,Obstacle):
            ko+=s.incontact(i,Mobot)
    s.remobodies(ko,'collision')

    KPI=[s.time/(time()-s.t0),0,0] # KPI's computation
    for b in s.bodies:
        if b.on:
            if isinstance(b,Mobot):
                KPI[1] += 1
                if b.knows.tell_state()>0: KPI[2] += 1
    KPI[1]/=NM
    KPI[2]/=NM
    s.KPIds.update(KPI)
    end=s.has_been_closed() or s.KPIds.KPI[1]==0 or s.KPIds.KPI[2]==s.KPIds.KPI[1] or s.time>time_limit
s.close()
