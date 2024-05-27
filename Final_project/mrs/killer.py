import argparse
import utils as ut
import xmlrpc.client

parser = argparse.ArgumentParser()
parser.add_argument('--dirs', dest='dirsF', type=str, help='IP directions')
args = parser.parse_args()

# Open directions file (with error handling)
try:
    with open(args.dirsF, 'r') as directions_file:
        directions = directions_file.readlines()
except FileNotFoundError:
    raise FileNotFoundError(f"Directions file not found: {args.dirsF}")

ips = ut.readIPs(directions)

for ip in ips:
    print("Killing: ",ip.host,":",str(ip.port))
    try:
        srv = xmlrpc.client.Server("http://"+ip.host+":"+str(ip.port))
        ack = srv.RPC_finish()
        if ack == "ACK":
            print("Killed")
    except Exception as e:
        print(e)