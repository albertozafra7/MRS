from multiprocessing import Process, Value, Array, Lock
import numpy as np
import time     # import the time library for the timestamp
from datetime import datetime
import xmlrpc.client
import utils as ut
import matplotlib
import matplotlib.pyplot as plt
import random
import subprocess

srv = xmlrpc.client.Server("http://155.210.154.192:60000")
print("connected")
q = np.array(srv.RPC_get_positions())
print("q",q)