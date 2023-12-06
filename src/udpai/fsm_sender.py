from .fsm import FSMState, Exit, TIMEOUT
from .packet import PacketType

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
        return packet, info

    def next_state(self, server, file, packet, info):
        return SendBuffer_S()

# ---------------------------------------------------------
class SendBuffer_S(FSMState):
    def act(self, server, file, packet, info):
        #send buffer slots that have not been sent or resend the one that needs to be
        return packet, info

    def next_state(self, server, file, packet, info):
        return WaitAck_S()

# ---------------------------------------------------------
class WaitAck_S(FSMState):
    def act(self, server, file, packet, info):
        #wait for ACK
        return packet, info

    def next_state(self, server, file, packet, info):
        #recieve ACK -> EmptyBuffer 
        return EmptyBuffer_S()

        #Timeout -> SendBuffer
        return SendBuffer_S()

# ---------------------------------------------------------
class EmptyBuffer_S(FSMState):
    def act(self, server, file, packet, info):
        return packet, info

    def next_state(self, server, file, packet, info):
        return SendEnd_S()
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
        
