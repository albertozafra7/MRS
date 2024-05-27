
import numpy as np

class IPadress:
    def __init__(self, host, port):
        self.host = host
        self.port = port
    
def readIPs(directions):
    # Create directions list with host and port information

    dirs = []
    for dir in directions:
        host, port = dir.strip().split(':')
        dirs.append(IPadress(host,int(port)))
    return dirs

def read_directions(id,connections,directions):
    """
    Reads connections from connsF where global_id = id.
    Each line of connsF looks like this:
      universal_id, local_id, group_id, uid1, uid2, uid3...
    
    id1, id2, id3: global ids of robots that are communicated with the robot
    with universal id == universal_id
    
    After knowing the ids of the communicated robots. It reads the IP
    addreses from dirsF. Where the address of the N robot is in the N line.
    
    Returns an array "dirs" where each element has 2 fields: host and port.
    """

    # Find lines in connections file matching the robot's global ID
    for line in connections:
        line_data = line.strip().split(',')
        if line_data[0] == str(id):
            break

    # Extract communicated robot IDs
    communicated_ids = [int(data) for data in line_data[3:]]

    # Create directions list with host and port information
    dirs = []
    for i, communicated_id in enumerate(communicated_ids):
        if communicated_id >= len(directions):
            raise ValueError(f"Not enough entries in directions file for robot {id}")
        host, port = directions[communicated_id].strip().split(':')
        dirs.append(IPadress(host,int(port)))
    return dirs
    

def numLocalRobs(id,connections):
    
    line_data = connections[id].strip().split(',')
    group = line_data[2]
    
    nL = 0
    for line in connections:
        line_data = line.strip().split(',')
        if line_data[2] == group:
            nL = nL+1
    return nL

def numRobsInGroup(idG,connections):
    
    nL = 0
    for line in connections:
        line_data = line.strip().split(',')
        if int(line_data[2]) == idG:
            nL = nL+1
    return nL

def numGroups(connections):
    
    nG = 0
    for line in connections:
        line_data = line.strip().split(',')
        if int(line_data[2])>nG:
            nG=int(line_data[2])
    return nG+1

def readGroup(id,connections):
    
    line_data = connections[id].strip().split(',')
    return int(line_data[2])
            
def readIP(id,directions):
    
    host, port = directions[id].strip().split(':')
    return host

def readPort(id,directions):
    
    host, port = directions[id].strip().split(':')
    return int(port)

def readInitialPosition(id,positions):
    initial_pos = np.zeros(2)

    for line in positions:
        line_data = line.strip().split(',')
        if int(line_data[0]) == id:
            initial_pos[0] = float(line_data[1])
            initial_pos[1] = float(line_data[2])
            break

    return initial_pos

def readIntialPositions(positions):
    poses = []

    for line in positions:
        initial_pos = np.zeros(2)
        line_data = line.strip().split(',')
        initial_pos[0] = float(line_data[1])
        initial_pos[1] = float(line_data[2])
        poses.append(initial_pos)

    return np.array(poses)

def readShape(shapes):
    sh = []
    
    for line in shapes:
        line_data = line.strip().split(',')
        sh.append(line_data[0])
    
    return sh

def readRotations(shapes):
    rotations = []
    
    for line in shapes:
        line_data = line.strip().split(',')
        rotations.append(bool(line_data[1]))

    return rotations