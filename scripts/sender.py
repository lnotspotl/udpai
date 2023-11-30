#!/usr/bin/env python3

from udpai.utils import parse_args, print_args
from udpai.server import Server
from udpai.file import File

args = parse_args()
print_args(args)

# load file
file = File(args.file, write=False)

# create server
server = Server(
    local_ip=args.remote_ip,
    local_port = args.remote_port,
    remote_ip=args.local_ip,
    remote_port=args.local_port
)

# create FSM

# fsm.run()

print("Done sender!")