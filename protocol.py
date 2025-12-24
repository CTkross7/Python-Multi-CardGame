import json

def encode(data: dict) -> bytes:
    return (json.dumps(data, ensure_ascii=False) + "\n").encode("utf-8")

def decode(raw: bytes) -> dict:
    return json.loads(raw.decode("utf-8"))
