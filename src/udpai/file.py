#!/usr/bin/env python3

import os
from udpai.packet import Packet, PacketType, DATA_SIZE

class File:
    def __init__(self, file_path):
        self.file_path = file_path

    def __iter__(self):
        self.file = open(self.file_path, "rb")
        return self

    def __next__(self):
        data = self.file.read(DATA_SIZE)
        if not data:  # EOF
            raise StopIteration
        
        # create packet
        packet = Packet(
            type=PacketType.DATA,
            data_len=len(data),
            data=data
        )
        return packet