import threading

class FileAssembler:
    def __init__(self, filename, piece_length, total_length):
        self.filename = filename
        self.piece_length = piece_length
        self.total_length = total_length
        self.lock = threading.Lock()

        with open(self.filename, "wb") as f:
            f.truncate(total_length)

    def write_piece(self, index, data: bytes):
        offset = index * self.piece_length
        with self.lock:
            with open(self.filename, "r+b") as f:
                f.seek(offset)
                f.write(data)
