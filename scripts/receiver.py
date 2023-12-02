#!/usr/bin/env python3

from udpai.utils import parse_args, print_args
from udpai.server import Server
from udpai.file import File
from udpai.fsm import WaitStart_R

args = parse_args()
print_args(args)

file = File(args.file, write=True)

# create server
server = Server(
    local_ip=args.local_ip,
    local_port = args.local_port,
    remote_ip=args.remote_ip,
    remote_port=args.remote_port
)

# create FSM
packet = None
state = WaitStart_R()
info = ""

while state.name != "Exit":
    print(state.name)
    packet, info = state.act(server, file, packet)
    print(packet.type)
    state = state.next_state(server, file, packet, info)

print("Done receiver!")
