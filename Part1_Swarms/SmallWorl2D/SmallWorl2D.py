## SmallWorl2D
## Version: 20230923
## Author: Enrique Teruel (ET) eteruel@unizar.es
## License: CC-BY-SA

## A typical small_worl2d is a rectangular Space shown in a matplotlib window, with or without limits
## populated by a number of Body's like Obstacle's, Nest's or Food's,
## MoBody's (a Moving subclass of Body's) like MObstacle's, and
## AniBody's (an Animated subclass of MoBody's), which are the interesting Mobot's, Killer's, Shepherd's, etc
## AniBody's are animated by Soul's (there can be several in one Body), which are the (most) interesting control codes
## AniBodys might have some Knowledge

## Front matters
# Not mine imports
from time import time, localtime, strftime
from math import pi, sin, cos, sqrt, inf
from random import seed, random, uniform, choice
from shapely.geometry import Point, Polygon, LineString                                                                 
from shapely.affinity import translate, rotate, scale
from shapely import intersects, intersection
from shapely.ops import nearest_points
from point2d import Point2D 
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.animation import FFMpegWriter # requires having ffmpeg installed, from https://ffmpeg.org/
# Mine imports
from gadgETs import pipi, voronoi, WUGraph

class Space: # a rectangle populated by Body's

    ## Basic functions
    
    def __init__(self,name,dt=0.01,DRS=4,R=1,occl=False,ConnCtrl=0,limits='',randomseed=None,visual=False,shoul=False,showtrail=False,showconn=False,datxt=False,loginfo=False,SS=15,W=16,H=9):
        """ Also creates and inits files and graphics """

        ## Global parameters
        self.name=name
        # Visual detail
        self.visual=visual # to see the world (and selected KPI's) on the run, and record a movie
        self.shoul=shoul # to show Soul's or not
        self.showtrail=showtrail # to show the trails (of Mobots only) or not
        self.showconn=showconn # to show the graph of connections or not
        # Info detail
        self.datxt=datxt # dump the (KPI) data a csv file, to make plots afterwards
        self.loginfo=loginfo # dump info to a log file
        # Canvas sizing; default aspect ratio W:H; coords (-W:W,-H:H); 
        self.SS=SS # Screen Size SS in ches
        self.W=W
        self.H=H
        self.room=[(-W,-H),(W,-H),(W,H),(-W,H)]
        self.limits=limits # str possibly containing v or/and h
            # Limits are implemented as Obstacles, with a near-infinity enclosing radio
            # Without limits, moving bodies that cross the top appear at the bottom, etc
            # In such case, avoid placing obstacles, etc near the no-limit            
        # Time parameters
        self.dt=dt # time step, in seconds
        self.DRS=DRS # "Display Refresh after Steps", the number of time steps per frame. For dt=0.01s and 25 fps (0.04 s/frame), DRS=4; fps=1/(DRS*dt)
        self.fps=int(1/(DRS*dt)) # frames per second
        # Max vel's should be a fraction of the following vN and wN (intended for relatively small displacements per redraw)
        self.vN=4 # traverse 4 units distance in 1 sec (32 canvas-width in 8 secs)
        self.wN=4*pi # 2 full revolutions in 1 sec (120 rpm, quite fast)
        # Communication radius in the space (omnidirectional and with same R for every type of (ani)Body), occlusion or not
        self.R=R 
        self.occl=occl
        # Connection/Proximity Graph (intended for Connectivity Control):
        # 0 - without, show the full connection graph if showconn
        # 1 - nearest, very "cheap", although it doesn't guarantee keeping connectedness
        # 2 - MST, most permissive that keeps connectedness, but too "expensive" (only centralized-ideal computation is implemented, as a baseline, the distributed computation could be time-limited...)
        # 3 - IMRG, most permissive that can be computed locally (2-hops); it's more restricting than MST - not bad in our context?
        # 4 - DT, keep the Voronoi neighbors, perhaps too restricting? Implemented to compare, and because Voronoi...
        self.ConnCtrl=ConnCtrl

        ## Init of random, timing and objects
        if not randomseed==None: seed(randomseed) # Random seed for reproducibility
        self.t0=time() # initial real time (to inform simulation speed)
        self.time=-self.dt # simulation time (s)
        self.lastime=self.time-self.DRS*self.dt # time of last draw
        self.SR=0 # Number of Steps to Redraw
        self.bodies=[] # list of Body's in this Space
        self.dist=np.zeros((0,0)) # distances between self.bodies centroids in a symmetric np.matrix
        self.conn={} # a dict where conn[i] is the set of j's such that (i,j) is edge; i, j are AniBody's of the same type in self.bodies
            # although conceptually undirected, it is represented as a digraph for convenience
        if self.ConnCtrl>0: self.prox={} # the proximity subgraph of conn, a dict where prox[i] is the set of j's such that (i,j) in prox
            # although conceptually undirected, it is represented as a digraph for convenience
        self.conngraph=[] # a list of matplotlib lines for graphical representation of edges (i,j)
            # each edge ends being included twice for laziness (because the conn is represented as a digraph)
        self.KPIds=None # KPI dataset in this Space (just one set, not worthwhile to make a list)

        ## Creation and initialization of figure and files
        if self.loginfo:
            global log
            log=open(self.name+'.log','w')
            log.write('Simulation step dt={:.3f} s, DRS={:d} display refresh steps, {:d} fps\n'.format(self.dt,self.DRS,self.fps))
            log.write('vN={:.2f}, wN={:.2f}\n'.format(self.vN,self.wN))
        if self.visual:
            self.fig=plt.figure(figsize=(self.SS*self.W/sqrt(self.W**2+self.H**2), self.SS*self.H/sqrt(self.W**2+self.H**2)),frameon=False) # W:H proportion, SS inches diag (resizeable)
            self.ax=self.fig.add_axes([0,0,1,1]) # full window
            self.ax.set_facecolor('w') # white background
            self.ax.set_xlim(-self.W, self.W) # note that x coords, of everything visible in the space, range from -W to W
            self.ax.set_ylim(-self.H, self.H) # and y coords from -H to H
            self.movie_writer = FFMpegWriter(fps=self.fps)
            self.movie_writer.setup(self.fig, self.name+'.mp4', self.fig.dpi)

        ## Creation and drawing of the borders:
        if 'v' in self.limits:
            self.bodies.append(Obstacle(self,'top',pos=-1,area=-1,fc=(0,0,0),vertices=[(-self.W,self.H-0.1),(self.W,self.H-0.1),(self.W,1e12),(-self.W,1e12)]))
            self.bodies.append(Obstacle(self,'bottom',pos=-1,area=-1,fc=(0,0,0),vertices=[(-self.W,-self.H+0.1),(self.W,-self.H+0.1),(self.W,-1e12),(-self.W,-1e12)]))
        if 'h' in self.limits:
            self.bodies.append(Obstacle(self,'left',pos=-1,area=-1,fc=(0,0,0),vertices=[(-self.W+0.1,-self.H),(-self.W+0.1,self.H),(-1e12,self.H),(-1e12,-self.H)]))
            self.bodies.append(Obstacle(self,'right',pos=-1,area=-1,fc=(0,0,0),vertices=[(self.W-0.1,-self.H),(self.W-0.1,self.H),(1e12,self.H),(1e12,-self.H)]))

    def step(self):
        """ Advance one step of simulation time """
        self.time+=self.dt
        for b in self.bodies: # movement update                      
            if isinstance(b,MoBody):
                b.update()
        self.update_dist()
        self.update_conn()
        if self.SR>0:
            self.SR-=1
        else: 
            self.SR=self.DRS-1
            self.redraw()

    def redraw(self):
        if self.visual:
            for b in self.bodies:
                if b.on and b.time>self.lastime:
                    if not b.pp==None:
                        b.pp.remove()
                    b.pp=patches.Polygon(b.vertices,fc=b.fc) # the Body is dense
                    self.ax.add_patch(b.pp)
                    if isinstance(b,AniBody) and b.showtrail:
                        self.ax.add_patch(patches.CirclePolygon((b.pos.x,b.pos.y),0.01,fc=b.fc))
                    if isinstance(b,AniBody) and self.shoul:
                        for s in b.souls:
                            if s.time>self.lastime:
                                if not s.pp==None:
                                    s.pp.remove()
                                if s.vertices==None or len(s.vertices)<2:
                                    s.pp=None
                                else:
                                    s.pp=patches.Polygon(s.vertices,fill=False,ec=s.fc,lw=0.5,ls=':') # the Soul is ethereal
                                    self.ax.add_patch(s.pp) 
            if self.showconn:
                while len(self.conngraph)>0:
                    trash=self.conngraph.pop()
                    trash[0].remove()
                if self.ConnCtrl==0:
                    for i in list(self.conn):
                        for j in list(self.conn[i]):
                            d=self.dist[i,j]/self.R
                            self.conngraph.append(self.ax.plot([self.bodies[i].pos.x,self.bodies[j].pos.x],[self.bodies[i].pos.y,self.bodies[j].pos.y],color=(d,d,d),lw=0.3))
                else:
                    for i in list(self.prox):
                        for j in list(self.prox[i]):
                            self.conngraph.append(self.ax.plot([self.bodies[i].pos.x,self.bodies[j].pos.x],[self.bodies[i].pos.y,self.bodies[j].pos.y],color=(0.7,0.7,0.7),lw=0.3))
            if not self.KPIds==None and not self.KPIds.has_been_closed():
                self.KPIds.ax.set_xlim(0,1+int(self.time))
                plt.figure(self.KPIds.fig.number) # make self.KPIds.fig the active plot
                for i in range(len(self.KPIds.KPIplot)):
                    plt.plot(self.time,self.KPIds.KPI[self.KPIds.KPIplot[i][0]],self.KPIds.KPIplot[i][1])
            if not self.has_been_closed():
                plt.figure(self.fig.number) # make self.fig the active plot
                self.movie_writer.grab_frame()
                plt.pause(1e-6)
        self.lastime=self.time

    def has_been_closed(self):
        """ Returns True when the figure where self is drawn is not active """
        if self.visual:
            fig=self.ax.figure.canvas.manager
            active_figs=plt._pylab_helpers.Gcf.figs.values()
            return fig not in active_figs
        else:
            return False

    def close(self):
        if self.loginfo:
            log.write('{} closed, average simulation speed was {}\n'.format(self.name,self.time/(time()-self.t0)))
            log.close()
        if self.visual:
            plt.close(self.fig)
            self.movie_writer.finish()
        if not self.KPIds==None:
            self.KPIds.close()
        del self

    def flash(self,bodies):
        """ Might be useful for debugging """
        i=0
        while i < 10:
            i += 1
            for b in bodies:
                if not b.pp==None:
                    b.pp.remove()
            plt.draw()
            plt.pause(0.02)    
            for b in bodies:
                if not b.pp==None:
                    self.ax.add_patch(b.pp)
            plt.draw()
            plt.pause(0.02)

    def logprint(self,string):
        """ Log printing from outside """
        if self.loginfo:
            log.write(string)

    ## Body's management functions

    def findbody(self,name):
        """ Returns the index in self.bodies of the Body named so """
        names=[self.bodies[i].name for i in range(len(self.bodies))]
        try:
            return names.index(name)
        except ValueError:
            return -1

    def typindices(self,type):
        """ Returns the indices in self.bodies of the Body's of the type """
        indices=[]
        for i in range(len(self.bodies)):
            if isinstance(self.bodies[i],type):
                indices.append(i)
        return indices

    def fits(self,new,where,noverlap=True,safe=0):
        """ Returns True if the new Body fits in where (list of vertices of a polygon) """
        newPolygon=Polygon(new.vertices)
        if Polygon(where).contains(Polygon(new.vertices)):
            if noverlap:
                newPolygon=newPolygon.buffer(new.r_encl+safe)
                for old in self.bodies:
                    if old.on and newPolygon.intersects(Polygon(old.vertices)): return False
                else: return True
        else: return False

    def remobodies(self,ko,why='unspecified reason'):
        """ Removes (offs) all the self.bodies in list ko """
        ko=set(ko)
        for i in ko:
            b=self.bodies[i]
            b.switch(False)
            if self.loginfo:
                log.write('{:.3f}: Removed '.format(self.time)+b.name+' at ({:.2f},{:.2f})'.format(b.pos.x,b.pos.y)+' due to '+why+'\n')

    def update_dist(self):
        """ Updates the matrix of dist between all Body's in self.bodies """
        for i in range(len(self.bodies)):
            bi=self.bodies[i]
            for j in range(i+1,len(self.bodies)):
                bj=self.bodies[j]
                if bi.on and bj.on:
                    self.dist[i,j]=self.dist[j,i]=bi.pos.distance(bj.pos)
                else:
                    self.dist[i,j]=self.dist[j,i]=inf

    def update_conn(self):
        """ Updates the list of conn pairs between AniBody's of the same type in self.bodies """
        """ and also the list of conn pairs in prox """
        self.conn={}; self.prox={}
        for i in range(len(self.bodies)):
            if self.bodies[i].on and isinstance(self.bodies[i],AniBody):
                self.conn[i]=set()
                if self.ConnCtrl>0: self.prox[i]=set()
        if self.ConnCtrl==2: WUG=WUGraph(len(self.bodies)) # for computation of the MST
        for i in list(self.conn):
            type_i=type(self.bodies[i])
            for j in range(i+1,len(self.bodies)):
                if self.bodies[j].on and isinstance(self.bodies[j],type_i) and self.dist[i,j]<self.R: # i and j are kin and near
                    if self.occl:
                        ray=LineString([self.bodies[i].pos,self.bodies[j].pos])
                        for k in range(len(self.bodies)):
                            bk=self.bodies[k]
                            if not k in (i,j) and self.dist[i,k]<self.dist[i,j]+bk.r_encl:
                                if isinstance(bk,Obstacle) and Polygon(bk.vertices).intersects(ray):
                                    break
                        else:
                            self.conn[i] |= {j}
                            self.conn[j] |= {i}
                            if self.ConnCtrl==2: WUG.addEdge(i,j,self.dist[i,j])
                    else:
                        self.conn[i] |= {j}
                        self.conn[j] |= {i}
                        if self.ConnCtrl==2: WUG.addEdge(i,j,self.dist[i,j])
        if self.ConnCtrl==1:
            for i in list(self.conn):
                if self.conn[i]: # not empty
                    mindist=inf
                    for j in list(self.conn[i]):
                        dist=self.dist[i,j]
                        if dist<mindist:
                            mindist=dist; nn=j
                    self.prox[i] |= {nn} # {i} will be added to sel.prox[nn] on due time
        elif self.ConnCtrl==2:
            MST=WUG.MST() # computation of the MST by Boruvka's algorithm
            while MST: # copying into the self.MST (digraph represented by a dictionary)
                (i,j)=MST.pop()
                self.prox[i] |= {j}
                self.prox[j] |= {i}
        elif self.ConnCtrl==3:
            prox1st={}
            for i in list(self.conn): # building RNG locally, in a first round (this round alone, making self.prox<-prox1st, would lead to RNG, not substantilly better than DT for us)
                prox1st[i]=set()
                vneigh=self.voroneigh(i,self.conn[i],self.R)
                for j in vneigh:
                    othervneigh=set(vneigh).remove(j)
                    if ~intersects(intersection(Point(self.bodies[i].pos).buffer(self.dist[i,j]),Point(self.bodies[j].pos).buffer(self.dist[i,j])),othervneigh):
                        prox1st[i] |= {j} # {i} will be added to sel.prox[j] on due time
            for i in list(self.conn): # second round, building my (i) local 2-hop MST graphs
                localprox={}
                localprox[i]=prox1st[i] # start with my neighbors
                for j in prox1st[i]: # enlarge my graph with my relative neighborg's graphs
                    localprox[j] = prox1st[j]
                localWUG=WUGraph(len(self.bodies))
                for ii in list(localprox):
                    for ij in localprox[ii]: localWUG.addEdge(ii,ij,self.dist[ii,ij])
                localMST=localWUG.MST()
                localprox={}
                for ii in list(self.conn):
                    localprox[ii]=set()
                while localMST: # copying into the self.MST (digraph represented by a dictionary)
                    (ii,ij)=localMST.pop()
                    localprox[ii] |= {ij}
                    localprox[ij] |= {ii}
                self.prox[i]=localprox[i]

        # elif self.ConnCtrl==3: VERSION RNG, NO APORTA MUCHO FRENTE A LA SIGUIENTE (DT)
        #     for i in list(self.conn):
        #         vneigh=self.voroneigh(i,self.conn[i],self.R)
        #         for j in vneigh:
        #             othervneigh=set(vneigh).remove(j)
        #             if ~intersects(intersection(Point(self.bodies[i].pos).buffer(self.dist[i,j]),Point(self.bodies[j].pos).buffer(self.dist[i,j])),othervneigh):
        #                 self.prox[i] |= {j} # {i} will be added to sel.prox[j] on due time
        elif self.ConnCtrl==4:
            for i in list(self.conn):
                vneigh=self.voroneigh(i,self.conn[i],self.R)
                for j in vneigh:
                    self.prox[i] |= {j} # {i} will be added to sel.prox[j] on due time

    def conn_subgraph(self,type): 
        """ Returns the subgraph of conn formed by the on AniBody's of type only """
        """ Useful (actually used) in some applications, like Boids """
        result={}
        for i in range(len(self.bodies)):
            if self.bodies[i].on and isinstance(self.bodies[i],type):
                result[i]=self.conn[i]
        return result
    
    ## Perception functions: they must be defined in the Body's Space, not in the Body itself

    def nearby(self,i,type,r,rng=pi):
        """ Returns a list with the Body's of type "visible" from Body i """
        pos=self.bodies[i].pos
        th=self.bodies[i].th
        nearby=[]
        a=np.linspace(-rng,rng,12) 
        vpa=[(r*cos(x),r*sin(x)) for x in a] # vertices in perception area, relative to pos and th
        if rng<pi: # when not full range, the body (its centroid) is another vertex
            vpa.append((0,0))
        pa=translate(rotate(Polygon(vpa),th,(0,0),True),pos.x,pos.y) # rotate th and translate to pos the perception area
        for j in range(len(self.bodies)):
            bj=self.bodies[j]
            if bj.on and isinstance(bj,type) and j != i and self.dist[i,j]<(r+bj.r_encl) and pa.intersects(Polygon(bj.vertices)): # intersects perception area
                ray=LineString([pos,self.nearestpoint(i,bj)])
                for k in range(len(self.bodies)):
                    bk=self.bodies[k]
                    if not k in (i,j) and self.dist[i,k]<self.dist[i,j]+bk.r_encl:
                        if isinstance(bk,Obstacle) and Polygon(bk.vertices).intersects(ray): # occlusion
                            break
                else:
                    nearby.append(bj)
        return nearby

    def RnB(self,i,type,r,rng=pi,fast=True):
        """ Simulates a range&bearing sensor: Returns a list with the readings of the nearest points of Body's of type nearby "visible" from Body i """
        neigh=self.nearby(i,type,r,rng)
        readings=[]
        if fast: # approx with pos and r_encl
            for n in neigh:
                j=n.index()
                i2n=Point2D(self.bodies[j].pos.x-self.bodies[i].pos.x,self.bodies[j].pos.y-self.bodies[i].pos.y)
                readings.append((i2n.r-n.r_encl,pipi(i2n.a-self.bodies[i].th)))
        else:
            for n in neigh:
                i2n=Point2D(self.nearestpoint(i,n))-Point2D(self.bodies[i].pos.x,self.bodies[i].pos.y)
                readings.append((i2n.r,pipi(i2n.a-self.bodies[i].th)))
        return readings
    
    def clearway(self,i,type,r,rng=pi,N=30,th0=0):
        """ Returns the closest to th0 angle th0+(-rng:rng/N:rng) in which the buffered straight way is clear from Body's of type nearby "visible" from Body i """
        """ The corridor cannot surround the original position, otherwise it can be stuck by close obstacles """
        P0=Point2D(self.bodies[i].pos.x,self.bodies[i].pos.y)
        w=self.bodies[i].r_encl
        if r<4*w: r=4*w # coherent with corridor measures
        neigh=self.nearby(i,type,r,rng)
        th=0
        dth=rng/N
        while abs(th)<=rng:
            P1=P0+Point2D(r=2*w,a=pipi(th0+th))
            P2=P0+Point2D(r=r-2*w,a=pipi(th0+th))
            corridor=Polygon(LineString([Point(P1.x,P1.y),Point(P2.x,P2.y)]).buffer(2*w))
            for n in neigh:
                if corridor.intersects(Polygon(n.vertices)):
                    break
            else:
                # if abs(th)>0: self.bodies[i].souls[1].vertices=corridor.exterior.coords
                return th0+th
            if th>0:
                th=-th
            else:
                th=-th+dth
        return inf

    def nearest(self,i,type,r,rng=pi):
        """ Returns the nearest to Body i of the nearby Body's of type """
        pos=self.bodies[i].pos
        nearby=self.nearby(i,type,r,rng)
        nearest=None
        mindist=r
        while len(nearby)>0:
            dist=pos.distance(Polygon(nearby[-1].vertices))
            if dist<mindist:
                nearest=nearby.pop()
                mindist=dist
            else:
                nearby.pop()
        return nearest

    def nearestpoint(self,i,b):
        """ Returns the coords of the nearest to Body i point of b """
        np=nearest_points(Point(self.bodies[i].pos),Polygon(b.vertices))
        return (np[1].x,np[1].y)

    def reflectionpoint(self,i,b):
        """ Returns the coords of the reflection of Body i through its nearest point in b """
        np=nearest_points(Point(self.bodies[i].pos),Polygon(b.vertices))
        return (2*np[1].x-np[0].x,2*np[1].y-np[0].y)

    def incontact(self,i,type):
        """ Returns a list with the indices of the Body's of type in contact with Body i """
        bi=self.bodies[i]
        pbi=Polygon(bi.vertices)
        incontact=[]
        for j in range(len(self.bodies)):
            bj=self.bodies[j]
            if bj.on and isinstance(bj,type) and j != i and self.dist[i,j]<(bi.r_encl+bj.r_encl) and pbi.intersects(Polygon(bj.vertices)):
                incontact.append(j)
        return incontact

    # def voronoi(self,me,neigh,r,safe=0):
    #     """ Return the vertices of the Voronoi cell <r with the neigh around me, neigh is a list of Bodies """
    #     """ Adapted from gadgETs/voronoi to deal with Body's identities """
    #     """ POSSIBLY NOT NEEDED, ONLY VORONEIGH NEEDS TO BE ADAPTED? """
    #     pm=Point2D(self.bodies[me].pos)
    #     W=Polygon(pm.buffer(r))
    #     for n in neigh:
    #         pn=Point2D(self.bodies[n].pos)
    #         v=pn-pm
    #         pc=pm+0.5*v
    #         v.r=1
    #         pc=pc-safe*v
    #         v.r=r
    #         q0=pn+2*v
    #         v.a = v.a+pi/2
    #         q1=pc+2*v
    #         q2=pc-2*v
    #         W -= Polygon([(q0.x,q0.y),(q1.x,q1.y),(q2.x,q2.y)])
    #     if type(W)==Polygon:
    #         return list(W.exterior.coords)
    #     else:
    #         return([])

    def voroneigh(self,me,neigh,r):
        """ Returns the Voronoi neighbors Bodies, a subset of neigh (a list of Bodies) """
        """ Addapted from gadgETs/voronoi """
        pneigh=[]
        pme=(self.bodies[me].pos.x,self.bodies[me].pos.y)
        for n in neigh:
            pneigh.append((self.bodies[n].pos.x,self.bodies[n].pos.y))
        W=Polygon(voronoi(pme,pneigh,r,-0.001)) # the 0.001 is to avoid rounding mistakes
        Pme=Point2D(pme)
        vneigh=[]
        for n in neigh:
            Pn=Point2D(self.bodies[n].pos.x,self.bodies[n].pos.y)
            v=Pn-Pme
            Pc=Pme+0.5*v
            v.r=r
            q0=Pn+2*v
            v.a = v.a+pi/2
            q1=Pc+2*v
            q2=Pc-2*v
            if W.intersects(Polygon([(q0.x,q0.y),(q1.x,q1.y),(q2.x,q2.y)])): vneigh.append(n)
        return vneigh

