from .fsm import FSMState, Exit, TIMEOUT
from .packet import PacketType, Packet

RECEIVE_TIMEOUT = 10 # ms


###--RECIEVER--###########################################
# ---------------------------------------------------------
class WaitStart_R(FSMState):
    def act(self, server, file, packet, info):
        packet = server.receive()
        assert packet.type == PacketType.START
        crc_ok = packet.check()
        print("CRC ok:", crc_ok)
        server.send_ack(crc_ok=crc_ok)
        info["status"] = "crc_ok" if crc_ok else "crc_not_ok"
        return packet, info

    def next_state(self, server, file, packet, info):
        status = info["status"]
        if status == "crc_ok":
            return FillBuffer_R()
        elif status == "crc_not_ok":
            return WaitStart_R()

        assert False, "Unknown info"

# ---------------------------------------------------------
class FillBuffer_R(FSMState):
    def act(self, server, file, packet, info):
        packet = server.receive(RECEIVE_TIMEOUT)   

        # timeout 
        if packet is None:
            info["status"] = "timeout"
            next_id = info["buffer"].next_id
            ack_packet = Packet(PacketType.ACK, 0, b"", packet_id=next_id)
            server.send(ack_packet)
            return packet, info
        
        if packet.type == PacketType.STOP and packet.check():
            info["status"] = "stop"
            return packet, info
        
        buffer = info["buffer"]
        buffer.insert_packet(packet)
        info["status"] = "buffer_full" if buffer.full() else "fill"
        
        return packet, info

    def next_state(self, server, file, packet, info):
        status = info["status"]
        if status == "timeout" or status == "buffer_full":
            return EmptyBuffer_R()
        
        if status == "stop":
            return AckEnd_R()
        
        assert status == "fill"
        
        return FillBuffer_R()

# ---------------------------------------------------------
class EmptyBuffer_R(FSMState):
    def act(self, server, file, packet, info):
        buffer = info["buffer"]
        next_id = buffer.empty_buffer()
        packet = Packet(PacketType.ACK, 0, b"", packet_id=next_id)
        packet = server.send(packet)
        return packet, info
    
    def next_state(self, server, file, packet, info):
        return FillBuffer_R()


# ---------------------------------------------------------
class AckEnd_R(FSMState):
    def act(self, server, file, packet, info):
        crc_ok = packet.check()
        packet = server.send_ack(crc_ok)
        return packet, info

    def next_state(self, server, file, packet, info):
        return Exit()
