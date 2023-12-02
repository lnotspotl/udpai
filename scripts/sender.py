#!/usr/bin/env python3

from udpai.utils import parse_args, print_args
from udpai.server import Server
from udpai.file import File
from udpai.fsm import SendStart_S

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
packet = None
state = SendStart_S()
info = ""

while state.name != "Exit":
    packet, info = state.act(server, file, packet)
    state = state.next_state(server, file, packet, info)

print("Done sender!")