class KPIdataset: # a dataset with the key performance indices 
    
    def __init__(self,name,space,KPI0,KPIplot=[]):
        self.name=name
        self.space=space
        self.KPI=KPI0 # initial value of the n KPIs
        self.KPIplot=KPIplot # KPIs format to plot when visual [(i,'{.-:o+*}{rgbcmyk}'),...]
        if self.space.datxt:
            global dtxt # All KPI data are dumped to a csv file
            dtxt=open(self.name+'.csv','w')
        if self.space.visual and len(self.KPIplot):
            self.fig=plt.figure(figsize=(self.space.SS*16/sqrt(16**2+9**2), self.space.SS*9/2/sqrt(16**2+9**2))) # 16:9/2 proportion
            self.ax=self.fig.add_axes([0.1,0.1,0.8,0.8]) # 10% margin
            self.ax.set_facecolor('w') # white background
            self.ax.set_xlim(0, 1) # initial time scale (will expand from 0 to "now" as time passes)
            self.ax.set_ylim(0, 1) # all KPIs should be normalized
        else: self.fig=None      
        self.space.KPIds=self

    def update(self,KPI):
        """ Update the values in KPI, and write them in the dtxt file """
        self.KPI=KPI
        if self.space.datxt:
            dtxt.write('{:.3f}'.format(self.space.time))
            for i in range(len(KPI)):
                dtxt.write(' {:.6f}'.format(KPI[i]))
            dtxt.write('\n')

    def has_been_closed(self):
        """ Returns True when the figure where self is drawn is not active """
        if self.fig:
            fig=self.ax.figure.canvas.manager
            active_figs=plt._pylab_helpers.Gcf.figs.values()
            return fig not in active_figs
        else: return False

    def close(self):
        if self.space.datxt: dtxt.close()
        if self.space.visual and len(self.KPIplot) and not self.has_been_closed():
            self.fig.savefig(self.name+'.pdf', orientation='landscape', format='pdf')
            plt.close(self.fig)
        del self

