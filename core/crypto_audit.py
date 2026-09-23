import hashlib
from pathlib import Path

def compute_sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def compute_sha256_file(filepath: str | Path) -> str:
    sha = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            sha.update(chunk)
    return sha.hexdigest()
