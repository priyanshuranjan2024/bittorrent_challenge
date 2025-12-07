#encoding part
def bencode(data):
    if isinstance(data, int):
        return f"i{data}e".encode()

    elif isinstance(data, str):
        s = data.encode()
        return f"{len(s)}:".encode() + s

    elif isinstance(data, bytes):
        return f"{len(data)}:".encode() + data

    elif isinstance(data, list):
        return b"l" + b"".join(bencode(item) for item in data) + b"e"

    elif isinstance(data, dict):
        result = b"d"
        for key in sorted(data.keys()):
            if not isinstance(key, str):
                raise TypeError("dictionary key must be string")
            result += bencode(key)
            result += bencode(data[key])
        result += b"e"
        return result

    else:
        raise TypeError(f"Unsupported type: {type(data)}")


#decoding part
def bdecode(data: bytes):
    
    def decode_at(index):
        char = data[index:index+1]

        #integer
        if char == b"i":
            end = data.index(b"e", index)
            number = int(data[index+1:end])
            return number, end + 1

        #list
        elif char == b"l":
            lst = []
            idx = index + 1
            while data[idx:idx+1] != b"e":
                item, idx = decode_at(idx)
                lst.append(item)
            return lst, idx + 1

        #dict
        elif char == b"d":
            dct = {}
            idx = index + 1
            while data[idx:idx+1] != b"e":
                key, idx = decode_at(idx)
                value, idx = decode_at(idx)
                dct[key.decode() if isinstance(key, bytes) else key] = value
            return dct, idx + 1

        #string bytes data
        elif char.isdigit():
            colon = data.index(b":", index)
            length = int(data[index:colon])
            start = colon + 1
            end = start + length
            return data[start:end], end

        else:
            raise ValueError("invalid bencode format")

    result, _ = decode_at(0)
    return result