class Body: # Something in a Space
    
    def __init__(self,space,name,vertices,pos=-1,th=0,area=-1,fc=(0,0,0)):
        """ name should be unique, it is for info but also used to find a Body
            pos is (x,y), within [-W:W,-H:H] save for borders; -1 for absolute vertices, typically for obstacles
            th in rad, 0 is pointing right
            area is -1 for absolute vertices; constant values below have been chosen to be nice with W=16 H=9 (total area=576)
            vertices are relative (save otherwise indicated by -1's), they are affected by area scale, pos translation and th rotation
            fc=black by default; the default for subclasses are different (grey, blue, yellow, green, red, cyan), and typically objects are fc-ish
        """
        self.time=0 # time of last change (to avoid redrawing the same)
        self.space=space
        self.name=name # str
        self.vertices=vertices # list of (x,y) defining a polygon, for graphical representation
        polygon=Polygon(self.vertices)
        if area==-1: # do not scale
            self.area=polygon.area
        else:
            self.area=area
            fact=sqrt(self.area/polygon.area)
            polygon=scale(polygon,fact,fact,origin='centroid')
        centroid=polygon.centroid
        if pos==-1: # vertices positions are absolute
            self.pos=centroid
            self.th=0
        else:
            self.pos=Point(pos) # unconstrained, but usually within [-W:W,-H:H] -- except borders
            self.th=pipi(th) # rad in [-pi:pi]
            polygon=translate(polygon,self.pos.x-centroid.x,self.pos.y-centroid.y)
            polygon=rotate(polygon,self.th,origin='centroid',use_radians=True)
        self.vertices=list(polygon.exterior.coords)
        self.r_encl=0 # radius of enclosing circle centered at c
        for vertex in self.vertices:
            Pv=Point(vertex)
            d=self.pos.distance(Pv)
            if d>self.r_encl:
                self.r_encl=d            
        self.fc=fc #(R,G,B)
        if self.space.visual:
            self.pp=None # to store the current plot patch
        self.on=True
 
    def __repr__(self):
        return self.name+' is a '+str(self.__class__)[17:-2]+' at ({:.2f},{:.2f})'.format(self.pos.x,self.pos.y)

    def switch(self,on):
        """ Turn on or off, i.e., "remove" """
        if on==False:
            if self.space.visual:
                if not self.pp==None:
                    self.pp.remove()
                    self.pp=None
                if isinstance(self,AniBody):
                    for s in self.souls:
                        s.vertices=None
                        if not s.pp==None:
                            s.pp.remove()
                            s.pp=None
        self.on=on
        self.time=self.space.time # something changed

    def index(self):
        """ Returns the index in self.space.bodies of self """
        bodies=[self.space.bodies[i] for i in range(len(self.space.bodies))]
        try:
            return bodies.index(self)
        except ValueError:
            return -1

