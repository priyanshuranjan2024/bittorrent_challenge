PSTR = b"BitTorrent protocol"
PSTR_LEN = len(PSTR)

MSG_IDS = {
    "choke": 0,
    "unchoke": 1,
    "interested": 2,
    "not_interested": 3,
    "have": 4,
    "bitfield": 5,
    "request": 6,
    "piece": 7,
    "cancel": 8,
}

def encode_handshake(info_hash: bytes, peer_id: bytes) -> bytes:
    if len(info_hash) != 20:
        raise ValueError("info_hash must be 20 bytes")
    if len(peer_id) != 20:
        raise ValueError("peer_id must be 20 bytes")

    reserved = b"\x00" * 8

    return (
        bytes([PSTR_LEN]) + # protocol string length
        PSTR +                   
        reserved +               
        info_hash +              
        peer_id                  
    )


def decode_handshake(data: bytes):
    if len(data) < 49:
        raise ValueError("handsake short")

    pstrlen = data[0]
    pstr = data[1:1+pstrlen]

    if pstr != PSTR:
        raise ValueError("invalid protocol string")

    reserved_start = 1 + pstrlen
    info_hash_start = reserved_start + 8
    peer_id_start = info_hash_start + 20

    info_hash = data[info_hash_start:peer_id_start]
    peer_id = data[peer_id_start:peer_id_start + 20]

    return {
        "info_hash": info_hash,
        "peer_id": peer_id
    }


def encode_keep_alive() -> bytes:
    return (0).to_bytes(4, "big")



def build_message(msg_id: int, payload: bytes = b"") -> bytes:
    length = 1 + len(payload)
    return length.to_bytes(4, "big") + bytes([msg_id]) + payload


# general protocol functions

def encode_choke():
    return build_message(MSG_IDS["choke"])

def encode_unchoke():
    return build_message(MSG_IDS["unchoke"])

def encode_interested():
    return build_message(MSG_IDS["interested"])

def encode_not_interested():
    return build_message(MSG_IDS["not_interested"])

def encode_have(index: int):
    payload = index.to_bytes(4, "big")
    return build_message(MSG_IDS["have"], payload)

def encode_bitfield(bitfield: bytes):
    return build_message(MSG_IDS["bitfield"], bitfield)

def encode_request(index: int, begin: int, length: int):
    payload = (
        index.to_bytes(4, "big") +
        begin.to_bytes(4, "big") +
        length.to_bytes(4, "big")
    )
    return build_message(MSG_IDS["request"], payload)

def encode_piece(index: int, begin: int, block: bytes):
    payload = (
        index.to_bytes(4, "big") +
        begin.to_bytes(4, "big") +
        block
    )
    return build_message(MSG_IDS["piece"], payload)

def encode_cancel(index: int, begin: int, length: int):
    payload = (
        index.to_bytes(4, "big") +
        begin.to_bytes(4, "big") +
        length.to_bytes(4, "big")
    )
    return build_message(MSG_IDS["cancel"], payload)


def decode_message(data: bytes):
    if len(data) < 4:
        raise ValueError("Incomplete message")

    length = int.from_bytes(data[:4], "big")

    # Keep-alive
    if length == 0:
        return {"type": "keep-alive"}

    if len(data) < 4 + length:
        raise ValueError("Partial message")

    msg_id = data[4]
    payload = data[5:4+length]

    # Reverse lookup
    msg_type = None
    for name, mid in MSG_IDS.items():
        if mid == msg_id:
            msg_type = name
            break

    if msg_type is None:
        raise ValueError("Unknown message id")

    result = {"type": msg_type}

    # Payload parsing
    if msg_type == "have":
        result["index"] = int.from_bytes(payload, "big")

    elif msg_type in ("request", "cancel"):
        result["index"] = int.from_bytes(payload[0:4], "big")
        result["begin"] = int.from_bytes(payload[4:8], "big")
        result["length"] = int.from_bytes(payload[8:12], "big")

    elif msg_type == "piece":
        result["index"] = int.from_bytes(payload[0:4], "big")
        result["begin"] = int.from_bytes(payload[4:8], "big")
        result["block"] = payload[8:]

    elif msg_type == "bitfield":
        result["bitfield"] = payload

    return result
