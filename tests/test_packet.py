from udpai.packet import Packet, PacketType

def test_serialize():
    packet = Packet(PacketType.DATA, 0, b'Lorem ipsum', 23)
    serialized = packet.to_bytes()
    packet_reconstructed = Packet.from_bytes(serialized)

    assert packet.type == packet_reconstructed.type
    assert packet.crc == packet_reconstructed.crc
    assert packet.data_len == packet_reconstructed.data_len
    assert packet.data == packet_reconstructed.data
    assert packet.packet_id == packet_reconstructed.packet_id
    assert packet.check()

def test_packet_crc():
    packet = Packet(PacketType.DATA, 0, b'hello world', 323)
    assert packet.check()