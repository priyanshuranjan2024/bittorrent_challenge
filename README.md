# BitTorrent Client

Just exploring and building a basic version of bittorrent by reading docs and online forums.

---

## Project Structure

### 1. `bencode.py`
this file is for encoding and decoding the bencode(that is the encoding used in the bittorrent protocol for torrent files)


---

### 2. `tracker_client.py`
main and entry point of the program.


---

### 3. `peer_protocol.py`
implementing the peer protocol as per bittorrent specifications

---

### 4. `peer_client.py`
handling bitfields.
---

### 5. `piece_manager.py`
tracking the status of pieces.


---

### 6. `peer_worker.py`
creating workers for downloading.

---

### 7. `piece_downloader.py`
handling of downloading and reassembly.

---

### 8. `file_assembler.py`
just assembles the downloaded pieces into a file.

---

## ▶ How to Run

### Real torrent file
```bash
python3 tracker_client.py test.torrent
