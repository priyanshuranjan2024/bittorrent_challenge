import threading
import socket

from piece_downloader import download_piece
from peer_protocol import encode_handshake, decode_handshake
from file_assembler import FileAssembler


class PeerWorker(threading.Thread):
    def __init__(self, peer_index, peer_ip, peer_port, piece_manager, bitfield,file_assembler):
        super().__init__()
        self.peer_index = peer_index
        self.peer_ip = peer_ip
        self.peer_port = peer_port
        self.pm = piece_manager
        self.bitfield = bitfield
        self.fa = file_assembler


    def peer_has_piece(self, piece_index):
        if not self.bitfield:
            return False

        byte_index = piece_index // 8
        bit_index = piece_index % 8

        if byte_index >= len(self.bitfield):
            return False

        b = self.bitfield[byte_index]
        return (b & (1 << (7 - bit_index))) != 0
    
    
    def _connect(self):


        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5)
        s.connect((self.peer_ip, self.peer_port))

        hs = encode_handshake(self.pm.info_hash, self.pm.peer_id)
        s.sendall(hs)

        resp = s.recv(68)
        decode_handshake(resp)

        return s

    
    
    def run(self):
        sock = None

        try:
            sock = self._connect()
        except:
            return

        while True:
            index = self.pm.get_next_piece()
            if index is None:
                break

            if not self.peer_has_piece(index):
                self.pm.requeue(index)
                continue

            piece_len = self.pm.piece_length
            expected_hash = self.pm.hashes[index]

            data = download_piece(sock, index, piece_len, expected_hash)

            if data is None:
                self.pm.requeue(index)
                continue
            
            
            #verifing hash
            if not self.pm.verify_piece(index, data):
                print(f"[Peer {self.peer_index}] Hash failed for piece {index}")
                self.pm.requeue(index)
                continue
            
            
            #success
            self.fa.write_piece(index, data)
            self.pm.mark_complete(index)
            print(f"Downloaded and saved piece {index}")  



   