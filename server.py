import socket
import threading
import time
import os
from protocol import encode, decode
from room import Room
from game.player import Player

# Windows 콘솔에서 ANSI 이스케이프 시퀀스를 지원하도록 설정
if os.name == 'nt':
    os.system('')

HOST = "0.0.0.0"
PORT = 9009
DISCOVERY_PORT = 9010

rooms = {}
rooms_lock = threading.Lock()
last_snapshot = ""


def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except OSError:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip


SERVER_IP = get_local_ip()


def discovery_server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("", DISCOVERY_PORT))

    while True:
        try:
            data, addr = sock.recvfrom(1024)
            if data.decode() == "UNO_DISCOVER":
                sock.sendto(f"UNO_SERVER:{SERVER_IP}:{PORT}".encode(), addr)
        except OSError:
            break


def recv_msg(conn, buffer):
    while b"\n" not in buffer:
        try:
            chunk = conn.recv(4096)
            if not chunk:
                return None
            buffer.extend(chunk)
        except OSError:
            return None

    raw, _, rest = buffer.partition(b"\n")
    buffer.clear()
    buffer.extend(rest)

    try:
        return decode(raw)
    except Exception:
        return None


def client_thread(conn, addr):
    player = None
    room = None
    buffer = bytearray()

    try:
        # ---- 메뉴 루프 ----
        while True:
            conn.sendall(encode({
                "type": "MENU",
                "server_ip": SERVER_IP
            }))

            data = recv_msg(conn, buffer)
            if not data:
                return

            choice = data.get("choice")

            # 방 목록 요청
            if choice == "LIST":
                with rooms_lock:
                    rooms_data = [{
                        "code": c,
                        "name": r.name,
                        "count": len(r.players),
                        "max": r.max_players,
                        "locked": bool(r.password),
                        "running": r.running
                    } for c, r in rooms.items()]

                conn.sendall(encode({
                    "type": "ROOM_LIST",
                    "rooms": rooms_data
                }))
                continue

            # 방 생성
            if choice == "1":
                try:
                    max_p = int(data.get("max", 4))
                except (ValueError, TypeError):
                    max_p = 4

                room = Room(
                    max_players=max_p,
                    password=data.get("password"),
                    name=data.get("name", "UNO ROOM")
                )
                with rooms_lock:
                    rooms[room.code] = room

                conn.sendall(encode({
                    "type": "INFO",
                    "code": room.code
                }))
                break

            # 방 참가
            elif choice == "2":
                with rooms_lock:
                    room = rooms.get(data.get("code", ""))

                if not room:
                    conn.sendall(encode({"type": "ERROR", "msg": "방이 존재하지 않습니다."}))
                    continue
                if not room.check_password(data.get("password")):
                    conn.sendall(encode({"type": "ERROR", "msg": "비밀번호가 일치하지 않습니다."}))
                    continue
                if room.running:
                    conn.sendall(encode({"type": "ERROR", "msg": "이미 게임이 진행 중입니다."}))
                    continue
                
                # [추가] 방 정원 초과 검사
                if len(room.players) >= room.max_players:
                    conn.sendall(encode({"type": "ERROR", "msg": "방 정원이 가득 찼습니다."}))
                    continue

                break

        # ---- 플레이어 생성 (단조 증가 PID 적용) ----
        # len(room.players) 대신 room.issue_pid() 호출하여 PID 충돌 방지
        pid = room.issue_pid()
        pname = f"Player{pid}"
        player = Player(pid, pname, conn)
        room.add_player(player)

        if len(room.players) == 1:
            threading.Thread(target=room.game_loop, daemon=True).start()

        # ---- 명령 처리 ----
        while True:
            msg = recv_msg(conn, buffer)
            if not msg:
                break
            room.handle_command(player, msg)

    finally:
        # 퇴장 처리 및 빈 방 cleanup
        if room and player:
            room.remove_player(player)
            with rooms_lock:
                if len(room.players) == 0 and room.code in rooms:
                    del rooms[room.code]
        try:
            conn.close()
        except OSError:
            pass


# =========================================================
# ANSI 이스케이프 시퀀스를 사용한 모니터링
# =========================================================
def monitor_rooms():
    global last_snapshot

    while True:
        time.sleep(1)

        with rooms_lock:
            lines = [f"서버 IP: {SERVER_IP}:{PORT}", "-" * 40]
            for c, r in rooms.items():
                lines.append(
                    f"[{c}] {r.name} "
                    f"{'🔒' if r.password else ''} "
                    f"{len(r.players)}/{r.max_players} "
                    f"{'진행중' if r.running else '대기중'}"
                )

        snapshot = "\n".join(lines)

        if snapshot != last_snapshot:
            # \033[H : 커서를 화면 좌상단(0,0)으로 이동
            # \033[J : 커서 위치부터 화면 끝까지 지우기
            # 외부 os.system("cls") 프로세스 호출 없이 콘솔 화면을 신속하고 깨끗하게 갱신
            print("\033[H\033[J", end="")
            print(snapshot)
            last_snapshot = snapshot


def main():
    server = socket.socket()
    server.bind((HOST, PORT))
    server.listen()

    print(f"UNO SERVER STARTED : {SERVER_IP}:{PORT}")

    threading.Thread(target=discovery_server, daemon=True).start()
    threading.Thread(target=monitor_rooms, daemon=True).start()

    while True:
        try:
            conn, addr = server.accept()
            threading.Thread(
                target=client_thread,
                args=(conn, addr),
                daemon=True
            ).start()
        except OSError:
            break


if __name__ == "__main__":
    main()
        pid = len(room.players)
        pname = f"Player{pid}"
        player = Player(pid, pname, conn)
        room.add_player(player)

        if len(room.players) == 1:
            threading.Thread(target=room.game_loop, daemon=True).start()

        if len(room.players) >= room.max_players:
            conn.sendall(encode({"type": "ERROR", "msg", "방 정원이 초과 되었습니다."}))
            continue
                                     

        # ---- 명령 처리 ----
        while True:
            msg = recv_msg(conn, buffer)
            if not msg:
                break
            room.handle_command(player, msg)

    finally:
        if room and player:
            room.remove_player(player)
            with rooms_lock:
                if len(room.players) == 0 and room.code in room:
                    del rooms[room.code]
        conn.close()


# =========================
# 방 상태 모니터 (변경 시만 출력)
# =========================
def monitor_rooms():
    global last_snapshot

    while True:
        time.sleep(1)

        with rooms_lock:
            lines = [f"서버 IP: {SERVER_IP}:{PORT}", "-" * 40]
            for c, r in rooms.items():
                lines.append(
                    f"[{c}] {r.name} "
                    f"{'🔒' if r.password else ''} "
                    f"{len(r.players)}/{r.max_players} "
                    f"{'진행중' if r.running else '대기중'}"
                )

        snapshot = "\n".join(lines)

        if snapshot != last_snapshot:
            os.system("cls" if os.name == "nt" else "clear")
            print(snapshot)
            last_snapshot = snapshot


# =========================
# 메인
# =========================
def main():
    server = socket.socket()
    server.bind((HOST, PORT))
    server.listen()

    print(f"UNO SERVER STARTED : {SERVER_IP}:{PORT}")

    threading.Thread(target=discovery_server, daemon=True).start()
    threading.Thread(target=monitor_rooms, daemon=True).start()

    while True:
        conn, addr = server.accept()
        threading.Thread(
            target=client_thread,
            args=(conn, addr),
            daemon=True
        ).start()


if __name__ == "__main__":
    main()
