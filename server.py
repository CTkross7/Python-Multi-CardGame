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
        # ===== 로비 로직 =====
        while True:
            # 메뉴 전송
            conn.sendall(encode({"type": "MENU"}))
            
            data = recv_msg(conn, buffer)
            if not data:
                return

            if data["choice"] == "1":
                # 방 생성
                room = Room(
                    max_players=int(data["max"]),
                    password=data.get("password"),
                    name="UNO GAME"
                )
                with rooms_lock:
                    rooms[room.code] = room
                
                conn.sendall(encode({"type": "INFO", "msg": f"방 코드: {room.code}"}))
                break

            elif data["choice"] == "2":
                # 방 참가
                code = data.get("code")
                pw = data.get("password")
                
                with rooms_lock:
                    room = rooms.get(code)
                
                if not room:
                    conn.sendall(encode({"type": "ERROR", "msg": "방이 없습니다."}))
                    continue
                if room.running:
                    conn.sendall(encode({"type": "ERROR", "msg": "이미 게임 중입니다."}))
                    continue
                # 비밀번호 체크 등 생략(필요시 room.check_password 사용)
                break
        
        # ===== 게임 입장 =====
        # 고유 ID 생성 (Player + 접속순서)
        pid = len(room.players)
        pname = f"Player{pid}"
        
        player = Player(pid, pname, conn)
        room.add_player(player)
        print(f"[{room.code}] {pname} 입장")

        # 방장이면(첫 플레이어면) 게임 루프 쓰레드 실행
        if len(room.players) == 1:
             threading.Thread(target=room.game_loop, daemon=True).start()

        # 명령 대기 루프
        while True:
            msg = recv_msg(conn, buffer)
            if not msg:
                break
            room.handle_command(player, msg)

    except Exception as e:
        print(f"Error: {e}")
    finally:
        if room and player:
            room.remove_player(player)
        conn.close()

def main():
    server = socket.socket()
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen()
    print(f"Server started on {HOST}:{PORT}")

    while True:
        conn, addr = server.accept()
        threading.Thread(target=client_thread, args=(conn, addr), daemon=True).start()

if __name__ == "__main__":
    main()