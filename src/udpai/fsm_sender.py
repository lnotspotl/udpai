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
        buffer = info["buffer"]

        buffer.fill_buffer(file)

        #fill buffer slots that are None with next packets up to N_PACKETS
        return packet, info

    def next_state(self, server, file, packet, info):
        return SendBuffer_S()

# ---------------------------------------------------------
class SendBuffer_S(FSMState):
    def act(self, server, file, packet, info):
        buffer = info["buffer"]

        # buffer is empty, no more data to send
        if buffer.empty():
            info["status"] = "empty"
            return packet, info
        
        # buffer is not empty, send buffer
        info["status"] = "not_empty"
        buffer.send_buffer(server)

        #send buffer slots that have not been sent or resend the one that needs to be
        return packet, info

    def next_state(self, server, file, packet, info):
        status = info["status"]

        if status == "empty":
            return SendEnd_S()

        return WaitAck_S()

# ---------------------------------------------------------
class WaitAck_S(FSMState):
    def act(self, server, file, packet, info):
        packet = server.receive()
        assert packet.type == PacketType.ACK

        crc_ok = packet.check()
        if not crc_ok:
            info["status"] = "crc_not_ok"
            return packet, info
        
        buffer = info["buffer"]
        buffer.process_ack(packet)

        return packet, info

    def next_state(self, server, file, packet, info):

        status = info["status"]

        if status == "crc_not_ok":
            return WaitAck_S()
        
        return SendBuffer_S()

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
        
