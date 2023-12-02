from . import server
from . packet import PacketType

TIMEOUT = 200 # ms

from abc import abstractmethod
        
class FSMState:
    def __init__(self):
        self.name = self.__class__.__name__

    @abstractmethod
    def act(self, server, file, packet):
        pass

    @abstractmethod
    def next_state(self, server, file, packet):
        pass

###--GLOBAL--#############################################
#---------------------------------------------------------
class Exit(FSMState):
    def act(self, server, file, packet):
        pass #exit()  ???

    def next_state(self, server, file, packet):
        pass

###--SENDER--#############################################
#---------------------------------------------------------
class AckStart_S(FSMState):
    def act(self, server, file, packet):
        #Wait StartAck
        return server.receive(TIMEOUT)

    def next_state(self, server, file, packet):
        #Start timeout -> SendStart_S
        if packet is None:
            return SendStart_S()

        #Start CRC not ok -> SendStart_S
        if not packet.check_crc():
            return SendStart_S()

        #Start CRC ok -> SendMsg_S
        if packet.check_crc():
            return SendMsg_S()

#---------------------------------------------------------
class SendStart_S(FSMState):
    def act(self, server, file, packet):
        #send start packet
        return server.send_start()

    def next_state(self, server, file, packet):
        return AckStart_S()

#---------------------------------------------------------
class SendMsg_S(FSMState):
    def act(self, server, file, packet):
        #TO DO
        #Try to send msg
        pass

    def next_state(self, server, file, packet):
        #TO DO
        #There is nothing to send -> SendEnd_S

        #Msg sent -> WaitAck_S

        pass

#---------------------------------------------------------
class WaitAck_S(FSMState):
    def act(self, server, file, packet):
        #wait Msg Ack
        return server.receive(TIMEOUT)

    def next_state(self, server, file, packet):
        #Timeout -> SendAgain_S
        if packet is None:
            return SendAgain_S()

        #Msg CRC not ok -> SendAgain_S
        if not packet.check_crc():
            return SendAgain_S()

        #Msg CRC ok -> SendMsg_S
        if packet.check_crc():
            return SendMsg_S()

#---------------------------------------------------------
class SendAgain_S(FSMState):
    def act(self, server, file, packet):
        #send the same packet again
        server.send(packet)

    def next_state(self, server, file, packet):
        return WaitAck_S()

#---------------------------------------------------------
class SendEnd_S(FSMState):
    def act(self, server, file, packet):
        #send stop packet
        server.send_stop()

    def next_state(self, server, file, packet):
        return WaitAckEnd_S()

#---------------------------------------------------------
class WaitAckEnd_S(FSMState):
    def act(self, server, file, packet):
        #wait End Ack
        return server.receive(TIMEOUT)

    def next_state(self, server, file, packet):
        #Timeout -> SendEnd_S
        if packet is None:
            return SendEnd_S()

        #End CRC not ok -> SendEnd_S
        if not packet.check_crc():
            return SendEnd_S()

        #End CRC ok -> SendEnd_S
        if packet.check_crc():
            return Exit()

###--RECIEVER--###########################################
#---------------------------------------------------------
class WaitStart_R(FSMState):
    def act(self, server, file, packet):
        #wait Start msg
        return server.receive()

    def next_state(self, server, file, packet):
        #TO DO
        #Start CRC wrong -> WaitStart_S + send CRC wrong

        #Start CRC ok -> WaitMsg_R
        if packet.check_crc():
            return WaitMsg_R

#---------------------------------------------------------
class WaitMsg_R(FSMState):
    def act(self, server, file, packet):
        #wait msg
        return server.receive()

    def next_state(self, server, file, packet):
        #Msg CRC not ok -> SendMsgAckCrcWrong
        if not packet.check_crc():
            return SendMsgAckCrcWrong_R()

        #End CRC ok -> SendEnd_S
        if packet.check_crc():
            return SendMsgAck_R()

#---------------------------------------------------------
class SendMsgAck_R(FSMState):
    def act(self, server, file, packet):
        #send Ack
        server.send_ack(crc_ok = packet.check_crc())
        return packet

    def next_state(self, server, file, packet):
        #packet type is DATA -> WaitMsg_R
        if packet.type.value == PacketType.DATA:
            return WaitMsg_R()
        
        #packet type is STOP -> Exit + send ack
        if packet.type.value == PacketType.STOP:
            server.send_ack()
            return Exit()

#---------------------------------------------------------
class SendMsgAckCrcWrong_R(FSMState):
    def act(self, server, file, packet):
        #TO DO:
        #send ack is wrong
        pass

    def next_state(self, server, file, packet):
        return WaitMsg_R()


if __name__ == "__main__":
    server = "server"
    file = "File"
    packet = None
    state = SendStart_S()

    while state.name != "Exit":
        print(state.name)
        packet = state.act(server, file, packet)
        state = state.next_state(server, file, packet)