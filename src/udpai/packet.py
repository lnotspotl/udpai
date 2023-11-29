#!/usr/bin/env python3

from enum import Enum
from dataclasses import dataclass

from zlib import crc32

PACKET_TYPE_SIZE = 1  # 1 byte
CRC_SIZE = 4  # 4 bytes
DATA_LEN_SIZE = 4  # 4 bytes
DATA_SIZE = 1024  # 1 KB
ENDIAN = 'big'

class PacketType(Enum):
    START = 0
    STOP = 1
    DATA = 2
    ACK = 3

class Packet:
    def __init__(self, type: PacketType, data_len: int, data: bytes, crc=None):
        self.type = type
        self.crc = crc
        self.data_len = data_len
        self.data = data

        if crc is None:
            self.fill_crc()

    def fill_crc(self):
        self.crc = self._calculate_crc()

    def check_crc(self):
        crc = self._calculate_crc()
        return crc == self.crc

    def _calculate_crc(self):
        crc_bytes = self.type_bytes + self.data_len_bytes + self.data_bytes
        return crc32(crc_bytes)

    def to_bytes(self):
        return self.type_bytes + self.crc_bytes + self.data_len_bytes + self.data_bytes
    
    @classmethod
    def from_bytes(cls, packet_bytes):
        type = cls._type_from_bytes(packet_bytes)
        crc = cls._crc_from_bytes(packet_bytes)
        data_len = cls._data_len_from_bytes(packet_bytes)
        data = cls._data_from_bytes(packet_bytes)

        return cls(type, data_len, data, crc)
    
    @property
    def type_bytes(self):
        return self.type.value.to_bytes(PACKET_TYPE_SIZE, byteorder=ENDIAN)
    
    @property
    def crc_bytes(self):
        return self.crc.to_bytes(CRC_SIZE, byteorder=ENDIAN)
    
    @property
    def data_len_bytes(self):
        return self.data_len.to_bytes(DATA_LEN_SIZE, byteorder=ENDIAN)
    
    @property
    def data_bytes(self):
        return self.data

    @staticmethod
    def _type_from_bytes(packet_bytes):
        start, stop = 0, PACKET_TYPE_SIZE
        type = int.from_bytes(packet_bytes[start:stop], byteorder=ENDIAN)
        return PacketType(type)

    @staticmethod
    def _crc_from_bytes(packet_bytes):
        start, stop = PACKET_TYPE_SIZE, PACKET_TYPE_SIZE + CRC_SIZE
        crc = int.from_bytes(packet_bytes[start:stop], byteorder=ENDIAN)
        return crc

    @staticmethod
    def _data_len_from_bytes(packet_bytes):
        start, stop = PACKET_TYPE_SIZE + CRC_SIZE, PACKET_TYPE_SIZE + CRC_SIZE + DATA_LEN_SIZE
        data_len = int.from_bytes(packet_bytes[start:stop], byteorder=ENDIAN)
        return data_len
    
    @staticmethod
    def _data_from_bytes(packet_bytes):
        start = PACKET_TYPE_SIZE + CRC_SIZE + DATA_LEN_SIZE
        data = packet_bytes[start:]
        return data