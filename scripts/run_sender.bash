#!/usr/bin/env bash

python3 sender.py --local-ip="172.24.125.199" --local-port=5005 --remote-ip="10.0.0.15" --remote-port=5006 --file="test.txt"
#python3 sender.py --local-ip="10.0.0.15" --local-port=5005 --remote-ip="172.24.125.199" --remote-port=5006 --file="test.txt"
