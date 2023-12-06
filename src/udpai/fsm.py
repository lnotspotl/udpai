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
