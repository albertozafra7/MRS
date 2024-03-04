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
import random

from SmallWorl2D import Space, KPIdataset, Obstacle, Nest, Mobot, Soul, GoTo, Knowledge

time_limit = 60

## A couple of functions related to quadrants

def sigmoid(x):
    # return 1 / (1 + np.exp((2000-x)*0.005))
    return 1 / (1 + np.exp((1000-x)*0.01))


def median_point(point1, point2):
    
    """
    Compute the median point between two points.
    
    Args:
    - point1: Tuple or list containing the coordinates of the first point.
    - point2: Tuple or list containing the coordinates of the second point.
    
    Returns:
    - Tuple containing the coordinates of the median point.
    """
    pointAux = Point((point1.x + point2.x) / 2,(point1.y + point2.y) / 2)
    
    return pointAux  # Return the median point as a tuple

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
        
def quadrant(i): # in which quadrant am I?
    """ Quadrant identifier """
    
    if i == 0:      # Lower left quadrant
        return 3    
    elif i == 1:    # The quadrant with the blue nest (Upper right)
        return 1
    elif i == 2:    # The quadrant with the pink nest (Upper left)
        return 2
    else:
        return 4    # Lower right quadrant

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

    def stop(self):
        """ stop """
        self.nw = 'stop'
        self.destination = None
        self.where=None

    def go_to_nest(self,destination):
        """ To go towards the biggest nest in straight line """
        self.destination=destination
        self.where=destination
        self.nw = 'keepgoing'
        self.obstalikes=Obstacle
        self.bumper=1.25
        # self.p=0.01

    def update(self):
        """ Relatively more or less often than random changes of direction, it points approx. towards the destination """
        if super().update():
            if not self.destination==None and random.random()<0.5*self.p: # 0.5? for "relatively more or less" often... ADJUST?    
                arrow=Point2D(self.destination.x-self.body.pos.x,self.destination.y-self.body.pos.y)
                self.body.teleport(th=pipi(uniform(0.9,1.1)*arrow.a)) # +/- 0.1? for "approx." ADJUST?
            return True
        else: return False

class MyState(Knowledge): # CHANGE FOR YOURS
    """ This is not what is actually required, 
        it is merely an integer state that informs of the integer quadrant were there is a Nest (1:4),
        0 when no Nest known
    """

    def __init__(self,body,qdrnt=np.zeros([4])):
        super().__init__(body,state=qdrnt)

class BiB(Soul): # Bigger is Better, CHANGE FOR YOURS
    """ This is not what is actually required,
        it merely makes robots stay by their discovered Nest (the Demo in the course slides)
    """
    
    # Modifications for the Nest program


    def __init__(self,body,T=0): # YOU CAN HAVE DIFFERENT T, etc, IF YOU WISH
        GoToZ(body,T) # requires a GoToZ soul in the same body
        self.GoToZ=body.souls[-1] # this way it knows how to call it
        self.t_ini = -1
        self.p_ini = body.pos
        self.in_nest = True
        self.update_rate = 10
        MyState(body) # this Soul needs a Mind in its Body to work
        super().__init__(body,T)

    def update(self):
        if super().update():
            current=self.body.knows.tell_state()
            # if current==0:  # If we haven't detected any nest
            b=self.body
            k=b.knows
            i=b.index()
            s=b.space
            my_comm = k.tell_communications()
            nest = s.incontact(i,Nest)
                
            if nest and not self.in_nest and k.tell_state_action() != "nested" and k.tell_state_action() != "nesting" :
                self.t_ini = s.time
                self.p_ini = b.pos
            elif not nest and self.in_nest and self.t_ini != -1:
                t_total = s.time - self.t_ini

                if t_total > np.max(current[qdrnt(b)]):
                    k.set_center(median_point(self.p_ini,b.pos)) # We get the center of the nest
                
                current[qdrnt(b)] = np.maximum(current[qdrnt(b)],t_total)
                
                b.knows.set_state(current) # I've been in one!
                comm = np.zeros([4])
                comm[qdrnt(b)] = 1
                k.sum_communications(comm)
                
            else: # Communication
                neigh=s.nearby(i,type(b),s.R)   # We get the neighbours
                # vals = np.zeros([4])        # Size aux
                comms = np.zeros([4])
                for n in neigh:                 # We do the mean of the info of all neigh
                    # vals += n.knows.tell_state()
                    comms = np.where(n.knows.tell_state() != 0, comms+1, comms)
                    
                    if(np.max(current) < np.max(n.knows.tell_state())):  # If our nest isn't the biggest
                        k.set_center(n.knows.tell_center())                     # We update the center
                    
                    current = np.maximum(current,n.knows.tell_state())

                    

                # my_comm = np.log(my_comm+1)
                # opinions = my_comm + comms
                # opinions = np.where(opinions == 0, 1, opinions)

                k.set_state(current)
                k.sum_communications(comms)

            if k.tell_state_action() != "nested" and k.tell_state_action() != "nesting" and current.any(): # changes color and set destination to quadrant
                b.fc=cmykdrn(np.argmax(current)) # this is NOT the usual way to show a soul, but it looks nice here


            # state machine
            if(k.tell_state_action() == "nesting" and nest and qdrnt(b)==np.argmax(current)): # If in contact with the biggest nest -> stop
                k.set_state_action("nested")
                self.t_ini = -1
                self.GoToZ.stop()
                b.fc=(1,1,0.3)      # Yellow

            nests_k = np.sum(np.where(my_comm != 0, 1, 0))

            # Roussian Roulete movement
            if s.steps%self.update_rate == 0: # Every X iterations we compute the probability to go to the nest or explore
                if nests_k>1 and k.tell_state_action() != "nested" and current.any() and (random.random() < sigmoid(max(k.tell_communications())) or s.time > 20): #  Goes to the biggest nest
                    #self.GoToZ.set_dest(center(s,np.argmax(current)))
                    
                    k.set_state_action("nesting")
                    self.GoToZ.go_to_nest(k.tell_center())

                    if np.argmax(current) == 2:
                        b.fc=(1,0,0.3)      # Red
                    else:
                        b.fc=(0.1,1,0.1)    # Green


                elif (k.tell_state_action() != "nested" and (random.random() < 0.02)) or (k.tell_state_action() == "exploring" and b.pos.distance(center(s,qdrnt(b))) < 0.5):    # Changes direction each ~30 steps
                    k.set_state_action("exploring")
                    self.GoToZ.set_dest(center(s,random.randint(1, 4)))
                    b.fc=cmykdrn(np.argmax(current))
            
            # If nested in the smallest nest
            if k.tell_state_action() == "nested" and qdrnt(b)!=quadrant(np.argmax(current)): #or random.random() < 0.01):
                    k.set_state_action("nesting")
                    self.GoToZ.go_to_nest(k.tell_center())

                    if np.argmax(current) == 2:
                        b.fc=(1,0,0.3)      # Red
                    else:
                        b.fc=(0.1,1,0.1)    # Green

            self.in_nest = nest
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
    NM=50; random.random()

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
                if b.knows.tell_state().all(): KPI[2] += 1
    KPI[1]/=NM
    KPI[2]/=NM
    s.KPIds.update(KPI)
    end=s.has_been_closed() or s.KPIds.KPI[1]==0 or s.KPIds.KPI[2]==s.KPIds.KPI[1] or s.time>time_limit
s.close()

