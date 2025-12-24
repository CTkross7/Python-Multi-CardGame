import json

def encode(data: dict) -> bytes:
    return (json.dumps(data, ensure_ascii=False) + "\n").encode()

def decode(raw: bytes) -> dict:
    return json.loads(raw.decode())