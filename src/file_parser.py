import sys
import urllib.request
from urllib.parse import urlparse

from bencoding import bdecode


def load_torrent(source):
    parsed = urlparse(source)

    #url then download
    if parsed.scheme in ("http", "https"):
        with urllib.request.urlopen(source) as response:
            return response.read()
    else:
        #just opening the file
        with open(source, "rb") as f:
            return f.read()


def main():
    if len(sys.argv) != 2:
        print("Usage: python torrent_parser.py <torrent_path_or_url>")
        return

    source = sys.argv[1]

    raw_data = load_torrent(source)
    torrent = bdecode(raw_data)

    announce = torrent.get("announce")
    info = torrent.get("info")

    if isinstance(announce, bytes):
        announce = announce.decode()

    print("\ announce URL:")
    print(announce)

    print("\n info dictionary:")
    print(info)


if __name__ == "__main__":
    main()
