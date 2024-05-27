#!/usr/bin/python
# -*- coding: UTF-8 -*-
from simulator import Simulator
import argparse

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('--conn_file', dest='conn_file', type=str, help='Connection file path')
    parser.add_argument('--dir_file', dest='dir_file', type=str, help='Ip direction file path')
    parser.add_argument('--pos_file', dest='pos_file', type=str, help='Initial position file path')
    parser.add_argument('--shape_file', dest='shape_file', type=str, help='Shapes file path')
    parser.add_argument('--logs_file', dest='logs_file', type=str, help='Logs file path')
    
    args = parser.parse_args()
    
    simulator = Simulator(conn_file=args.conn_file, dir_file=args.dir_file, pos_file=args.pos_file, shape_file=args.shape_file, logs_file=args.logs_file)

    