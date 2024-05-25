from agent import agent
import argparse
import utils as ut
import Communication as comm
import numpy as np

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('--nL', dest='nL', type=int, help='Connections of the nodes')
    parser.add_argument('--nG', dest='nG', type=int, help='Number of goups')
    parser.add_argument('--uid', dest='uid', type=int, help='Your universal ID')
    parser.add_argument('--idL', dest='idL', type=int, help='Your local ID')
    parser.add_argument('--qx', dest='qx', type=float, help='Initial x local pose')
    parser.add_argument('--qy', dest='qy', type=float, help='Initial y local pose')
    parser.add_argument('--shapeL', dest='shapeL', type=str, help='Local shape formation')
    parser.add_argument('--idG', dest='idG', type=int, help='Your Group ID')
    parser.add_argument('--qGx', dest='qGx', type=float, help='Initial x group pose')
    parser.add_argument('--qGy', dest='qGy', type=float, help='Initial y group pose')
    parser.add_argument('--shapeG', dest='shapeG', type=str, help='Local shape formation')
    parser.add_argument('--qTx', dest='qTx', type=float, help='Initial x target pose')
    parser.add_argument('--qTy', dest='qTy', type=float, help='Initial y target pose')
    parser.add_argument('--dirsF', dest='dirsF', type=str, help='Directions file path')
    parser.add_argument('--connF', dest='connF', type=str, help='Communications file path')
    parser.add_argument('--rotationL', dest='rotationL', type=bool, help='If the local formation rotation is enabled')
    parser.add_argument('--rotationG', dest='rotationG', type=bool, help='If the local formation rotation is enabled')
    

    args = parser.parse_args()

    # Open connections file (with error handling)
    try:
        with open(args.connF, 'r') as connections_file:
            connections = connections_file.readlines()
    except FileNotFoundError:
        raise FileNotFoundError(f"Connections file not found: {args.connsF}")
    # Open directions file (with error handling)
    try:
        with open(args.dirsF, 'r') as directions_file:
            directions = directions_file.readlines()
    except FileNotFoundError:
        raise FileNotFoundError(f"Directions file not found: {args.dirsF}")

    a = agent(num_robots=args.nL, num_groups=args.nG, uid=args.uid, idL=args.idL, initial_poseL=np.array([args.qx,args.qy]), shapeL=args.shapeL, idG=args.idG, initial_poseG=np.array([args.qGx,args.qGy]), shapeG=args.shapeG, initial_poseT=np.array([args.qTx,args.qTy]), dir_file=directions, comm_file=connections, rotationL=args.rotationL, rotationG=args.rotationG)
    
    print("Exiting...")