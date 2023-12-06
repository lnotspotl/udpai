#!/usr/bin/env python3

from udpai.utils import parse_args, print_args
from udpai.server import Server
from udpai.file import File
from udpai.fsm_sender import SendStart_S
from udpai.fsm_buffer import SenderBuffer

args = parse_args()
print_args(args)

# load file
file = File(args.file, write=False)

# create server
server = Server(
    local_ip=args.local_ip,
    local_port = args.local_port,
    remote_ip=args.remote_ip,
    remote_port=args.remote_port
)

# create FSM
packet = None
state = SendStart_S()
info = dict()
info["buffer"] = SenderBuffer(capacity=5)

while state.name != "Exit":
    print(state.name)
    packet, info = state.act(server, file, packet, info)
    print(packet)
    state = state.next_state(server, file, packet, info)

print("Done sender!")
