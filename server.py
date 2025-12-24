# server.py
import socket, threading
from protocol import encode
from player import Player
from game_state import GameState
from ui import UI


HOST = "127.0.0.1"
PORT = 9009

clients = []
players = []

def broadcast(data):
    for p in players:
        if p.conn:
            p.conn.sendall(encode(data))

def handle_client(conn, addr, pid):
    name = f"Player{pid}"
    player = Player(pid, name, conn)
    players.append(player)
    print(f"{name} connected")

def main():
    server = socket.socket()
    server.bind((HOST, PORT))
    server.listen()

    print("UNO Server running...")

    # 최대 2명 접속 + AI 2명
    pid = 0
    while len(players) < 2:
        conn, addr = server.accept()
        handle_client(conn, addr, pid)
        pid += 1

    # AI 추가
    players.append(Player(100, "AI_1", is_ai=True))
    players.append(Player(101, "AI_2", is_ai=True))

    game = GameState(players)
    game.start()

    broadcast({"type": "START"})

    while True:
        p = players[game.turn]
        broadcast({
            "type": "STATE",
            "turn": p.name,
            "top": game.discard[-1].serialize(),
            "color": game.current_color.value,
            "counts": {pl.name: len(pl.hand) for pl in players}
        })

        if p.is_ai:
            UI.banner(p.name + " THINKING")
            event = game.ai_turn()
            UI.event(event)
            game.next_turn()
            
        else:
            msg = p.conn.recv(1024)
            data = msg.decode().strip().split(",")
            if data[0] == "PLAY":
                game.play_card(p, int(data[1]))
                game.next_turn()

if __name__ == "__main__":
    main()