from .fsm import FSMState, Exit, TIMEOUT
from .packet import PacketType, Packet


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
        packet = server.receive(TIMEOUT)   
        buffer = info["buffer"]

        # timeout or crc not ok
        if packet is None or not packet.check():
            info["status"] = "timeout"
            packet = Packet(PacketType.ACK, 0, b"",packet_id=buffer.next_id)
            server.send(packet)
            return packet
        

        if packet.type == PacketType.STOP:
            info["status"] = "stop"
            return packet, None
        
        assert packet.type == PacketType.DATA
        info["status"] = "data"
        buffer.process_packet(packet, file)
        
        return packet, None

    def next_state(self, server, file, packet, info):
        status = info["status"]
        if status == "timeout":
            return FillBuffer_R()
        
        if status == "stop":
            return AckEnd_R()
        
        assert status == "data"

        return Write_R()


# ---------------------------------------------------------
class Write_R(FSMState):
    def act(self, server, file, packet, info):
        buffer = info["buffer"]
        next_id = buffer.write_to_file(file)

        packet = Packet(PacketType.ACK, 0, b"", packet_id=next_id)
        server.send(packet)

        return packet, None

    def next_state(self, server, file, packet, info):
        return FillBuffer_R()


# ---------------------------------------------------------
class AckEnd_R(FSMState):
    def act(self, server, file, packet, info):
        crc_ok = packet.check()
        packet = server.send_ack(crc_ok)
        return packet, None

    def next_state(self, server, file, packet, info):
        return Exit()
