#!/usr/bin/env bash

python3 receiver.py --local-ip="10.0.0.15" --local-port=5006 --remote-ip="172.24.125.199" --remote-port=5005 --file="test2.txt"
#python3 receiver.py --local-ip="172.24.125.199" --local-port=5006 --remote-ip="10.0.0.5" --remote-port=5005 --file="test2.txt"
