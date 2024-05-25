import argparse
import utils as ut
import Communication as comm


parser = argparse.ArgumentParser()
parser.add_argument('--conns', dest='connsF', type=str, help='Connections of the nodes')
parser.add_argument('--dirs', dest='dirsF', type=str, help='IP directions')
parser.add_argument('--id', dest='id', type=int, help='Your gobal ID')

args = parser.parse_args()

id = args.id

# Open connections file (with error handling)
try:
    with open(args.connsF, 'r') as connections_file:
        connections = connections_file.readlines()
except FileNotFoundError:
    raise FileNotFoundError(f"Connections file not found: {args.connsF}")
# Open directions file (with error handling)
try:
    with open(args.dirsF, 'r') as directions_file:
        directions = directions_file.readlines()
except FileNotFoundError:
    raise FileNotFoundError(f"Directions file not found: {args.dirsF}")

nL = ut.numLocalRobs(id,connections)
nG = ut.numGroups(connections)
port = ut.readPort(id,directions)
dirs = ut.read_directions(id,connections,directions)


com = comm.Communication(nL, nG, "127.0.0.1", port, dirs)

input()
# com.get_positions()

# print("2: ",dirs[1].port)

#--> jabasnbas.txt
#        local_id, global_id, id1, id2, id3

#--> ips.txt
#   1 jhdafjdas
#   2 kfdajfklasd