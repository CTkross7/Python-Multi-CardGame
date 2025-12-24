import socket
from protocol import encode, decode
from ui.console_ui import ConsoleUI as UI
from ui.console_ui import Color

sock = socket.socket()
sock.connect(("127.0.0.1", 9009))

buffer = bytearray()

def recv_msg(sock):
    while b"\n" not in buffer:
        chunk = sock.recv(4096)
        if not chunk:
            return None
        buffer.extend(chunk)

    raw, _, rest = buffer.partition(b"\n")
    buffer.clear()
    buffer.extend(rest)
    return decode(raw)


player_name = "Player0"
room_code = None


# ===== 로비 =====
while True:
    UI.clear()
    UI.banner("UNO 콘솔 게임 | DEV: CTkross")

    recv_msg(sock)  # MENU
    choice = input("1. 방 생성 | 2. 방 참가 : ").strip()

    if choice == "1":
        max_p = input("인원 수 (2~4): ").strip()
        pw = input("비밀번호 (없으면 Enter): ").strip()

        sock.sendall(encode({
            "choice": "1",
            "max": max_p,
            "password": pw or None
        }))

        resp = recv_msg(sock)
        room_code = resp["msg"].split(": ")[-1]

        UI.clear()
        UI.banner("방 생성 완료")
        UI.info(f"방 코드: [{room_code}]")
        input("Enter → 대기실")
        break

    elif choice == "2":
        room_code = input("방 코드: ").strip().upper()
        pw = input("비밀번호: ").strip()

        sock.sendall(encode({
            "choice": "2",
            "code": room_code,
            "password": pw or None
        }))

        resp = recv_msg(sock)
        if resp["type"] == "ERROR":
            UI.error(resp["msg"])
            input("Enter")
            continue
        break


# ===== 게임 루프 =====
while True:
    msg = recv_msg(sock)

    if msg["type"] == "WAIT":
        UI.clear()
        UI.banner("대기 중")
        UI.info(f"방 코드: [{room_code}]")
        UI.info(f"{msg['count']} / {msg['max']} 명 대기 중")
        continue

    if msg["type"] == "STATE":
        UI.clear()
        UI.banner("UNO GAME")
        UI.info(f"방 코드: [{room_code}]")

        UI.highlight_turn(msg["turn"], msg["turn"] == player_name)

        if msg["turn"] == player_name:
            UI.section("턴 제한 시간")
            UI.timer_bar(msg["turn_left"], msg["turn_time"])

        UI.section("바닥 카드")
        print(UI.card(msg["top"]))

        UI.section("상대 상태")
        for name, cnt in msg["counts"].items():
            if name != player_name:
                print(f"{name}: 카드 {cnt}장")

        UI.section("내 카드")
        UI.grid(list(enumerate(msg["hand"])),
                lambda x: f"[{x[0]}]{UI.card(x[1])}")

        if len(msg["hand"]) == 1:
            UI.blink("🔥 UNO! 입력 안 하면 패널티! 🔥", Color.RED)

        if msg["turn"] == player_name:
            cmd = input("\n번호 / p / u : ").strip().lower()
            if cmd == "u":
                sock.sendall(encode({"cmd": "UNO"}))
            elif cmd == "p":
                sock.sendall(encode({"cmd": "PASS"}))
            else:
                sock.sendall(encode({"cmd": f"PLAY {cmd}"}))
