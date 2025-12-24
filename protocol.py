import json

def encode(data: dict) -> bytes:
    """
    JSON + 개행 문자로 메시지 경계 보장
    """
    return (json.dumps(data) + "\n").encode("utf-8")


def decode(raw: bytes) -> dict:
    """
    단일 JSON 문자열 디코딩
    """
    return json.loads(raw.decode("utf-8"))
