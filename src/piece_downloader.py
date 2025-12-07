import socket
from peer_protocol import (
    encode_request,
    encode_interested,
    encode_unchoke,
    decode_message
)

BLOCK_SIZE = 16 * 1024


def recv_exact(sock, size):
    data = b""
    while len(data) < size:
        chunk = sock.recv(size - len(data))
        if not chunk:
            return None
        data += chunk
    return data


def download_piece(sock, piece_index, piece_length, piece_hash):
    sock.sendall(encode_interested())
    sock.sendall(encode_unchoke())

    blocks = {}
    bytes_requested = 0

    #requests
    while bytes_requested < piece_length:
        req_len = min(BLOCK_SIZE, piece_length - bytes_requested)
        req = encode_request(piece_index, bytes_requested, req_len)
        sock.sendall(req)
        bytes_requested += req_len

    received = 0

    while received < piece_length:
        header = recv_exact(sock, 4)
        if not header:
            return None

        length = int.from_bytes(header, "big")

        if length == 0:
            continue

        body = recv_exact(sock, length)
        msg = decode_message(header + body)

        if msg["type"] == "piece":
            begin = msg["begin"]
            block = msg["block"]
            blocks[begin] = block
            received += len(block)

    #reassembling
    data = bytearray()
    offset = 0
    while offset < piece_length:
        data += blocks[offset]
        offset += len(blocks[offset])

    return bytes(data)
