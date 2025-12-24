import socket, threading, time
from protocol import encode, decode
from room import Room
from game.player import Player

HOST, PORT = "127.0.0.1", 9009
rooms = {}

def client_thread(conn):
    while True:
        conn.sendall(encode({"type": "MENU"}))
        data = decode(conn.recv(1024))

        if data["choice"] == "1":
            max_p = int(data["max"])
            pw = data.get("password")
            room = Room(max_p, pw)
            rooms[room.code] = room
            conn.sendall(encode({"type": "INFO", "msg": f"방 코드: {room.code}"}))
            break

        elif data["choice"] == "2":
            room = rooms.get(data["code"])
            if not room or not room.check_password(data.get("password")):
                conn.sendall(encode({"type": "ERROR", "msg": "방 정보가 틀렸습니다"}))
                continue
            break

    player = Player(len(room.players), f"Player{len(room.players)}", conn)
    room.add_player(player)

    while not room.started:
        conn.sendall(encode({
            "type": "WAIT",
            "count": len(room.players),
            "max": room.max_players
        }))
        if room.can_start():
            room.start_game()
        time.sleep(1)

    while True:
        game = room.game
        p = game.players[game.turn]

        state = {
            "type": "STATE",
            "turn": p.name,
            "top": game.discard[-1].serialize(),
            "hand": [c.serialize() for c in player.hand],
            "counts": {pl.name: len(pl.hand) for pl in game.players}
        }
        conn.sendall(encode(state))

        if game.is_timeout():
            game.next_turn()
            continue

        if p.is_ai:
            idx = p.ai_think(game)
            if idx is not None:
                game.play_card(p, idx)
            game.next_turn()
        elif p == player:
            msg = decode(conn.recv(1024))
            if msg["cmd"].startswith("PLAY"):
                _, idx = msg["cmd"].split()
                game.play_card(player, int(idx))
                game.next_turn()

def main():
    server = socket.socket()
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen()
    print("UNO 서버 실행 중")

    while True:
        conn, _ = server.accept()
        threading.Thread(target=client_thread, args=(conn,), daemon=True).start()

if __name__ == "__main__":
    main()
