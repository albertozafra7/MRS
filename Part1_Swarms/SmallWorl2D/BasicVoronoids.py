## (Not so) BasicVoronoids
## Version: 20231130
## Author: Enrique Teruel (ET) eteruel@unizar.es
## License: CC-BY-SA

from time import time, localtime, strftime
from random import uniform
from shapely.geometry import Point, Polygon                                                                 

import numpy as np

from gadgETs import voronoi
from SmallWorl2D import Space, KPIdataset, Obstacle, MObstacle, Mobot, Soul, GoTo

class Voronoid(Soul):
    """ Soul of a Voronoi's-based mobile sensor in a network covering a static region, Cortes2004 like """
    
    def __init__(self,body,T,Q=[],r=1,safe=0,fc=None):
        self.Q=Q # list of vertices of the polygon region to be covered
        self.r=r
        # self.rng=rng # when smaller than pi works badly, too many collisions
        self.safe=safe # a safety distance to shrink the Voronoi cells
        self.d=0 # distance of last GoTo /r (a KPI)
        super().__init__(body,T,fc)
        # (Pseudo-continuous) Low-level motion control
        GoTo(body,T=0,Kp=10,tol=body.r_encl/4,nw='keepgoing')
        self.GoTo=body.souls[-1]

    def update(self):
        if super().update():
            b=self.body
            i=b.index()
            s=b.space
            if i>=0:
                bpos=(b.pos.x,b.pos.y)
                neigh=s.nearby(i,(type(b),Obstacle),self.r)
                npos=[]
                for n in neigh:
                    # Using RnB here would be a nonsense, since afterwards we would need compute the coords of the neigh's
                    if isinstance(n,Obstacle):
                        npos.append(s.reflectionpoint(i,n)) # better than the nearest point, which makes sense too
                    else:
                        npos.append(s.nearestpoint(i,n))

                self.W = Polygon(voronoi(bpos,npos,self.r/2,self.safe))
                if len(self.Q): self.W &= Polygon(self.Q)
                self.vertices=list(self.W.exterior.coords) # Soul represented by the destination Voronoi cell
                self.GoTo.cmd_set(self.W.centroid,self.T)
                self.d=Point(bpos).distance(self.W.centroid)/self.r
            return True
        else: return False


## MAIN

name='BasicVoronoids'+strftime("%Y%m%d%H%M", localtime())
N=50; R=4
s=Space(name,R=R,occl=True,ConnCtrl=4,limits='hv',visual=True,shoul=True,showtrail=False,showconn=True,loginfo=True)
KPIdataset(name,s,[1,1],[(0,'.y'),(1,'.k')])
s.bodies.append(Obstacle(s,'O',pos=-1,area=-1,vertices=[(-s.W,-s.H),(s.W/2,-s.H),(s.W/2,0),(s.W,0),(s.W,s.H),(0,s.H)],fc=(1,0,0))) # auxiliary
s.bodies.append(MObstacle(s,'B1',pos=(1,4),area=2,th=uniform(-np.pi,0),v=0.1*s.vN,v_max=0.2*s.vN,w_max=0.05*s.wN))
s.bodies.append(MObstacle(s,'B2',pos=(2,-4),area=2,th=uniform(0,np.pi),v=0.1*s.vN,v_max=0.2*s.vN,w_max=0.05*s.wN))
s.bodies.append(Obstacle(s,'W1',pos=-1,area=-1,vertices=[(-s.W,-1),(-2,-1),(-2,1),(-s.W,1)],fc=(0,0,0)))
s.bodies.append(Obstacle(s,'W2',pos=-1,area=-1,vertices=[(s.W/2-1,s.H),(s.W/2-1,2),(s.W/2+1,2),(s.W/2+1,s.H)],fc=(0,0,0)))
i=0
while i<N:
    new=Mobot(s,'m'+str(i),pos=(uniform(-s.W,s.W),uniform(-s.H,s.H)),th=uniform(-np.pi,np.pi),area=0.02,v_max=s.vN,w_max=s.wN,fc=[0,0,1],showtrail=s.showtrail)
    if s.fits(new,s.room,safe=new.r_encl):
        s.bodies.append(new); i += 1
        Voronoid(new,Q=[],r=R,safe=new.r_encl,T=uniform(0.1,0.2),fc=[0.8,0.8,1])       
s.remobodies([4],'it was auxiliary') # remove the auxiliary obstacle
s.dist=np.zeros((len(s.bodies),len(s.bodies))) # distances between centroids in a np.matrix
s.update_dist(); s.update_conn()

end=False
while not end:
    s.step()
    ko=[]
    for b in s.bodies: # collision management
        if isinstance(b,(Obstacle,Mobot)): ko+=s.incontact(b.index(),Mobot)
    s.remobodies(ko,'collision')

    KPI=[s.time/(time()-s.t0),0] # KPIs [simulation speed, max distance moved]
    for b in s.bodies:
        if isinstance(b,Mobot): KPI[1] = max(KPI[1],b.souls[0].d)
    s.KPIds.update(KPI)
    end=s.has_been_closed() or s.time>120 or s.time>2 and s.KPIds.KPI[1]<0.01
else: s.close()