## gadgETs: Collection of convenience low level functions and the like
## Version: 20231020
## Author: Enrique Teruel (ET) eteruel@unizar.es
## License: CC-BY-SA

from math import pi, sqrt
from shapely.geometry import Point, Polygon
from shapely.affinity import translate, rotate, scale
from point2d import Point2D 

def coordlistr(list):
    string=''
    for p in list:
        string=string+' {:.3f},{:.3f} '.format(p[0],p[1])
    return string

def listrcoord(listr):
    coords=[]
    for p in listr:
        [x,y]=p.split(',')
        coords.append((float(x),float(y)))
    return coords

def tuplestr(tuple):
    string=''
    for c in tuple:
        string=string+' {:.3f} '.format(c)
    return string

def pipi(angle):
    """ Put angle (in rad) in [-pi:pi] """
    while angle>pi:
        angle=angle-2*pi
    while angle<-pi:
        angle=angle+2*pi
    return angle

def ellipse(n,c0,th0=0,A=1,ar=1):
    """ Return a 4n-vertices polygon inscribed in ellipse centered at c0=[x0,y0], oriented towards th0, with area A and aspect ratio ar=b/a, a horizontal radius """
    vertices=[Point2D(r=1,a=x*2*pi/n) for x in range(int(n/4)*4)]
    e=Polygon([(vertices[i].x,vertices[i].y) for i in range(len(vertices))]) # a unit circle at the origin
    a=sqrt(A/pi/ar) # a so that the area of the ellipse is A
    e=scale(e,a,ar*a)
    e=rotate(e,th0,use_radians=True)
    e=translate(e,c0[0],c0[1])
    return list(e.exterior.coords)

def maxdistellipses(n,c0,th,A,ar):
    """ Return the maximum distance between corresponding points of two ellipses """
    n=int(n)
    V1=ellipse(n,c0[0,:],th[0][0],A[0][0],ar[0][0])
    V2=ellipse(n,c0[1,:],th[1][0],A[1][0],ar[1][0])
    dmax=0
    for i in range(n):
        d=sqrt((V2[i][0]-V1[i][0])**2+(V2[i][1]-V1[i][1])**2)
        if d>dmax:
            dmax=d
    return dmax

def voronoi(me,neigh,r,safe=0):
    """ Return the vertices of the Voronoi cell <r with the neigh around me, neigh is a list of (x,y) """
    """ safe is a safety distance """
    W=Polygon(Point(me).buffer(r))
    pm=Point2D(me)
    for n in neigh:
        pn=Point2D(n)
        v=pn-pm
        pc=pm+0.5*v
        v.r=1
        pc=pc-safe*v
        v.r=r
        q0=pn+2*v
        v.a = v.a+pi/2
        q1=pc+2*v
        q2=pc-2*v
        W -= Polygon([(q0.x,q0.y),(q1.x,q1.y),(q2.x,q2.y)])
    if type(W)==Polygon:
        return list(W.exterior.coords)
    else:
        return([])

def get_all_cc(graph):
    already_seen = set()
    result = []
    for node in graph:
        if node not in already_seen:
            cc, already_seen = get_cc(graph, node, already_seen)
            result.append(cc)
    return result

def get_cc(graph, node, already_seen):
        result = set([node])
        nodes2see = set([node])
        while nodes2see:
            node = nodes2see.pop()
            already_seen.add(node)
            nodes2see = nodes2see | graph[node] - already_seen
            result = result | graph[node]
        return result, already_seen

def largest_cc(graph):
    components=get_all_cc(graph)
    count=0
    while len(components):
        current=components.pop(0)
        if len(current)>count:
            largest=current
            count=len(largest)
    return largest

""" test get_all_cc
graph = { # a directed graph; when undirected it is necessary to have (i,j) and (j,i)
     0: {0, 1, 2, 3},
     1: set(),
     2: {1, 2},
     3: {3, 4, 5},
     4: {3, 4, 5},
     5: {3, 4, 5, 7}, 
     6: {6, 8},
     7: set(),
     8: {8, 9},
     9: set()}
for cc in get_all_cc(graph):
    ccg={}
    while cc:
        node=cc.pop()
        ccg[node]=graph[node]
    print(ccg)
components = get_all_cc(graph); print(components)
print(max([len(cc) for cc in components]))
print(largest_cc(graph))
# (For cc) The result is the same if directed, but undirected representation more useful / easier, e.g., who is connected to "me"?
"""

