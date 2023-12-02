#!/usr/bin/env bash

python3 receiver.py \
 --local-ip="10.0.0.80" \ 
 --local-port=5005 \
 --remote-ip="10.0.0.81" \
 --remote-port=5005 \
 --file="test2.txt"