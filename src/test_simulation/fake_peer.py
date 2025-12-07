import socket
import hashlib
from peer_protocol import (
    decode_handshake,
    encode_handshake,
    build_message
)

HOST = "127.0.0.1"
PORT = 5000

PIECE_LENGTH = 16
TOTAL_PIECES = 5

# Make fake file data
fake_file = b"A" * (PIECE_LENGTH * TOTAL_PIECES)

# Generate fake piece hashes
piece_hashes = []
for i in range(TOTAL_PIECES):
    start = i * PIECE_LENGTH
    end = start + PIECE_LENGTH
    piece_hashes.append(hashlib.sha1(fake_file[start:end]).digest())


def make_bitfield():
    # 5 pieces → 1 byte is enough
    return bytes([0b11111000])


def handle_client(conn):
    # Receive handshake
    hs = conn.recv(68)
    decoded = decode_handshake(hs)

    # Respond with handshake
    conn.sendall(hs)

    # Send bitfield
    bitfield_msg = build_message(5, make_bitfield())
    conn.sendall(bitfield_msg)

    while True:
        header = conn.recv(4)
        if not header:
            break

        length = int.from_bytes(header, "big")
        if length == 0:
            continue

        body = conn.recv(length)
        msg_id = body[0]

        if msg_id == 6:  # request
            index = int.from_bytes(body[1:5], "big")
            begin = int.from_bytes(body[5:9], "big")
            req_len = int.from_bytes(body[9:13], "big")

            start = index * PIECE_LENGTH + begin
            block = fake_file[start:start + req_len]

            # piece message
            payload = (
                index.to_bytes(4, "big") +
                begin.to_bytes(4, "big") +
                block
            )

            msg = build_message(7, payload)
            conn.sendall(msg)


def main():
    s = socket.socket()
    s.bind((HOST, PORT))
    s.listen(1)

    print(f"Fake peer running on {HOST}:{PORT}")
    conn, _ = s.accept()
    print("Client connected")

    handle_client(conn)

    conn.close()
    s.close()


if __name__ == "__main__":
    main()
