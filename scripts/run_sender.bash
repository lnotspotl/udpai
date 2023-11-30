#!/usr/bin/env bash

python3 sender.py --local-ip="10.0.0.80" --local-port=5005 --remote-ip="10.0.0.80" --remote-port=5005\
    --file="test.txt"