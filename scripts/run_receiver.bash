#!/usr/bin/env bash

python3 receiver.py --local-ip="10.0.0.50" --local-port=5006 --remote-ip="10.0.0.3" --remote-port=5005 --file="TEST.b"
#python3 receiver.py --local-ip="172.24.125.199" --local-port=5006 --remote-ip="10.0.0.5" --remote-port=5005 --file="test2.txt"
