import sys
import os
import time
import hashlib
import random
import urllib.parse
import urllib.request

# from urllib.parse import urlparse
from bencoding import bencode
from bencoding import bdecode
from file_parser import load_torrent
from peer_client import connect_and_get_bitfield, bitfield_to_pieces
from piece_manager import PieceManager
from peer_worker import PeerWorker
from file_assembler import FileAssembler


def generate_peer_id():
    prefix = "-CC0101-"
    suffix = bytes([random.randint(0, 255) for _ in range(12)])
    return prefix.encode() + suffix

def parse_compact_peers(peers_bytes):
    peers = []
    for i in range(0, len(peers_bytes), 6):
        ip_bytes = peers_bytes[i:i+4]
        port_bytes = peers_bytes[i+4:i+6]

        ip = ".".join(str(b) for b in ip_bytes)
        port = int.from_bytes(port_bytes, "big")

        peers.append((ip, port))
    return peers

def main():
    if len(sys.argv) != 2:
        print("Usage: python tracker_client.py <torrent_file_or_url>")
        return

    source = sys.argv[1]
    raw = load_torrent(source)
    torrent = bdecode(raw)

    announce = torrent["announce"]
    if isinstance(announce, bytes):
        announce = announce.decode()

    info = torrent["info"]
    
    pm = PieceManager(info)
    print(f"Total pieces: {pm.total_pieces}")
    
    filename = info["name"] #filename of the thing i am going to download
    
    if isinstance(filename, bytes):
        filename = filename.decode()

    fa = FileAssembler(
        filename,
        pm.piece_length,
        pm.total_length
    )
    
    info_bencoded = bencode(info)
    info_hash = hashlib.sha1(info_bencoded).digest()

    peer_id = generate_peer_id()
    
    pm.info_hash = info_hash #pushing into the peer manager
    pm.peer_id = peer_id

    left = info.get("length", 0)
    
    
    if isinstance(left, bytes):
        left = int(left)
    
    #url
    params = {
        "info_hash": info_hash,
        "peer_id": peer_id,
        "port": 6881,
        "uploaded": 0,
        "downloaded": 0,
        "left": left,
        "compact": 1,
        "event":"started",
        "numwant":50
    }

    
    query = urllib.parse.urlencode(params)

    tracker_url = announce + "?" + query

    print("ccBitTorrent")
    print("Announce URL:", tracker_url)

    #contact tracker
    with urllib.request.urlopen(tracker_url) as r:
        status = r.status
        response_data = r.read()

    print(f"{status} OK")

    # decoding response from above tracker
    tracker_response = bdecode(response_data)

    peers_bytes = tracker_response.get("peers")

    if not peers_bytes:
        print("No peers received")
        return

    peers = parse_compact_peers(peers_bytes)
    
    # peers = [("127.0.0.1", 5000)] #for testing purpose //simulation part

    print(f"Got {len(peers)} peers")

    for i, (ip, port) in enumerate(peers):
        print(f"Peer {i} is ip: {ip} port: {port}")
        
    #bug
    #0 peers showing
    #i think problem is with the bittorrent file i downloaded from the ubuntu website  
    print("\nConnecting to peers and requesting bitfields")
    
    peer_bitfields = []
    
    for i, (ip,port) in enumerate(peers):
        print(f"\nConnecting to Peer {i} ({ip}:{port})")  
        bitfield = connect_and_get_bitfield(ip, port, info_hash, peer_id)
        
        if bitfield is None:
            print("Could not retrieve bitfield")
            continue
        
        peer_bitfields.append((ip, port, bitfield))

        
        pieces = bitfield_to_pieces(bitfield)
        
        print(f"Bitfield size: {len(bitfield)} bytes")
        
        for p in pieces[:30]:
            print(f"Has piece {p}")
            
    
    print("\nStarting peer workers")
    
    workers = []
    
    for i, (ip, port, bitfield) in enumerate(peer_bitfields):
        w = PeerWorker(i, ip, port, pm, bitfield,fa)
        w.start()
        workers.append(w)
        
    for w in workers:
        w.join()
        
    while not pm.is_complete(): #in case of 0 peers getting hanged
        #will use keyboard interrupt for now till i get better torrent file online
        time.sleep(1)

    print("download complete")
    print("shutting down")



if __name__ == "__main__":
    main()
