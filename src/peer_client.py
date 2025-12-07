import socket
import time

from peer_protocol import (
    encode_handshake,
    decode_handshake,
    decode_message,
    encode_interested 
)


def connect_and_get_bitfield(ip, port, info_hash, peer_id, timeout=5):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        s.connect((ip, port))

        #handsake send
        hs = encode_handshake(info_hash, peer_id)
        s.sendall(hs)

        resp = s.recv(68) #handsake receive
        decode_handshake(resp)
        
        s.sendall(encode_interested()) # issue 1 : telling other peers i am interested

        bitfield = None
        

        while True: #reading
            header = s.recv(4)
            if len(header) < 4:
                break

            length = int.from_bytes(header, "big")

            if length == 0:
                continue

            body = s.recv(length)
            msg = decode_message(header + body)

            if msg["type"] == "bitfield":
                bitfield = msg["bitfield"]
                break

            if msg["type"] == "have": #corner case incase of just have message
                break

        s.close()
        return bitfield

    except Exception as e:
        return None


def bitfield_to_pieces(bitfield: bytes):
    pieces = []
    for byte_index, b in enumerate(bitfield):
        for bit in range(8):
            if b & (1 << (7 - bit)):
                pieces.append(byte_index * 8 + bit)
    return pieces
