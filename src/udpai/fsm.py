from enum import Enum
from multiprocessing.connection import wait
from nis import match
from unittest import case

from packet import Packet, PacketType
#packet.type.value

TIMEOUT = 200 # ms

def tprint(state, next_state):
    print("Aktuální stav je: " + state, "Přeházím do stavu: " + next_state)

class FSM:
    def __init__(self, server, file):
        self.server = server
        self.file = file

class state_sender(Enum):
    SEND_START = 0
    WAIT_ACK = 1
    SEND_PACKET = 2
    SEND_STOP = 3
    END = 4

class fsm_sender(FSM):
    def __init__(self, server, file, state: state_sender):
        super().__init__(server, file)
        self.state = state
        self.last_state = state

    def move_next_state(self, packet):
        last_state = self.state

        if self.state == state_sender.SEND_START:
            self.server.send_start()
            tprint(self.state, state_sender.WAIT_ACK)
            self.state = state_sender.WAIT_ACK

        elif self.state == state_sender.WAIT_ACK:
            packet = self.server.receive(TIMEOUT)

            if packet is None and self.last_state == state_sender.SEND_START:
                tprint(self.state, state_sender.SEND_START)
                self.state = state_sender.SEND_START

            if packet is None and self.last_state == state_sender.SEND_PACKET:
                tprint(self.state, state_sender.SEND_PACKET)
                self.state = state_sender.SEND_PACKET

            if packet is None and self.last_state == state_sender.SEND_STOP:
                tprint(self.state, state_sender.SEND_STOP)
                self.state = state_sender.SEND_STOP
            
            if packet is not None and packet.type == PacketType.ACK and self.last_state == state_sender.SEND_PACKET:
                tprint(self.state, state_sender.SEND_PACKET)
                self.state = state_sender.SEND_PACKET

            if packet is not None and packet.type == PacketType.ACK and self.last_state == state_sender.SEND_STOP:
                tprint(self.state, state_sender.END)
                self.state = state_sender.END

            #DO TO: recieve end akc
            next_state = state_sender.END

            tprint(self.state, next_state)
            self.state = next_state

        elif self.state == state_sender.SEND_PACKET:
            try:
                packet = self.file.next()
                self.server.send(packet)
                self.state = state_sender.WAIT_ACK
            except StopIteration:

            tprint(self.state, state_sender.WAIT_ACK)

        elif self.state == state_sender.END:
            tprint(self.state, "KONEEEEEE")
            exit()
        self.last_state = last_state

class state_reciever(Enum):
    WAIT_START = 0
    SEND_ACK = 1
    WAIT_MSG = 2

class fsm_reciever(FSM):
    def __init__(self, server, file, state: state_reciever):
        super().__init__(server, file)
        self.state = state

    def move_next_state(self, packet):
        if self.state == state_reciever.WAIT_START:
            #DO TO: wait till start msg is recieved
            tprint(self.state, state_reciever.SEND_ACK)
            self.state = state_reciever.SEND_ACK

        elif self.state == state_reciever.SEND_ACK:
            #DO TO: send ack msg
            self.state = state_reciever.WAIT_MSG
            tprint(self.state, state_reciever.WAIT_MSG)

        elif self.state == state_reciever.WAIT_MSG:
            #TO DO: wait till msg is recieved
            #msg is not end msg
                tprint(self.state, state_reciever.SEND_ACK)
                self.state = state_reciever.SEND_ACK
            #msg is end msg
                #exit()
            
                

            
