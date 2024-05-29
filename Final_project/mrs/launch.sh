#!/bin/bash
: > ./logs/logs.txt
python3 ./main.py --conn_file=./params/connections.txt --dir_file=./params/ips.txt --pos_file=./params/initial_poses.txt --shape_file=./params/shapes.txt --logs_file=./logs/logs.txt > output.txt