# Class to represent a (weighted undirected) graph to compute its MST
class WUGraph:
 
    def __init__(self,vertices):
        self.V= vertices # No. of vertices
        self.graph = [] # default list to store graph
         
  
    # function to add an edge to graph
    def addEdge(self,u,v,w):
        self.graph.append([u,v,w])
 
    # A utility function to find set of an element i
    # (uses path compression technique)
    def find(self, parent, i):
        if parent[i] == i:
            return i
        return self.find(parent, parent[i])
 
    # A function that does union of two sets of x and y
    # (uses union by rank)
    def union(self, parent, rank, x, y):
        xroot = self.find(parent, x)
        yroot = self.find(parent, y)
 
        # Attach smaller rank tree under root of high rank tree
        # (Union by Rank)
        if rank[xroot] < rank[yroot]:
            parent[xroot] = yroot
        elif rank[xroot] > rank[yroot]:
            parent[yroot] = xroot
        #If ranks are same, then make one as root and increment
        # its rank by one
        else :
            parent[yroot] = xroot
            rank[xroot] += 1
 
    # The main function to construct MST using Boruvska's algorithm
    # Should've been named Minimum Spanning FOREST since it's NOT assumed graph is connected
    def MST(self):
        result=[]
        parent = []; rank = []
 
        # An array to store index of the cheapest edge of
        # subset. It store [u,v,w] for each component
        cheapest =[]
 
        # Initially there are V different trees.
        # Finally there will be one tree that will be MST
        OneTree=False # numTrees = self.V
        MSTweight = 0
 
        # Create V subsets with single elements
        for node in range(self.V):
            parent.append(node)
            rank.append(0)
            cheapest =[-1] * self.V                
     
        # Keep combining components (or sets) until all
        # components are not combined into single MST

        while not OneTree: # numTrees > 1
            OneTree=True
            # Traverse through all edges and update
               # cheapest of every component
            for i in range(len(self.graph)):
 
                # Find components (or sets) of two corners
                # of current edge
                u,v,w =  self.graph[i]
                set1 = self.find(parent, u)
                set2 = self.find(parent ,v)
 
                # If two corners of current edge belong to
                # same set, ignore current edge. Else check if
                # current edge is closer to previous
                # cheapest edges of set1 and set2
                if set1 != set2:    
                     
                    if cheapest[set1] == -1 or cheapest[set1][2] > w :
                        cheapest[set1] = [u,v,w]
 
                    if cheapest[set2] == -1 or cheapest[set2][2] > w :
                        cheapest[set2] = [u,v,w]
 
            # Consider the above picked cheapest edges and add them
            # to MST
            for node in range(self.V):
 
                #Check if cheapest for current set exists
                if cheapest[node] != -1:
                    u,v,w = cheapest[node]
                    set1 = self.find(parent, u)
                    set2 = self.find(parent ,v)
 
                    if set1 != set2 :
                        MSTweight += w
                        self.union(parent, rank, set1, set2)
                        # print ("Edge %d-%d with weight %d included in MST" % (u,v,w))
                        result.append((u,v))
                        OneTree=False # numTrees = numTrees - 1
             
            #reset cheapest array
            cheapest =[-1] * self.V
        
        # print ("Weight of MST is %d" % MSTweight)  
        return result

""" test MST 
g = WUGraph(7)
g.addEdge(0, 1, 10)
g.addEdge(0, 2, 6)
g.addEdge(0, 3, 5)
g.addEdge(1, 3, 15)
g.addEdge(2, 3, 4)
g.addEdge(2, 3, 4)
g.addEdge(4, 5, 3)
g.addEdge(4, 6, 5)
g.addEdge(5, 6, 2)
mst=g.MST()
print(mst)
"""