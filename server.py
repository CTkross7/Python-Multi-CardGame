import socket
from protocol import encode
from player import Player
from game_state import GameState
from ui import UI

HOST = "127.0.0.1"
PORT = 9009

players = []
buffers = {}

def send_state(game):
    for p in players:
        if p.conn:
            p.conn.sendall(encode({
                "type": "STATE",
                "turn": players[game.turn].name,
                "top": game.discard[-1].serialize(),
                "color": game.current_color.value,
                "counts": {pl.name: len(pl.hand) for pl in players},
                "hand": [c.serialize() for c in p.hand]
            }))

def notify_turn(game):
    p = players[game.turn]
    if p.conn:
        p.conn.sendall(encode({
            "type": "TURN_START",
            "you": True
        }))

def main():
    server = socket.socket()
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen()
    print("UNO Server running...")

    pid = 0
    while len(players) < 2:
        conn, _ = server.accept()
        player = Player(pid, f"Player{pid}", conn)
        players.append(player)
        buffers[conn] = b""
        print(f"{player.name} connected")
        pid += 1

    players.append(Player(100, "AI_1", is_ai=True))
    players.append(Player(101, "AI_2", is_ai=True))

    game = GameState(players)
    game.start()

    send_state(game)
    notify_turn(game)

    while True:
        current = players[game.turn]

        # 🤖 AI 턴
        if current.is_ai:
            UI.banner(current.name)
            UI.event(game.ai_turn())
            game.next_turn()
            send_state(game)
            notify_turn(game)
            continue

        conn = current.conn

        try:
            chunk = conn.recv(1024)
            if not chunk:
                raise ConnectionResetError
            buffers[conn] += chunk
        except ConnectionResetError:
            print(f"{current.name} disconnected")
            players.remove(current)
            continue

        while b"\n" in buffers[conn]:
            raw, buffers[conn] = buffers[conn].split(b"\n", 1)
            cmd = raw.decode().strip().split(",")

            # ✅ 턴 검증 (핵심)
            if cmd[0] == "PLAY":
                if conn != players[game.turn].conn:
                    print("❌ Not your turn")
                    continue

                game.play_card(current, int(cmd[1]))
                game.next_turn()
                send_state(game)
                notify_turn(game)

if __name__ == "__main__":
    main()
