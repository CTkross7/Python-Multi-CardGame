import socket
from protocol import encode, decode
from ui.console_ui import ConsoleUI as UI
from ui.console_ui import Color

sock = socket.socket()
sock.connect(("127.0.0.1", 9009))

player_name = "Player0"  # 현재 클라이언트 기준
room_code = None         # ⭐ 방 코드 저장용

# ===== 로비 =====
while True:
    UI.clear()
    UI.banner("UNO 콘솔 게임 | DEV: CTkross")

    decode(sock.recv(1024))  # MENU 수신
    choice = input("1. 방 생성 | 2. 방 참가 : ")

    # ----- 방 생성 -----
    if choice == "1":
        max_p = input("인원 수 (2~4): ")
        pw = input("비밀번호 (없으면 Enter): ")

        sock.sendall(encode({
            "choice": "1",
            "max": max_p,
            "password": pw or None
        }))

        # 🔥 방 코드 수신
        resp = decode(sock.recv(1024))
        if resp["type"] == "INFO":
            room_code = resp["msg"].split(": ")[-1]

            UI.clear()
            UI.banner("방 생성 완료")
            UI.info(f"방 코드: [{room_code}]")
            UI.info("친구에게 이 코드를 공유하세요")
            input("\nEnter를 누르면 대기실로 이동합니다...")
        break

    # ----- 방 참가 -----
    elif choice == "2":
        room_code = input("방 코드: ").strip().upper()
        pw = input("비밀번호: ")

        sock.sendall(encode({
            "choice": "2",
            "code": room_code,
            "password": pw or None
        }))

        resp = decode(sock.recv(1024))
        if resp["type"] == "ERROR":
            UI.error(resp["msg"])
            input("계속하려면 Enter")
            continue
        break


# ===== 게임 루프 =====
while True:
    UI.clear()
    msg = decode(sock.recv(4096))

    # ----- 대기 화면 -----
    if msg["type"] == "WAIT":
        UI.banner("대기 중")
        if room_code:
            UI.info(f"방 코드: [{room_code}]")
        UI.info(f"{msg['count']} / {msg['max']} 명 대기 중")
        continue

    # ----- 게임 상태 -----
    if msg["type"] == "STATE":
        UI.banner("UNO GAME")

        # 방 코드 상시 표시
        if room_code:
            UI.info(f"방 코드: [{room_code}]")

        # 턴 강조
        UI.highlight_turn(msg["turn"], msg["turn"] == player_name)

        # 상태 영역
        UI.section("게임 상태")
        print("바닥 카드:", UI.card(msg["top"]))

        # 상대 정보
        UI.section("상대 상태")
        for name, cnt in msg["counts"].items():
            if name != player_name:
                print(f"{name}: 카드 {cnt}장")

        # 내 카드
        UI.section("내 카드")
        UI.grid(
            list(enumerate(msg["hand"])),
            lambda x: f"[{x[0]}]{UI.card(x[1])}"
        )

        # UNO 경고
        if len(msg["hand"]) == 1:
            UI.blink("🔥 UNO! 입력 안 하면 패널티! 🔥", Color.RED)

        # 입력 처리
        if msg["turn"] == player_name:
            cmd = input("\n낼 카드 번호 (p: 패스 / u: UNO): ").strip()
            if cmd == "u":
                sock.sendall(encode({"cmd": "UNO"}))
            elif cmd != "p":
                sock.sendall(encode({"cmd": f"PLAY {cmd}"}))
