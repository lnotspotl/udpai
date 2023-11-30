#!/usr/bin/env python3

import socket
from . packet import Packet, PacketType

BUFFER_SIZE = 1028 + 256  # 1.25 KB

class Server:
    def __init__(
        self, local_ip: str, local_port: int, remote_ip: str, remote_port: int
    ):
        self.setup_sockets(local_ip, local_port, remote_ip, remote_port)

    def setup_sockets(
        self, local_ip: str, local_port: int, remote_ip: str, remote_port: int
    ):
        socket_settings = [socket.AF_INET, socket.SOCK_DGRAM]  # Internet, UDP
        self.local_socket = socket.socket(*socket_settings)
        self.local_socket.bind((local_ip, local_port))
        self.local_ip = local_ip
        self.local_port = local_port

        self.remote_socket = socket.socket(*socket_settings)
        self.remote_ip = remote_ip
        self.remote_port = remote_port

    def send(self, packet: Packet):
        send_settings = (self.remote_ip, self.remote_port)
        self.remote_socket.sendto(packet.to_bytes(), send_settings)

    def receive(self, timeout=None):
        self.local_socket.settimeout(timeout)
        try:
            received_bytes, _ = self.local_socket.recvfrom(BUFFER_SIZE)
        except socket.timeout:
            return None
        return Packet.from_bytes(received_bytes)
    
    def __del__(self):
        self.local_socket.close()
        self.remote_socket.close()

if __name__ == "__main__":
    local_ip = "10.0.0.80"
    local_port = 5005 
    remote_ip = "10.0.0.80"
    remote_port = 5005

    server = Server(
        local_ip=remote_ip,
        local_port = remote_port,
        remote_ip=local_ip,
        remote_port=local_port
    )

    print("Server is listening...")
    while True:
        dummy_packet = Packet(PacketType.DATA, 0, 0, b"")
        server.send(dummy_packet)