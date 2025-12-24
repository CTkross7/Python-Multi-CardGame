import socket
import sys
from protocol import encode, decode
from ui.console_ui import ConsoleUI as UI
from ui.console_ui import Color
import time

sock = socket.socket()
try:
    sock.connect(("127.0.0.1", 9009))
except ConnectionRefusedError:
    print("서버에 연결할 수 없습니다.")
    sys.exit()

# 초기값은 None, 서버가 정해줄 때까지 대기
player_name = None 
room_code = None
msg_buffer = bytearray()

def recv_packet(conn):
    global msg_buffer
    while b"\n" not in msg_buffer:
        try:
            chunk = conn.recv(4096)
            if not chunk:
                return None
            msg_buffer.extend(chunk)
        except OSError:
            return None

    line, _, rest = msg_buffer.partition(b"\n")
    msg_buffer.clear()
    msg_buffer.extend(rest)
    return decode(line)

# ===== 로비 =====
while True:
    UI.clear()
    UI.banner("UNO Network Game")
    
    # 메뉴 표시를 위해 서버가 주는 패킷 대기 (MENU or WAIT or ...)
    # 첫 연결 시 MENU 패킷이 옴
    pass 
    
    # 여기서 recv를 바로 하면 화면 갱신 전에 블로킹되므로, 
    # 흐름상 서버가 MENU를 보내주길 기대함.
    # 하지만 server.py 구조상 클라이언트가 접속하면 바로 루프로 들어가서 MENU를 보냄.
    
    msg = recv_packet(sock)
    if not msg:
        sys.exit()

    if msg.get("type") == "MENU":
        choice = input("1. 방 생성 | 2. 방 참가 : ")
        if choice == "1":
            max_p = input("인원 수 (2~4): ")
            pw = input("비밀번호 (Enter로 생략): ")
            sock.sendall(encode({"choice": "1", "max": max_p, "password": pw or None}))
            
            resp = recv_packet(sock)
            if resp["type"] == "INFO":
                room_code = resp["msg"].split(": ")[-1]
                print(f"방 생성됨: {room_code}")
                # 대기 상태로 진입
                break
                
        elif choice == "2":
            code = input("방 코드: ").upper()
            pw = input("비밀번호: ")
            sock.sendall(encode({"choice": "2", "code": code, "password": pw or None}))
            
            resp = recv_packet(sock)
            if resp.get("type") == "ERROR":
                print(resp["msg"])
                input("엔터 키를 눌러 다시 시도...")
                continue
            # 성공하면 루프 탈출
            break

# ===== 게임 루프 =====
while True:
    UI.clear()
    
    msg = recv_packet(sock)
    if not msg:
        print("서버 연결 끊김")
        break

    # 1. 대기 화면
    if msg["type"] == "WAIT":
        UI.banner("대기 중")
        if room_code:
            UI.info(f"방 코드: {room_code}")
        UI.info(f"접속 인원: {msg['count']} / {msg['max']}")
        continue

    # 2. 게임 시작 (내 이름 할당)
    elif msg["type"] == "GAME_START":
        player_name = msg["my_name"]
        UI.clear()
        UI.banner("게임 시작!")
        UI.info(f"당신의 이름은 [{player_name}] 입니다.")
        time.sleep(2)
        continue

    # 3. 게임 상태 업데이트
    elif msg["type"] == "STATE":
        UI.banner(f"UNO - {player_name}")
        UI.info(f"현재 턴: {msg['turn']}")
        
        # 내 턴 여부 확인
        is_my_turn = (msg["turn"] == player_name)
        
        UI.highlight_turn(msg["turn"], is_my_turn)
        
        # 바닥 카드
        UI.section("바닥 카드")
        print("   " + UI.card(msg["top"]))

        # 다른 플레이어 정보
        UI.section("플레이어 현황")
        for p_name, cnt in msg["counts"].items():
            marker = "👈 (나)" if p_name == player_name else ""
            print(f"   {p_name}: 카드 {cnt}장 {marker}")

        # 내 패 (번호와 함께 출력)
        UI.section("나의 패")
        UI.grid(
            list(enumerate(msg["hand"])),
            lambda x: f"[{x[0]}] {UI.card(x[1])}"
        )
        
        # 턴 진행 시간 바
        UI.timer_bar(msg["turn_left"], msg["turn_time"])

        # 입력 처리 (내 턴일 때만)
        if is_my_turn:
            print("\n[행동] 숫자:카드내기 / p:카드먹기(패스) / u:우노")
            cmd = input("입력 > ").strip().lower()
            
            if cmd == "u":
                sock.sendall(encode({"cmd": "UNO"}))
            elif cmd == "p":
                sock.sendall(encode({"cmd": "PASS"}))
            elif cmd.isdigit():
                sock.sendall(encode({"cmd": f"PLAY {cmd}"}))
        else:
            print("\n상대방의 턴을 기다리는 중...")
            # 화면 깜빡임 방지를 위해 약간 대기 (필수는 아님)
            time.sleep(0.5)

    elif msg["type"] == "ERROR":
        UI.error(msg["msg"])
        time.sleep(1)