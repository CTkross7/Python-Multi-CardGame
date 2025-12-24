# client.py
import socket
from protocol import decode

HOST = "127.0.0.1"
PORT = 9009

sock = socket.socket()
sock.connect((HOST, PORT))

print("Connected to UNO Server")

buffer = b""

while True:
    chunk = sock.recv(4096)
    if not chunk:
        continue

    buffer += chunk

    while b"\n" in buffer:
        raw, buffer = buffer.split(b"\n", 1)

        if not raw.strip():
            continue  # ✅ 빈 메시지 무시

        msg = decode(raw)

        if msg["type"] == "STATE":
            print("\nCurrent Turn:", msg["turn"])
            print("Top Card:", msg["top"])
            print("Current Color:", msg["color"])
            print("Players:", msg["counts"])

            if msg["turn"] == "Player0":
                cmd = input("Play card index or pass (p): ")
                if cmd != "p":
                    sock.sendall(f"PLAY,{cmd}".encode())