class Obstacle(Body):
    
    def __init__(self,space,name,vertices=[],pos=0,th=0,area=0,fc=0):
        """ pos==0 for random pose, area==0 for random size """
        if pos==0: # random pose
            pos=(uniform(-self.W,self.W),uniform(-self.H,self.H))
            th=uniform(-pi,pi)
        if area==0: # random size
            area=uniform(0.5,1)
        if len(vertices)==0:
            for i in range(12):
                vertices.append((cos(i/6*pi),sin(i/6*pi)))
        if fc==0:
            R=G=B=uniform(0.2,0.4) # dark grey
            fc=(R,G,B)
        super().__init__(space,name,vertices,pos,th,area,fc)

class Nest(Body):
    def __init__(self,space,name,pos=0,th=0,area=0,vertices=[],fc=0):
        """ pos==0 for random pose, area==0 for random size """
        if pos==0: # random pose
            pos=(uniform(-self.W,self.W),uniform(-self.H,self.H))
            th=uniform(-pi,pi)
        if area==0: # random size
            area=uniform(1,5)
        if len(vertices)==0:
            for i in range(36):
                vertices.append((cos(i/18*pi),sin(i/18*pi)))
        if fc==0:
            R=G=0
            B=uniform(0.5,1) # blue
            fc=(R,G,B)
        super().__init__(space,name,vertices,pos,th,area,fc)

