import socket
import threading
import time
import os
from protocol import encode, decode
from room import Room
from game.player import Player

HOST = "0.0.0.0"
PORT = 9009
DISCOVERY_PORT = 9010

rooms = {}
rooms_lock = threading.Lock()

last_snapshot = ""   # 방 상태 변화 감지용


# =========================
# LAN IP 얻기
# =========================
def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip


SERVER_IP = get_local_ip()


# =========================
# UDP 서버 자동 탐색
# =========================
def discovery_server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("", DISCOVERY_PORT))

    while True:
        data, addr = sock.recvfrom(1024)
        if data.decode() == "UNO_DISCOVER":
            sock.sendto(
                f"UNO_SERVER:{SERVER_IP}:{PORT}".encode(),
                addr
            )


# =========================
# TCP 패킷 수신
# =========================
def recv_msg(conn, buffer):
    while b"\n" not in buffer:
        chunk = conn.recv(4096)
        if not chunk:
            return None
        buffer.extend(chunk)

    raw, _, rest = buffer.partition(b"\n")
    buffer.clear()
    buffer.extend(rest)
    return decode(raw)


# =========================
# 클라이언트 처리
# =========================
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

            # 방 목록 요청
            if data["choice"] == "LIST":
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
            if data["choice"] == "1":
                room = Room(
                    max_players=int(data["max"]),
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
            elif data["choice"] == "2":
                with rooms_lock:
                    room = rooms.get(data["code"])

                if not room:
                    conn.sendall(encode({"type": "ERROR", "msg": "방 없음"}))
                    continue
                if not room.check_password(data.get("password")):
                    conn.sendall(encode({"type": "ERROR", "msg": "비밀번호 오류"}))
                    continue
                if room.running:
                    conn.sendall(encode({"type": "ERROR", "msg": "게임 진행중"}))
                    continue
                break

        # ---- 플레이어 생성 ----
        pid = len(room.players)
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
        if room and player:
            room.remove_player(player)
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
