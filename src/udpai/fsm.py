from array import array
from tkinter import Pack
from . import server
from .packet import PacketType

TIMEOUT = 1000  # ms
N_PACKETS = 5


    
from abc import abstractmethod


class FSMState:
    def __init__(self):
        self.name = self.__class__.__name__

    @abstractmethod
    def act(self, server, file, packet, info):
        pass

    @abstractmethod
    def next_state(self, server, file, packet, info):
        pass


###--GLOBAL--#############################################
# ---------------------------------------------------------
class Exit(FSMState):
    def act(self, server, file, packet, info):

        print("Done!, See ya!")
        return None, ""

    def next_state(self, server, file, packet, info):
        pass


###--SENDER--##############################################
# ---------------------------------------------------------
class SendStart_S(FSMState):
    def act(self, server, file, packet, info):

        return

    def next_state(self, server, file, packet, info):

        return WaitAckStart_S

# ---------------------------------------------------------
class WaitAckStart_S(FSMState):
    def act(self, server, file, packet, info):
        return

    def next_state(self, server, file, packet, info):

        return FillBuffer_S

        return SendStart_S
        
# ---------------------------------------------------------
class FillBuffer_S(FSMState):
    def act(self, server, file, packet, info):
        #fill buffer slots that are None with next packets up to N_PACKETS
        return

    def next_state(self, server, file, packet, info):
        return SendBuffer_S

# ---------------------------------------------------------
class SendBuffer_S(FSMState):
    def act(self, server, file, packet, info):
        #send buffer slots that have not been sent or resend the one that needs to be
        return

    def next_state(self, server, file, packet, info):
        return WaitAck_S

# ---------------------------------------------------------
class WaitAck_S(FSMState):
    def act(self, server, file, packet, info):
        #wait for ACK
        return

    def next_state(self, server, file, packet, info):
        #recieve ACK -> EmptyBuffer 
        return EmptyBuffer_S

        #Timeout -> SendBuffer
        return SendBuffer_S

# ---------------------------------------------------------
class EmptyBuffer_S(FSMState):
    def act(self, server, file, packet, info):
        
        return

    def next_state(self, server, file, packet, info):
        return FillBuffer_S

# ---------------------------------------------------------
class SendEnd_S(FSMState):
    def act(self, server, file, packet, info):
        return

    def next_state(self, server, file, packet, info):
        
        return WaitAckEnd_S 

# ---------------------------------------------------------
class WaitAckEnd_S(FSMState):
    def act(self, server, file, packet, info):
        return

    def next_state(self, server, file, packet, info):
        return Exit
        return SendEnd_S
        

###--RECIEVER--###########################################
# ---------------------------------------------------------
class WaitStart_R(FSMState):
    def act(self, server, file, packet, info):

        packet = server.receive()
        assert packet.type == PacketType.START
        crc_ok = packet.check()
        print("CRC ok:", crc_ok)
        server.send_ack(crc_ok=crc_ok)
        info = "crc_ok" if crc_ok else "crc_not_ok"
        return packet, info

    def next_state(self, server, file, packet, info):
        if info == "crc_ok":
            return WaitMsg_R()
        elif info == "crc_not_ok":
            return WaitStart_R()
    
        assert False, "Unknown info"

# ---------------------------------------------------------
class WaitMsg_R(FSMState):
    def act(self, server, file, packet, info):

        packet = server.receive()
        crc_ok = packet.check()
        server.send_ack(crc_ok=crc_ok)

        if crc_ok and packet.type == PacketType.DATA:
            file.write_packet(packet)

        info = "crc_ok" if crc_ok else "crc_not_ok"

        return packet, info

    def next_state(self, server, file, packet, info):
        if info == "crc_nok":
            return WaitMsg_R()
        
        assert info == "crc_ok", "Unknown info"

        if packet.type == PacketType.DATA:
            return WaitMsg_R()
        elif packet.type == PacketType.STOP:
            return Exit()
        elif packet.type == PacketType.START:
            return WaitMsg_R()
        
        assert False, "Unknown packet type"

if __name__ == "__main__":
    server = "server"
    file = "File"
    packet = None
    state = SendStart_S()
    info = ""

    while state.name != "Exit":
        print(state.name)
        packet, info = state.act(server, file, packet)
        state = state.next_state(server, file, packet, info)