class Food(Body):
    def __init__(self,space,name,pos=0,th=0,area=0,vertices=[],fc=0):
        """ pos==0 for random pose, area==0 for random size """
        if pos==0: # random pose
            pos=(uniform(-self.W,self.W),uniform(-self.H,self.H))
            th=uniform(-pi,pi)
        if area==0: # random size
            area=uniform(0.005,0.02)
        if len(vertices)==0:
            for i in range(12):
                vertices.append((cos(i/6*pi),sin(i/6*pi)))
        if fc==0:
            R=G=uniform(0.7,1)
            B=0 # yellow-ish
            fc=(R,G,B)
        super().__init__(space,name,vertices,pos,th,area,fc)

class MoBody(Body): # Moving Body

    def __init__(self,space,name,vertices=[],pos=-1,th=0,area=-1,fc=(0,0,0),v=0,w=0,vth=0,v_max=0,w_max=0,v_min=0):
        super().__init__(space,name,vertices,pos,th,area,fc)
        # velocities are expressed as /s
        self.v=v
        if v>v_max: v_max=v
        self.w=w
        if w>w_max: w_max=w
        self.vth=vth
        self.E=0 # for "energy" accountability
        self.set_velim(v_max,w_max,v_min)

    def __repr__(self):
        return super().__repr__()+' with velocity '+str((self.v,self.w,self.vth))

    def teleport(self,pos=None,th=None):
        """ Teleport to pos,th """
        polygon=Polygon(self.vertices)
        if pos!=None:
            pos=Point(pos)
            polygon=translate(polygon,pos.x-self.pos.x,pos.y-self.pos.y)
            self.pos=pos
        if th!=None:
            th=pipi(th)
            polygon=rotate(polygon,pipi(th-self.th),origin='centroid',use_radians=True)
            self.th=th
        self.vertices=list(polygon.exterior.coords)
        self.time=self.space.time # something changed

    def set_velim(self,v_max='=',w_max='=',v_min='='):
        """ Change limit velocities """
        if v_max != '=': self.v_max=max(0,v_max) # dist/s
        if w_max != '=': self.w_max=max(0,w_max) # rad/s
        if v_min != '=': self.v_min=max(0,v_min) # dist/s
        self.cmd_vel() # apply the new limits

    def cmd_vel(self,v='=',w='=',vth='='):
        """ Change v, w, vth respecting their limits. '=' means don't change. v and w can be increased or decreased with '+' or '-'."""
        v_old=self.v; w_old=self.w # for "energy" accountability
        if v=='=':
            v=self.v
        elif v=='+':
            v=self.v+self.v_max/10
        elif v=='-':
            v=self.v-self.v_max/10
        self.v=min(max(abs(v),self.v_min),self.v_max) # dist/s
        if w=='=':
            w=self.w
        elif w=='+':
            w=self.w+self.w_max/10
        elif w=='-':
            w=self.w-self.w_max/10
        self.w=max(-self.w_max,min(w,self.w_max)) # rad/s
        if vth=='=':
            vth=self.vth
        if self.v>v_old: E=0.5*(self.v-v_old)/self.v_max
        self.vth=max(-pi,min(vth,pi)) # rad (angle of velocity vector)
        self.time=self.space.time # something changed
        self.E+=0.25*abs(self.w-w_old)/self.w_max+0.5*max(self.v-v_old,0)/self.v_max # a kind of "energy" (1 in a o to max change of both v and w)

    def update(self):
        """ Update pose of self. Linear approx because dt (must be) short """
        if self.on and abs(self.v)+abs(self.w)>0:
            dt=self.space.dt
            dth=self.w*dt
            dx=self.v*dt*cos(self.th+dth/2+self.vth) # vth is the rel angle of velocity vector
            dy=self.v*dt*sin(self.th+dth/2+self.vth)
            # Going beyond one limit teleports to the contrary
            if self.pos.x+dx>self.space.W:
                dx=dx-2*self.space.W
            elif self.pos.x+dx<-self.space.W:
                dx=dx+2*self.space.W
            if self.pos.y+dy>self.space.H:
                dy=dy-2*self.space.H
            elif self.pos.y+dy<-self.space.H:
                dy=dy+2*self.space.H
            self.pos=translate(self.pos,dx,dy)
            self.th=pipi(self.th+dth)
            polygon=Polygon(self.vertices)
            polygon=translate(polygon,dx,dy)
            polygon=rotate(polygon,dth,origin='centroid',use_radians=True)
            self.vertices=list(polygon.exterior.coords)
            self.time=self.space.time # something changed

