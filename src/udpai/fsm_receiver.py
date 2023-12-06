from .fsm import FSMState, Exit, TIMEOUT
from .packet import PacketType


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
