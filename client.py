import socket
import sys
import time
from protocol import encode, decode
from ui.console_ui import ConsoleUI as UI

DISCOVERY_PORT = 9010
SERVER_PORT = 9009


# =========================
# 서버 자동 탐색
# =========================
def discover_server(timeout=3):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.settimeout(timeout)

    try:
        sock.sendto(b"UNO_DISCOVER", ("255.255.255.255", DISCOVERY_PORT))
        data, _ = sock.recvfrom(1024)
        msg = data.decode()

        if msg.startswith("UNO_SERVER"):
            _, ip, port = msg.split(":")
            return ip, int(port)
    except:
        return None
    finally:
        sock.close()

    return None


# =========================
# 서버 연결
# =========================
def connect_server():
    result = discover_server()
    if result:
        return result

    UI.error("서버 자동 탐색 실패")
    ip = input("서버 IP 직접 입력: ").strip()
    return ip, SERVER_PORT


server_ip, server_port = connect_server()

sock = socket.socket()
try:
    sock.connect((server_ip, server_port))
except Exception:
    UI.error("서버 연결 실패")
    sys.exit()

buffer = bytearray()


# =========================
# 패킷 수신 (안정화)
# =========================
def recv_packet():
    global buffer
    while b"\n" not in buffer:
        try:
            data = sock.recv(4096)
            if not data:
                return None
            buffer.extend(data)
        except OSError:
            return None

    raw, _, rest = buffer.partition(b"\n")
    buffer.clear()
    buffer.extend(rest)

    try:
        return decode(raw)
    except Exception:
        return None


# =========================
# 로비
# =========================
room_code = None
player_name = None

while True:
    UI.clear()
    msg = recv_packet()
    if msg is None:
        UI.error("서버 응답 없음")
        sys.exit()

    if msg.get("type") != "MENU":
        continue

    UI.banner("UNO NETWORK GAME")
    UI.info(f"서버: {server_ip}:{server_port}")

    print("1. 방 생성")
    print("2. 방 참가")
    print("3. 방 목록")

    choice = input("> ").strip()

    # ----- 방 목록 -----
    if choice == "3":
        sock.sendall(encode({"choice": "LIST"}))
        lst = recv_packet()

        if lst is None or lst.get("type") != "ROOM_LIST":
            UI.error("방 목록을 불러올 수 없습니다")
            time.sleep(1)
            continue

        UI.clear()
        UI.section("방 목록")
        for i, r in enumerate(lst["rooms"]):
            lock = "🔒" if r["locked"] else ""
            status = "진행중" if r["running"] else "대기중"
            print(
                f"{i+1}. [{r['code']}] {r['name']} {lock} "
                f"{r['count']}/{r['max']} {status}"
            )
        input("\nEnter → 돌아가기")
        continue

    # ----- 방 생성 -----
    if choice == "1":
        max_p = input("인원(2~4): ").strip()
        pw = input("비밀번호(없으면 Enter): ").strip()

        sock.sendall(encode({
            "choice": "1",
            "max": max_p,
            "password": pw or None
        }))

        resp = recv_packet()
        if resp is None or resp.get("type") != "INFO":
            UI.error("방 생성 실패")
            time.sleep(1)
            continue

        room_code = resp["code"]
        break

    # ----- 방 참가 -----
    if choice == "2":
        code = input("방 코드: ").strip().upper()
        pw = input("비밀번호: ").strip()

        sock.sendall(encode({
            "choice": "2",
            "code": code,
            "password": pw or None
        }))

        resp = recv_packet()
        if resp is None:
            UI.error("서버 응답 없음")
            sys.exit()

        if resp.get("type") == "ERROR":
            UI.error(resp.get("msg", "입장 실패"))
            time.sleep(1)
            continue

        room_code = code
        break


# =========================
# 게임 루프
# =========================
while True:
    msg = recv_packet()
    if msg is None:
        UI.error("서버 연결 종료")
        break

    # ----- 대기 -----
    if msg["type"] == "WAIT":
        UI.clear()
        UI.banner("대기 중")
        UI.info(f"방 코드: {room_code}")
        UI.info(f"{msg['count']} / {msg['max']}")
        time.sleep(0.5)
        continue

    # ----- 게임 상태 -----
    if msg["type"] == "STATE":
        UI.clear()
        UI.banner("UNO GAME")
        UI.info(f"방 코드: {room_code}")

        turn = msg["turn"]
        UI.info(f"현재 턴: {turn}")

        # 바닥 카드
        UI.section("바닥 카드")
        print(UI.card(msg["top"]))

        # 플레이어 현황
        UI.section("플레이어")
        for n, c in msg["counts"].items():
            mark = "👈" if n == player_name else ""
            print(f"{n}: {c}장 {mark}")

        # 내 카드
        UI.section("내 카드")
        UI.grid(
            list(enumerate(msg["hand"])),
            lambda x: f"[{x[0]}] {UI.card(x[1])}"
        )

        # 타이머
        UI.timer_bar(msg["turn_left"], msg["turn_time"])

        # 입력
        if player_name and turn == player_name:
            cmd = input("번호 / p / u > ").strip().lower()
            if cmd == "p":
                sock.sendall(encode({"cmd": "PASS"}))
            elif cmd == "u":
                sock.sendall(encode({"cmd": "UNO"}))
            elif cmd.isdigit():
                sock.sendall(encode({"cmd": f"PLAY {cmd}"}))
        else:
            time.sleep(0.3)
