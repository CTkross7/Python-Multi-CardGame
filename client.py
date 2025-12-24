# client.py
import socket
from protocol import decode

HOST = "127.0.0.1"
PORT = 9009

sock = socket.socket()
sock.connect((HOST, PORT))

print("Connected to UNO Server")

while True:
    data = sock.recv(4096)
    msg = decode(data)

    if msg["type"] == "STATE":
        print("\nCurrent Turn:", msg["turn"])
        print("Top Card:", msg["top"])
        print("Current Color:", msg["color"])
        print("Players:", msg["counts"])

        if msg["turn"] == "Player0":
            cmd = input("Play card index or pass (p): ")
            if cmd != "p":
                sock.sendall(f"PLAY,{cmd}".encode())