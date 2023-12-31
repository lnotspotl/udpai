#!/usr/bin/env python3

import os
from udpai.packet import Packet, PacketType, DATA_SIZE

class File:
    def __init__(self, file_path, write):
        self.file_path = file_path
        self.write = write
        self.next_ready = True
        self.last_packet = None
        self.packet_id = 0

        if self.write:
            self.file = open(self.file_path, "wb")
        else:
            self.iter = self.__iter__()

    def write_packet(self, packet: Packet):
        assert self.write
        self.file.write(packet.data)

    def next(self):
        if self.next_ready:
            self.next_ready = False
            try:
                self.last_packet = next(self.iter)
            except:
                self.last_packet = None

        return self.last_packet
    
    def ack(self):
        self.next_ready = True

    def __iter__(self):
        assert not self.write 
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
            data=data,
            packet_id=self.packet_id,
        )
        self.packet_id += 1
        return packet
    
    def __del__(self):
        self.file.close()
