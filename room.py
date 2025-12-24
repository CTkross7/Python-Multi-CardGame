import threading
import time
import random
import string
from game.game_state import GameState
from game.player import Player
from protocol import encode

class Room:
    def __init__(self, max_players, password=None, name="UNO ROOM"):
        self.code = self._make_code()
        self.name = name
        self.password = password
        self.max_players = max_players
        self.players = []
        self.game = None
        self.running = False
        self.lock = threading.Lock()
        self.turn_time = 15

    def _make_code(self):
        return "".join(random.choices(string.ascii_uppercase + string.digits, k=5))

    def add_player(self, player):
        with self.lock:
            self.players.append(player)

    def remove_player(self, player):
        with self.lock:
            if player in self.players:
                self.players.remove(player)

    def broadcast(self, data):
        for p in self.players:
            if p.conn:
                try:
                    p.conn.sendall(encode(data))
                except: pass

    def game_loop(self):
        # 1. 인원 대기
        while len(self.players) < self.max_players:
            self.broadcast({"type": "WAIT", "count": len(self.players), "max": self.max_players})
            time.sleep(1)

        # 2. 순서 랜덤화 및 이름 부여
        random.shuffle(self.players)
        for i, p in enumerate(self.players):
            p.name = f"Player{i}" # 섞인 순서대로 이름 재부여
            if p.conn:
                p.conn.sendall(encode({
                    "type": "GAME_START",
                    "my_name": p.name
                }))

        # 3. 게임 엔진 시작
        self.game = GameState(self.players)
        self.game.start()
        self.running = True

        # 4. 메인 게임 루프
        while self.running:
            current_p = self.game.players[self.game.turn]
            self.turn_start = time.time()

            # 상태 전송 (개인화된 패킷)
            for p in self.players:
                if p.conn:
                    state = {
                        "type": "STATE",
                        "turn": current_p.name,
                        "top": self.game.discard[-1].serialize(),
                        "counts": {x.name: len(x.hand) for x in self.players},
                        "hand": [c.serialize() for c in p.hand], # 내 패만 전송
                        "turn_left": max(0, int(self.turn_time - (time.time() - self.turn_start))),
                        "turn_time": self.turn_time
                    }
                    p.conn.sendall(encode(state))

            # AI 처리 혹은 시간 초과 대기
            if current_p.is_ai:
                time.sleep(1.5)
                idx = current_p.ai_think(self.game)
                if idx is not None: self.game.play_card(current_p, idx)
                self.game.next_turn()
            else:
                # 플레이어 응답 대기 (handle_command에서 턴을 넘김)
                while time.time() - self.turn_start < self.turn_time:
                    if self.game.players[self.game.turn] != current_p:
                        break # 이미 카드를 내서 턴이 넘어감
                    time.sleep(0.1)
                
                # 시간 초과 시 강제 드로우 및 턴 넘김
                if self.game.players[self.game.turn] == current_p:
                    current_p.hand.append(self.game.deck.draw())
                    self.game.next_turn()

    def handle_command(self, player, msg):
        if not self.running: return
        cmd = msg.get("cmd", "")
        current_p = self.game.players[self.game.turn]

        if current_p != player: return # 턴이 아닌 사람의 명령 무시

        if cmd.startswith("PLAY"):
            idx = int(cmd.split()[1])
            if self.game.play_card(player, idx):
                self.game.next_turn()
        elif cmd == "PASS":
            player.hand.append(self.game.deck.draw())
            self.game.next_turn()