class MObstacle(MoBody,Obstacle): # A Moving Obstacle
    def __init__(self,space,name,vertices=[],pos=0,th=0,area=0,fc=0,v=0,w=0,vth=0,v_max=0,w_max=0,v_min=0):
        if len(vertices)==0:
            for i in range(30):
                vertices.append((cos(i/15*pi),sin(i/15*pi)))        
        if area==0: # random size
            area=uniform(0.05,0.1)
        if fc==0:
            R=G=B=uniform(0.6,0.8) # light grey
            fc=(R,G,B)
        super().__init__(space,name,vertices,pos,th,area,fc,v,w,vth,v_max,w_max,v_min)

    def update(self):
        super().update()
        if random()>0.95: # random velocity changes (not time-regular, they are more frequent when the body is updated more often)
            self.cmd_vel(choice(('+','-','=')),choice(('+','-','=')),'=')

class AniBody(MoBody): # An Animated (Moving) Body
    def __init__(self,space,name,vertices=[],pos=-1,th=0,area=-1,fc=(0,0,0),v=0,w=0,vth=0,v_max=0,w_max=0,v_min=0,showtrail=False):
        super().__init__(space,name,vertices,pos,th,area,fc,v,w,vth,v_max,w_max,v_min)
        self.showtrail=showtrail
        self.souls=[] # They must be given later by calling for a Soul(body,T)
        self.knows=None # It must be given later by calling for a Knows(body)

    def update(self): # AniBodies specialize the MoBody.update method by updating also their souls
        super().update()
        for s in self.souls:
            s.update()

