#!/usr/bin/env python3

from .packet import Packet, PacketType

class Buffer:
    def __init__(self, capacity):
        self.capacity = capacity
        self.buffer = [None] * capacity

    def buffer_idx(self, packet_id):
        return packet_id % self.capacity

class SenderBuffer(Buffer):
    def __init__(self, capacity):
        super().__init__(capacity=capacity)

        # Next id that needs to be sent
        self.next_id = 0

    def fill_buffer(self, file):
        for i in range(self.capacity):
            idx = self.buffer_idx(self.next_id + i)

            if self.buffer[idx] is None:
                file.ack()
                packet = file.next()
                if packet is None:
                    break

                assert packet.packet_id == self.next_id + i
                
                self.buffer[idx] = [packet, True]  # packet, needs sending

    def send_buffer(self, server):
        for i in range(self.capacity):
            idx = (self.next_id + i) % self.capacity

            if self.buffer[idx] is not None:
                packet, needs_sending = self.buffer[idx]
                if needs_sending:
                    server.send(packet)
                    self.buffer[idx][1] = False

    def size(self):
        return sum([1 if x is not None else 0 for x in self.buffer])
            
    def empty(self):
        return self.size() == 0
    
    def full(self):
        return self.size() == self.capacity
    
    def process_ack(self, packet):
        if packet is None:
            idx = self.buffer_idx(self.next_id)
            if self.buffer[idx] is not None:
                self.buffer[idx][1] = True
            return 

        if not packet.check_crc():
            return 
        
        assert packet.type == PacketType.ACK

        self.empty_buffer(packet.packet_id)

        assert self.next_id <= packet.packet_id
        self.next_id = packet.packet_id

    def empty_buffer(self, packet_id):
        t = self.next_id
        while t != packet_id:
            idx = self.buffer_idx(t)
            self.buffer[idx] = None
            t += 1

        idx = self.buffer_idx(packet_id)
        if self.buffer[idx] is not None:
            self.buffer[idx][1] = True

class ReceiverBuffer(Buffer):
    def __init__(self, capacity):
        super().__init__(capacity=capacity)

        self.next_id = 0

    def process_packet(self, packet, file):
        assert packet.type == PacketType.DATA

        idx = self.buffer_idx(packet.packet_id)
        if self.buffer[idx] is None:
            self.buffer[idx] = packet

    def write_to_file(self, file):
        next_id = self.next_id
        for i in range(self.capacity):
            idx = self.buffer_idx(next_id)
            packet = self.buffer[idx]
            if packet is None:
                break

            if packet.check():
                break

            file.write_packet(packet)
            self.buffer[idx] = None
            next_id += 1

        self.next_id = next_id

        return self.next_id