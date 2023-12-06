#!/usr/bin/env python3

from enum import Enum
from dataclasses import dataclass

from zlib import crc32
from hashlib import sha1

PACKET_TYPE_SIZE = 1  # 1 byte
CRC_SIZE = 4  # 4 bytes
DATA_LEN_SIZE = 4  # 4 bytes
HASH_SIZE = len(sha1(b"Hello world").hexdigest().encode('utf-8'))
DATA_SIZE = 1024  # 1 KB
ENDIAN = 'big'

class PacketType(Enum):
    START = 0
    STOP = 1
    DATA = 2
    ACK = 3

class Packet:
    def __init__(self, type: PacketType, data_len: int, data: bytes, crc=None, hash=None):
        self.type = type
        self.crc = crc
        self.hash = hash
        self.data_len = data_len
        self.data = data

        if hash is None:
            self.fill_hash()

        if crc is None:
            self.fill_crc()

    def check(self):
        return self.check_crc() and self.check_hash()

    def fill_crc(self):
        self.crc = self._calculate_crc()

    def fill_hash(self):
        self.hash = self._calculate_hash()

    def _calculate_hash(self):
        hash_bytes = self.data_bytes
        return sha1(hash_bytes).hexdigest().encode('utf-8')
    
    def check_hash(self):
        hash = self._calculate_hash()
        return hash == self.hash

    def check_crc(self):
        crc = self._calculate_crc()
        return crc == self.crc

    def _calculate_crc(self):
        assert self.hash is not None
        crc_bytes = self.type_bytes + self.data_len_bytes + self.data_bytes + self.hash_bytes
        return crc32(crc_bytes)

    def to_bytes(self):
        return self.type_bytes + self.crc_bytes + self.data_len_bytes + self.hash_bytes + self.data_bytes
    
    @classmethod
    def from_bytes(cls, packet_bytes):
        type = cls._type_from_bytes(packet_bytes)
        crc = cls._crc_from_bytes(packet_bytes)
        data_len = cls._data_len_from_bytes(packet_bytes)
        data = cls._data_from_bytes(packet_bytes)
        hash = cls._hash_from_bytes(packet_bytes)

        return cls(type, data_len, data, crc, hash)
    
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
    
    @property
    def hash_bytes(self):
        return self.hash

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
    def _hash_from_bytes(packet_bytes):
        start, stop = PACKET_TYPE_SIZE + CRC_SIZE + DATA_LEN_SIZE, PACKET_TYPE_SIZE + CRC_SIZE + DATA_LEN_SIZE + HASH_SIZE
        hash = packet_bytes[start:stop]
        return hash
    
    @staticmethod
    def _data_from_bytes(packet_bytes):
        start = PACKET_TYPE_SIZE + CRC_SIZE + DATA_LEN_SIZE + HASH_SIZE
        data = packet_bytes[start:]
        return data