class Mobot(AniBody): # A member of the swarm of mobile robots; there should be many
    def __init__(self,space,name,vertices=[],pos=0,th=0,area=0,fc=0,v=0,w=0,vth=0,v_max=0,w_max=0,v_min=0,showtrail=False):
        if len(vertices)==0:
            vertices=[(2,0),(0,0.5),(0,-0.5)]
        if area==0:
            area=uniform(0.005,0.01)
        if fc==0:
            R=0
            G=uniform(0.7,1)
            B=uniform(0,0.5*G) # green-ish
            fc=(R,G,B)
        super().__init__(space,name,vertices,pos,th,area,fc,v,w,vth,v_max,w_max,v_min,showtrail)

class Killer(AniBody): # Chases Mobots; might be more than one, collaborating or not
    def __init__(self,space,name,vertices=[],pos=0,th=0,area=0,fc=0,v=0,w=0,vth=0,v_max=0,w_max=0,v_min=0,showtrail=False):
        if len(vertices)==0:
            vertices=[(4,0),(0,0.5),(-2,2),(-1,0),(-2,-2),(0,-0.5)]
        if area==0:
            area=uniform(0.01,0.02)
        if fc==0:
            R=uniform(0.7,1)
            G=0
            B=uniform(0,0.5*R) # red-ish
            fc=(R,G,B)
        super().__init__(space,name,vertices,pos,th,area,fc,v,w,vth,v_max,w_max,v_min,showtrail)

class Shepherd(AniBody): # Takes care of the Mobots; might be more than one, collaborating or not
    def __init__(self,space,name,vertices=[],pos=0,th=0,area=0,fc=0,v=0,w=0,vth=0,v_max=0,w_max=0,v_min=0,showtrail=False):
        if len(vertices)==0:
            vertices=[(4,0),(0,1),(-2,0),(0,-1)]
        if area==0:
            area=uniform(0.01,0.02)
        if fc==0:
            R=0
            G=B=uniform(0.7,1) # cyan-ish
            fc=(R,G,B)
        super().__init__(space,name,vertices,pos,th,area,fc,v,w,vth,v_max,w_max,v_min,showtrail)

class Soul: # Something within a AniBody that controls it: manipulates its behavior in response to its environment, possibly using what it knows

    def __init__(self,body,T=0,fc=None):
        self.body=body
        if T<2*self.body.space.dt:
            T=self.body.space.dt
        self.T=T # period duration, if T<2*dt then T=dt (pseudo-continuous, update at every step)
        self.time=0
        if fc==None:
            self.fc=body.fc
        else:
            self.fc=fc
        body.souls.append(self)
        self.vertices=None # vertices of a polygon for graphical representation
        if self.body.space.visual:
            self.pp=None #  # to store the current plot patch

    def update(self):
        """ this update is called in the (ani)body update """
        """ it actually updates the self.time at the beginning and (about) after each self.T """
        """ subclasses of Soul specialize this update function their own way when a call to this super().update() returns True """ 
        if self.time<=self.T+self.body.space.dt/2 or self.body.space.time+self.body.space.dt/2>self.time+self.T:
            self.time+=max(self.T,self.body.space.dt)
            return True
        else:
            return False

class GoTo(Soul):
    """ Low-level Soul to go somewhere by several step-by-step cmd_vel's (rather than one teleport)
        When no where to go keepgoing, stop, wander oe zigzag.
        Avoids obstacles
    """

    def __init__(self,body,T,cosexp=3,Kp=5,tol=0,nw='keepgoing',p=0.01,obstalikes=None,bumper=0,OEF=0.3,rng=pi,fc=None):
        self.cosexp=cosexp # exponent for the cosine of the velecity direction with the heading
        self.Kp=Kp # Kp for the P ctrl of w wrt th error (1 is ok for small T)
        self.tol=tol # a number of times the r_encl to consider destination reached
        self.nw=nw # ''keepgoing', stop', 'wander', 'zigzag' when no where to go
        self.p=p # probability [0,1] to change vel when wandering
        self.obstalikes=obstalikes # types of Body's to be avoided as obstacles
        self.bumper=bumper # distance to activate collision avoidance
        self.OEF=OEF # Obstacle Evitation Factor to combine "repulsive force"
        self.rng=rng # obstacles in front, from 0 to rng
        self.where=None # (x,y) or Point destination
        self.when=0 # time to arrive at destination
        super().__init__(body,T,fc)
    
    def cmd_set(self,where='=',after='=',Kp='=',tol='=',nw='=',p='=',obstalikes='=',bumper='='):
        """ Set destination, arrival time after secs, Kp, tol, nw, and p; '=' to keep current values  """
        if where != '=':
            if where==None:
                self.where=None
            else:
                self.where=Point(where)
        if after != '=': self.when=self.time+max(after,self.body.space.dt)
        if Kp != '=': self.Kp=Kp
        if tol != '=': self.tol=tol
        if nw != '=': self.nw=nw
        if p != '=': self.p=p
        if obstalikes != '=': self.obstalikes=obstalikes
        if bumper != '=': self.bumper=bumper

    def update(self):
        if super().update():
            b=self.body; i=b.index()
            if i>=0:
                s=b.space
                if self.where != None:
                    arrow=Point2D(self.where.x-b.pos.x,self.where.y-b.pos.y) # a vector to the destination
                    if arrow.r<self.tol: arrow.r=0; self.where=None
                if self.where == None: # might have just become None above
                    arrow=Point2D(0,0)
                    if self.nw=='stop': # reset v and w
                        b.cmd_vel(v=0,w=0) # this will NOT stop a fUAV (required to set_velim)
                    elif self.nw=='wander': # random changes of w, v_max
                        b.cmd_vel(v=b.v_max)
                        if random()<self.p:
                            b.cmd_vel(v=b.v_max,w=choice(('+','-','=')))
                    elif self.nw=='zigzag': # random changes of direction, v_max
                        b.cmd_vel(v=b.v_max,w=0)
                        if random()<self.p:
                            b.teleport(th=self.body.th+uniform(-1,1)*pi)
                    elif self.nw=='keepgoing': # keep moving in same direction
                        b.cmd_vel(w=0)
                if self.obstalikes!=None:
                    obs=s.nearby(i,self.obstalikes,r=self.bumper,rng=self.rng)
                    if len(obs):
                        for o in obs: # add to arrow a "repulsive vector" away from each obstacle
                            npo=Point(s.nearestpoint(i,o)); arro=Point2D(b.pos.x-npo.x,b.pos.y-npo.y)
                            arro.r=self.OEF*(self.bumper-arro.r)/arro.r; arrow+=arro
                self.vertices=[(b.pos.x,b.pos.y),(b.pos.x+arrow.x,b.pos.y+arrow.y)] # the Soul apearance is arrow
                if arrow.r>0:
                    if self.when<=self.time: self.when=(self.time+s.dt)
                    misorientation=pipi(arrow.a-b.th) # turn almost completely without advance, then advance to arrive on time
                    w=self.Kp*misorientation # control P of w
                    v=arrow.r/max((self.when-self.time),s.dt)*max(0,cos(misorientation)**self.cosexp) # control JIT of v 
                    if self.where != None: b.cmd_vel(v,w)
                    elif b.v>0: b.cmd_vel(max(v,b.v),w) # this is obstacle avoidance when there is no where to go, and not stopped
            return True
        else: return False

