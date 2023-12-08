#!/usr/bin/env python3

from udpai.utils import parse_args, print_args
from udpai.server import Server
from udpai.file import File
from udpai.fsm_receiver import WaitStart_R
from udpai.fsm_buffer import ReceiverBuffer, BUFFER_SIZE
import time
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
info = dict()
info["buffer"] = ReceiverBuffer(capacity=BUFFER_SIZE)
time_start = time.time()

while state.name != "Exit":
    packet, info = state.act(server, file, packet, info)
    state = state.next_state(server, file, packet, info)

print("Done receiver!")
time_stop = time.time()
print("cas: ", time_stop-time_start)
