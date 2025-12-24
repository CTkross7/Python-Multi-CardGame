import socket
from protocol import decode
from ui import UI

HOST = "127.0.0.1"
PORT = 9009

sock = socket.socket()
sock.connect((HOST, PORT))
print("Connected to UNO Server")

buffer = b""
my_turn = False

while True:
    chunk = sock.recv(4096)
    if not chunk:
        continue

    buffer += chunk

    while b"\n" in buffer:
        raw, buffer = buffer.split(b"\n", 1)
        if not raw.strip():
            continue

        msg = decode(raw)

        msg_type = msg.get("type")

        # 🔔 내 턴 알림
        if msg_type == "TURN_START":
            my_turn = True
            UI.banner("YOUR TURN!")
            print("👉 지금 당신의 턴입니다!")
            continue

        # 🎮 게임 상태
        if msg_type == "STATE":
            UI.banner("GAME STATE")
            print("Turn:", msg["turn"])
            print("Top:", UI.card(msg["top"]))
            print("Color:", msg["color"])
            print("Players:", msg["counts"])

            print("\nYour hand:")
            for i, c in enumerate(msg["hand"]):
                print(f"[{i}] {UI.card(c)}")

            # ❗ 턴이 넘어갔으면 입력 비활성화
            if msg["turn"] != "Player0":
                my_turn = False
                continue

            # ✅ 내 턴일 때만 입력
            if my_turn:
                cmd = input("Play card index or p: ")
                if cmd != "p":
                    sock.sendall(f"PLAY,{cmd}\n".encode())
                my_turn = False