class Knowledge: # What a Soul knows
    """ A class to contain what a (Ani)Body knows, and to communicate it to others
        The basic version contains only a state variable, that can be set and tell
    """

    def __init__(self,body,state='idle'):
        self.body=body
        self.state=state
        body.knows=self

    def set_state(self,state):
        self.state=state

    def tell_state(self):
        return self.state

## MAIN: a meaningless demo of almost everything (and a typical pattern for the main code)

def init():

    ## Create Data Structures
    name='SW2D_'+strftime("%Y%m%d%H%M", localtime())
    global s, N
    s=Space(name,dt=0.01,DRS=4,R=3,occl=True,ConnCtrl=2,limits='hv',randomseed=0,visual=True,showtrail=True,showconn=True,datxt=True,loginfo=True)
    KPIdataset(name,s,[0,1],[(0,'.y'),(1,'.r')])

    ## Populate the world
    N=50

    # two Nests
    i=0
    while i<2:
        new=Nest(s,'n'+str(i),pos=(uniform(-s.W,s.W),uniform(-s.H,s.H)),th=uniform(-pi,pi))
        if s.fits(new,s.room,safe=5):
            s.bodies.append(new)
            i += 1

    # ten Obstacles
    i=0
    while i<10:
        new=Obstacle(s,'O'+str(i),pos=(uniform(-s.W,s.W),uniform(-s.H,s.H)),th=uniform(-pi,pi))
        if s.fits(new,s.room,safe=1):
            s.bodies.append(new)
            i += 1

    # ten MObstacles
    i=0
    while i<10:
        new=MObstacle(s,'MO'+str(i),pos=(uniform(-s.W,s.W),uniform(-s.H,s.H)),th=uniform(-pi,pi),v=s.vN/20,v_max=s.vN/10,w_max=s.wN/10)
        if s.fits(new,s.room,safe=1):
            s.bodies.append(new)
            i += 1

    # N Mobots
    i=0
    while i<N:
        new=Mobot(s,'m'+str(i),pos=(uniform(-s.W,s.W),uniform(-s.H,s.H)),th=uniform(-pi,pi),v_max=s.vN/uniform(2,4),w_max=s.wN,showtrail=s.showtrail)
        if s.fits(new,s.room,safe=new.r_encl*5):
            s.bodies.append(new)
            i += 1

    # a few Killers
    i=0
    while i<N/5:
        new=Killer(s,'k'+str(i),pos=(uniform(-s.W,s.W),uniform(-s.H,s.H)),th=uniform(-pi,pi),v_max=s.vN/uniform(1,2),w_max=s.wN/4)
        if s.fits(new,s.room,safe=new.r_encl*5):
            s.bodies.append(new)
            i += 1

    # a few Shepherds
    i=0
    while i<N/4:
        new=Shepherd(s,'s'+str(i),pos=(uniform(-s.W,s.W),uniform(-s.H,s.H)),th=uniform(-pi,pi),v_max=s.vN/uniform(1,3),w_max=s.wN/2)
        if s.fits(new,s.room,safe=new.r_encl*5):
            s.bodies.append(new)
            i += 1
    
    # many Foods in the empty spaces
    i=0
    j=0
    while j<30:
        new=Food(s,'f'+str(i),pos=(uniform(-s.W,s.W),uniform(-s.H,s.H)),th=uniform(-pi,pi))
        if s.fits(new,s.room,safe=new.r_encl*10):
            s.bodies.append(new)
            i += 1
            j=0
        else: j += 1

    # animation
    for b in s.bodies:
        if isinstance(b,MoBody):
            b.cmd_vel(v=b.v_max)
        if isinstance(b,AniBody):
            GoTo(b,T=0,nw=choice(['wander','zigzag']),obstalikes=(Obstacle),bumper=5*b.r_encl) # they wander or zigzag to no where

    s.dist=np.zeros((len(s.bodies),len(s.bodies))) # distances between centroids in a np.matrix
    s.update_dist()
    s.update_conn()

    if s.loginfo:
        log.write("{:d} initial Body's:\n".format(len(s.bodies)))
        for b in s.bodies: log.write(repr(b)+'\n')

if __name__ == '__main__': 

    init()
    end=False
    while not end: # THE loop
        s.step()
        ko=[]
        for b in s.bodies: # collision management
            i=b.index()
            if i>=0:
                if isinstance(b,Obstacle):
                    ko+=s.incontact(i,AniBody)
                elif isinstance(b,Mobot):
                    ko+=s.incontact(i,(Food,Mobot))
                elif isinstance(b,Killer):
                    ko+=s.incontact(i,(Mobot,Killer))
                elif isinstance(b,Shepherd):
                    ko+=s.incontact(i,(Killer,Shepherd))
        s.remobodies(ko,'collision')

        KPI=[s.time/(time()-s.t0),0] # KPIs [simulation speed, surviving mobots]
        for b in s.bodies:
            if b.on and isinstance(b,Mobot):
                KPI[1] += 1
        KPI[1] /= N
        s.KPIds.update(KPI)

        end=s.has_been_closed() or s.KPIds.KPI[1]==0 or s.time>30
    else:
        s.close()
