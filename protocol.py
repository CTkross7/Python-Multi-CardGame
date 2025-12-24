import json

def encode(data: dict) -> bytes:
    return (json.dumps(data) + "\n").encode()

def decode(data: bytes) -> dict:
    return json.loads(data.decode())
