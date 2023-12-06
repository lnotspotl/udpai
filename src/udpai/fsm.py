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
        return server.send_start(), info

    def next_state(self, server, file, packet, info):
        return WaitAckStart_S()

# ---------------------------------------------------------
class WaitAckStart_S(FSMState):
    def act(self, server, file, packet, info):
        return server.receive(TIMEOUT), info

    def next_state(self, server, file, packet, info):
        if packet is None:
            return SendStart_S()
        
        crc_ok = packet.check()

        # Start CRC not ok -> SendStart_S
        if not crc_ok:
            return SendStart_S()

        # Start CRC ok -> FillBuffer_S
        if crc_ok:
            return FillBuffer_S()
        
        assert False, "Should not get here"
        
# ---------------------------------------------------------
class FillBuffer_S(FSMState):
    def act(self, server, file, packet, info):
        #fill buffer slots that are None with next packets up to N_PACKETS
        return 

    def next_state(self, server, file, packet, info):
        return SendBuffer_S()

# ---------------------------------------------------------
class SendBuffer_S(FSMState):
    def act(self, server, file, packet, info):
        #send buffer slots that have not been sent or resend the one that needs to be
        return

    def next_state(self, server, file, packet, info):
        return WaitAck_S()

# ---------------------------------------------------------
class WaitAck_S(FSMState):
    def act(self, server, file, packet, info):
        #wait for ACK
        return

    def next_state(self, server, file, packet, info):
        #recieve ACK -> EmptyBuffer 
        return EmptyBuffer_S()

        #Timeout -> SendBuffer
        return SendBuffer_S()

# ---------------------------------------------------------
class EmptyBuffer_S(FSMState):
    def act(self, server, file, packet, info):
        
        return

    def next_state(self, server, file, packet, info):
        return FillBuffer_S()

# ---------------------------------------------------------
class SendEnd_S(FSMState):
    def act(self, server, file, packet, info):
        return server.send_stop(), info

    def next_state(self, server, file, packet, info):
        
        return WaitAckEnd_S()

# ---------------------------------------------------------
class WaitAckEnd_S(FSMState):
    def act(self, server, file, packet, info):
        return server.receive(TIMEOUT), info

    def next_state(self, server, file, packet, info):
        # Timeout -> SendEnd_S
        if packet is None:
            return SendEnd_S()
        
        crc_ok = packet.check()

        # End CRC not ok -> SendEnd_S
        if not crc_ok:
            return SendEnd_S()

        # End CRC ok -> SendEnd_S
        if crc_ok:
            return Exit()
        
        assert False, "Should not get here"
        

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
            return FillBuffer_R()
        elif info == "crc_not_ok":
            return WaitStart_R()
    
        assert False, "Unknown info"

# ---------------------------------------------------------
class WaitStart_R(FSMState):
    def act(self, server, file, packet, info):
        return None, None

    def next_state(self, server, file, packet, info):
        return FillBuffer_R()

# ---------------------------------------------------------
class FillBuffer_R(FSMState):
    def act(self, server, file, packet, info):
        return None, None

    def next_state(self, server, file, packet, info):
        if packet.type == PacketType.STOP:
            return AckEnd_R()
        return Write_R()

# ---------------------------------------------------------
class Write_R(FSMState):
    def act(self, server, file, packet, info):
        return None, None

    def next_state(self, server, file, packet, info):
        return FillBuffer_R()

# ---------------------------------------------------------
class AckEnd_R(FSMState):
    def act(self, server, file, packet, info):
        return None, None

    def next_state(self, server, file, packet, info):
        return Exit()


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
