import hashlib


def hash_file(content: bytes) -> bytes:
    return hashlib.sha256(content).digest()
