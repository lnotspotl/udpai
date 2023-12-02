from . import server
from .packet import PacketType

TIMEOUT = 200  # ms

from abc import abstractmethod


class FSMState:
    def __init__(self):
        self.name = self.__class__.__name__

    @abstractmethod
    def act(self, server, file, packet):
        pass

    @abstractmethod
    def next_state(self, server, file, packet, info):
        pass


###--GLOBAL--#############################################
# ---------------------------------------------------------
class Exit(FSMState):
    def act(self, server, file, packet):
        print("Done!, See ya!")
        return None, ""

    def next_state(self, server, file, packet, info):
        pass


###--SENDER--#############################################
# ---------------------------------------------------------

class SendStart_S(FSMState):
    def act(self, server, file, packet):
        # send start packet
        info = ""
        return server.send_start(), info

    def next_state(self, server, file, packet, info):
        return AckStart_S()


# ---------------------------------------------------------
class AckStart_S(FSMState):
    def act(self, server, file, packet):
        # Wait StartAck
        info = ""
        return server.receive(TIMEOUT), info

    def next_state(self, server, file, packet, info):
        # Start timeout -> SendStart_S
        if packet is None:
            return SendStart_S()
        
        crc_ok = packet.check_crc()

        # Start CRC not ok -> SendStart_S
        if not crc_ok:
            return SendStart_S()

        # Start CRC ok -> SendMsg_S
        if crc_ok:
            return SendMsg_S()
        
        assert False, "Should not get here"

# ---------------------------------------------------------
class SendMsg_S(FSMState):
    def act(self, server, file, packet):
        file.ack()
        packet = file.next()
        if packet is not None:
            server.send(packet)
            info = "msg"
        else:
            server.send_stop()
            info = "eof"
        return packet, info

    def next_state(self, server, file, packet, info):
        if info == "msg":
            return WaitAck_S()
        elif info == "eof":
            return SendEnd_S()
        
        assert False, "Unknown info"

# ---------------------------------------------------------
class WaitAck_S(FSMState):
    def act(self, server, file, packet):
        # wait Msg Ack
        info = ""
        return server.receive(TIMEOUT), info

    def next_state(self, server, file, packet, info):
        # Timeout -> SendAgain_S
        if packet is None:
            return SendAgain_S()
        
        crc_ok = packet.check_crc()

        # Msg CRC not ok -> SendAgain_S
        if not crc_ok:
            return SendAgain_S()

        # Msg CRC ok -> SendMsg_S
        if crc_ok:
            return SendMsg_S()
        
        assert False, "Should not get here"


# ---------------------------------------------------------
class SendAgain_S(FSMState):
    def act(self, server, file, packet):
        # send the same packet again
        info = ""
        packet = file.next()
        server.send(packet), info

    def next_state(self, server, file, packet, info):
        return WaitAck_S()


# ---------------------------------------------------------
class SendEnd_S(FSMState):
    def act(self, server, file, packet):
        info = ""
        server.send_stop(), info

    def next_state(self, server, file, packet, info):
        return WaitAckEnd_S()


# ---------------------------------------------------------
class WaitAckEnd_S(FSMState):
    def act(self, server, file, packet):
        info = ""
        return server.receive(TIMEOUT), info

    def next_state(self, server, file, packet, info):
        # Timeout -> SendEnd_S
        if packet is None:
            return SendEnd_S()
        
        crc_ok = packet.check_crc()

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
    def act(self, server, file, packet):
        packet = server.receive()
        assert packet.type == PacketType.START
        crc_ok = packet.check_crc()
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
    def act(self, server, file, packet):
        packet = server.receive()
        crc_ok = packet.check_crc()
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
