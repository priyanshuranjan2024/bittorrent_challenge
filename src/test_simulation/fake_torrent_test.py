import hashlib
from bencoding import bencode

PIECE_LENGTH = 16
TOTAL_PIECES = 5

# Fake file
fake_file = b"A" * (PIECE_LENGTH * TOTAL_PIECES)

pieces = b""
for i in range(TOTAL_PIECES):
    start = i * PIECE_LENGTH
    end = start + PIECE_LENGTH
    pieces += hashlib.sha1(fake_file[start:end]).digest()

torrent = {
    "announce": "http://localhost:9999/announce",
    "info": {
        "name": "fake_test_file.bin",
        "piece length": PIECE_LENGTH,
        "length": len(fake_file),
        "pieces": pieces
    }
}

with open("fake_test.torrent", "wb") as f:
    f.write(bencode(torrent))

print("Fake torrent created: fake_test.torrent")
