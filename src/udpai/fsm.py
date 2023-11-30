from enum import Enum
from multiprocessing.connection import wait
from nis import match
from unittest import case
#packet.type.value

def tprint(state, next_state):
    print("Aktuální stav je: " + state, "Přeházím do stavu: " + next_state)

class state_sender(Enum):
    START = 0
    WAIT_ACK = 1
    SEND_PACKET = 2
    END = 3

class fsm_sender:
    def __init__(self, state: state_sender):
        self.state = state

    def move_next_state(self, packet):
        if self.state == state_sender.START:
            #DO TO: send start msg
            tprint(self.state, state_sender.WAIT_ACK)
            self.state = state_sender.WAIT_ACK

        elif self.state == state_sender.WAIT_ACK:
            next_state = state_sender

            #DO TO: recieved ACK
            next_state = state_sender.SEND_PACKET

            #DO TO: was supposed to recieve START_ACK but did not (time ran out)
            next_state = state_sender.START

            #DO TO: recieve end akc
            next_state = state_sender.END

            tprint(self.state, next_state)
            self.state = next_state

        elif self.state == state_sender.SEND_PACKET:
            #DO TO: send start msg
            self.state = state_sender.WAIT_ACK
            tprint(self.state, state_sender.WAIT_ACK)

        elif self.state == state_sender.END:
            tprint(self.state, "KONEEEEEE")
            exit()


class state_reciever(Enum):
    WAIT_START = 0
    SEND_ACK = 1
    WAIT_MSG = 2

class fsm_reciever:
    def __init__(self, state: state_reciever):
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
            
                

            
