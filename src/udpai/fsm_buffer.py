#!/usr/bin/env python3

from .packet import Packet, PacketType

class Buffer:
    def __init__(self, capacity):
        self.capacity = capacity
        self.buffer = [None] * capacity

    def size(self):
        return sum([1 if x is not None else 0 for x in self.buffer])
            
    def empty(self):
        return self.size() == 0
    
    def full(self):
        return self.size() == self.capacity

class SenderBuffer(Buffer):
    def __init__(self, capacity, file):
        super().__init__(capacity=capacity)
        self.first_id = 0

        self.fill_buffer(file)

        # want to send:
        # self.first_id, self.first_id + 1, ... , self.first_id + self.capacity - 1

    def fill_buffer(self, file):
        for i in range(self.capacity):
            if self.buffer[i] is None:
                file.ack()
                packet = file.next()
                if packet is None:
                    break
                self.buffer[i] = [packet, True]  # packet, needs sending

    def process_ack(self, packet, file):
        assert packet.check()
        assert packet.type == PacketType.ACK

        packet_id = packet.packet_id

        if packet_id < self.first_id:
            return 

        n_deleted = packet_id - self.first_id

        self.buffer = self.buffer[n_deleted:] + [None] * n_deleted
        self.first_id = packet_id
        self.fill_buffer(file)

        if self.buffer[0] is not None:
            self.buffer[0][1] = True

    def send_buffer(self, server):
        for i in range(self.capacity):
            if self.buffer[i] is not None:
                packet, needs_sending = self.buffer[i]
                if needs_sending:
                    server.send(packet)
                    self.buffer[i][1] = False



class ReceiverBuffer(Buffer):
    def __init__(self, capacity):
        super().__init__(capacity=capacity)
        self.expected_id = 0

    def insert_packet(self, packet):

        # crc check
        if not packet.check():
            return
        
        packet_id = packet.packet_id

        assert packet_id <= self.expected_id + self.capacity

        # packet id check
        if packet_id < self.expected_id:
            return

        buffer_idx = packet_id - self.expected_id

        if self.buffer[buffer_idx] is not None:
            assert self.buffer[buffer_idx] == packet
        else:
            self.buffer[buffer_idx] = packet

    def empty_buffer(self, file):
        buffer_idx = 0
        while buffer_idx < self.capacity:
            if self.buffer[buffer_idx] is None:
                break
            
            packet = self.buffer[buffer_idx]
            self._write_packet_to_file(packet, file)
            self._update_buffer()
            self.expected_id += 1
            buffer_idx += 1

        return self.expected_id
    
    def _write_packet_to_file(self, packet, file):
        file.write_packet(packet)
        print(packet.packet_id, " <- ID packetu")

    def _update_buffer(self):
        self.buffer = self.buffer[1:] + [None]