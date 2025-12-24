import socket
import threading
import time
from protocol import encode, decode
from room import Room
from game.player import Player

HOST = "0.0.0.0"
PORT = 9009

rooms = {}
rooms_lock = threading.Lock()


def recv_msg(conn, buffer: bytearray):
    while b"\n" not in buffer:
        chunk = conn.recv(4096)
        if not chunk:
            return None
        buffer.extend(chunk)

    raw, _, rest = buffer.partition(b"\n")
    buffer.clear()
    buffer.extend(rest)
    return decode(raw)


def client_thread(conn, addr):
    player = None
    room = None
    buffer = bytearray()

    try:
        while True:
            conn.sendall(encode({"type": "MENU"}))
            data = recv_msg(conn, buffer)
            if not data:
                return

            if data["choice"] == "LIST":
                with rooms_lock:
                    room_list = [{
                        "code": c,
                        "name": r.name,
                        "count": len(r.players),
                        "max": r.max_players,
                        "locked": bool(r.password),
                        "running": r.running
                    } for c, r in rooms.items()]

                conn.sendall(encode({
                    "type": "ROOM_LIST",
                    "rooms": room_list
                }))
                continue

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
                    "msg": f"방 코드: {room.code}"
                }))
                break

            elif data["choice"] == "2":
                code = data["code"]
                pw = data.get("password")

                with rooms_lock:
                    room = rooms.get(code)

                if not room:
                    conn.sendall(encode({"type": "ERROR", "msg": "존재하지 않는 방"}))
                    continue
                if not room.check_password(pw):
                    conn.sendall(encode({"type": "ERROR", "msg": "비밀번호가 틀렸습니다"}))
                    continue
                if room.running:
                    conn.sendall(encode({"type": "ERROR", "msg": "이미 진행중인 방"}))
                    continue
                break

        player = Player(len(room.players), f"Player{len(room.players)}", conn)
        room.add_player(player)

        if not room.running:
            threading.Thread(target=room.game_loop, daemon=True).start()

        while True:
            msg = recv_msg(conn, buffer)
            if not msg:
                break
            room.handle_command(player, msg)

    except Exception as e:
        print(f"[ERROR] {addr}: {e}")

    finally:
        if room and player:
            room.remove_player(player)
        conn.close()


def monitor_rooms():
    while True:
        time.sleep(5)
        print("\n===== 서버 방 상태 =====")
        with rooms_lock:
            if not rooms:
                print("현재 생성된 방 없음")
            for code, room in rooms.items():
                lock = "🔒" if room.password else ""
                status = "진행중" if room.running else "대기중"
                print(f"[{code}] {room.name}{lock} {len(room.players)}/{room.max_players} {status}")
        print("========================")


def main():
    server = socket.socket()
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen()

    print("UNO 멀티방 서버 실행 중")

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
