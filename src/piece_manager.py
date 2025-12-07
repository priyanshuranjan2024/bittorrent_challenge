import threading
import queue
import hashlib


class PieceManager:
    def __init__(self, info_dict):
        self.piece_length = info_dict["piece length"]
        self.total_length = info_dict.get("length", 0)

        raw_pieces = info_dict["pieces"]

        self.hashes = [
            raw_pieces[i:i+20]
            for i in range(0, len(raw_pieces), 20)
        ]

        self.total_pieces = len(self.hashes)
        
        self.info_hash = None
        self.peer_id = None

        self.have = [False] * self.total_pieces
        self.queue = queue.Queue()

        for i in range(self.total_pieces):
            self.queue.put(i)

        self.lock = threading.Lock()


#general functions 
    def mark_complete(self, index):
        with self.lock:
            self.have[index] = True

    def needs_piece(self, index):
        with self.lock:
            return not self.have[index]

    def requeue(self, index):
        self.queue.put(index)

    def get_next_piece(self):
        try:
            return self.queue.get_nowait()
        except queue.Empty:
            return None

    def verify_piece(self, index, data: bytes):
        expected = self.hashes[index]
        actual = hashlib.sha1(data).digest()
        return expected == actual
    
    def is_complete(self):
        with self.lock:
            return all(self.have)

