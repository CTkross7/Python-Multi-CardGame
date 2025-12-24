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
        self.turn_start = None

    def _make_code(self):
        return "".join(random.choices(string.ascii_uppercase + string.digits, k=5))

    def check_password(self, pw):
        if self.password is None:
            return True
        return self.password == pw

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
                except:
                    pass

    # =========================
    # 게임 루프 (수정됨)
    # =========================
    def game_loop(self):
        # 1. 대기
        while len(self.players) < 2:
            self.broadcast({
                "type": "WAIT",
                "count": len(self.players),
                "max": self.max_players
            })
            time.sleep(1)

        # 2. AI 채우기
        while len(self.players) < self.max_players:
            self.players.append(
                Player(
                    pid=1000 + len(self.players),
                    name=f"AI-{len(self.players)}",
                    is_ai=True
                )
            )

        # 3. 게임 시작 & 순서 섞기 (랜덤 순서)
        random.shuffle(self.players)
        
        self.game = GameState(self.players)
        self.game.start()
        self.running = True

        # 4. 각 플레이어에게 "당신의 ID" 알려주기
        for p in self.players:
            if p.conn:
                try:
                    p.conn.sendall(encode({
                        "type": "GAME_START",
                        "my_name": p.name,  # 🔥 핵심: 너는 누구다 라고 알려줌
                        "players": [x.name for x in self.players]
                    }))
                except:
                    pass
        
        # 클라이언트가 준비할 시간 조금 줌
        time.sleep(1)

        # 5. 메인 루프
        while self.running:
            current = self.game.players[self.game.turn]
            self.turn_start = time.time()

            # 공통 상태 (상대의 패 정보는 제외됨)
            base_state = {
                "type": "STATE",
                "turn": current.name,
                "top": self.game.discard[-1].serialize(),
                "counts": {p.name: len(p.hand) for p in self.players}, # 상대방은 카드 수만 보냄
                "turn_time": self.turn_time
            }

            # 개별 전송 (자신의 패만 포함)
            for p in self.players:
                if p.conn:
                    state = dict(base_state)
                    state["hand"] = [c.serialize() for c in p.hand] # 내 패만 보냄
                    state["turn_left"] = max(0, int(self.turn_time - (time.time() - self.turn_start)))
                    
                    try:
                        p.conn.sendall(encode(state))
                    except:
                        pass

            # AI 턴 처리
            if current.is_ai:
                time.sleep(1) # AI가 생각하는 척
                idx = current.ai_think(self.game)
                if idx is not None:
                    self.game.play_card(current, idx)
                else:
                    # 낼 거 없으면 드로우(패스 로직에 따라 다름, 여기선 그냥 턴 넘김)
                    pass
                self.game.next_turn()
                continue

            # 시간 초과 체크
            while time.time() - self.turn_start < self.turn_time:
                time.sleep(0.1)
                # 턴 주인이 바뀌었으면(플레이어가 행동했으면) 루프 탈출
                if self.game.players[self.game.turn] != current:
                    break

            # 여전히 같은 턴이면 시간 초과 -> 강제 턴 넘김
            if self.game.players[self.game.turn] == current:
                self.game.next_turn()

    def handle_command(self, player, msg):
        if not self.running:
            return

        cmd = msg.get("cmd", "")
        current_player = self.game.players[self.game.turn]

        # 🔥 턴 검증: 요청한 플레이어가 현재 턴 주인이 아니면 무시
        if current_player != player:
            return

        if cmd.startswith("PLAY"):
            try:
                _, idx = cmd.split()
                idx = int(idx)
                # 카드 내기 성공 시에만 턴 넘김
                if self.game.play_card(player, idx):
                    self.game.next_turn()
            except:
                pass

        elif cmd == "PASS":
            # 덱에서 한 장 먹는 로직을 추가할 수도 있음. 여기선 단순히 턴 넘김.
            # 정석 UNO: 먹고 낼 수 있으면 냄. 편의상 여기선 바로 턴 넘김.
            # self.game.deck.draw() -> player.hand 추가 로직 필요 시 추가
            p_card = self.game.deck.draw()
            player.hand.append(p_card)
            self.game.next_turn()

        elif cmd == "UNO":
            player.said_uno = True