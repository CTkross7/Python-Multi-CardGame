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
        self.spectators = []

        self.game = None
        self.running = False

        self.lock = threading.Lock()
        self.log = []

        self._pid_counter = 0

        # 턴 제한 시간 (초)
        self.turn_time = 15
        self.turn_start = None

    # =========================
    # 유틸
    # =========================

    def issue_pid(self) -> int:
        """
        플레이어가 퇴장 후 재입장해도 ID가 중복되지 않도록
        단조 증가(Monotonic Increasing) ID를 안전하게 발급합니다.
        """
        with self.lock:
            self._pid_counter += 1
            return self._pid_counter
        
    def _make_code(self):
        return "".join(
            random.choices(string.ascii_uppercase + string.digits, k=5)
        )

    # ✅ [중요] 비밀번호 체크 메서드 추가
    def check_password(self, pw):
        """
        비밀번호가 없는 방이면 항상 True
        비밀번호가 있으면 정확히 일치해야 True
        """
        if self.password is None:
            return True
        return self.password == pw

    # =========================
    # 플레이어 관리
    # =========================
    def add_player(self, player):
        with self.lock:
            self.players.append(player)

    def remove_player(self, player):
        with self.lock:
            if player in self.players:
                self.players.remove(player)

    # =========================
    # 통신
    # =========================
    def broadcast(self, data):
        for p in self.players:
            if p.conn:
                try:
                    p.conn.sendall(encode(data))
                except:
                    pass

    # =========================
    # 게임 루프
    # =========================
    def game_loop(self):
        # ----- 대기 상태 -----
        while len(self.players) < 2:
            self.broadcast({
                "type": "WAIT",
                "count": len(self.players),
                "max": self.max_players
            })
            time.sleep(1)

        # ----- AI 자동 채우기 -----
        while len(self.players) < self.max_players:
            self.players.append(
                Player(
                    pid=1000 + len(self.players),
                    name=f"AI{len(self.players)}",
                    is_ai=True
                )
            )

        # ----- 게임 시작 -----
        self.game = GameState(self.players)
        self.game.start()
        self.running = True

        # ===== 메인 게임 루프 =====
        while self.running:
            current = self.game.players[self.game.turn]
            self.turn_start = time.time()

            base_state = {
                "type": "STATE",
                "turn": current.name,
                "top": self.game.discard[-1].serialize(),
                "counts": {
                    p.name: len(p.hand)
                    for p in self.players
                },
                "turn_time": self.turn_time
            }

            # 플레이어별 상태 전송
            for p in self.players:
                if p.conn:
                    state = dict(base_state)
                    state["hand"] = [
                        c.serialize() for c in p.hand
                    ]
                    state["turn_left"] = max(
                        0,
                        int(self.turn_time - (time.time() - self.turn_start))
                    )
                    try:
                        p.conn.sendall(encode(state))
                    except:
                        pass

            # ----- AI 처리 -----
            if current.is_ai:
                time.sleep(1)
                idx = current.ai_think(self.game)
                if idx is not None:
                    self.game.play_card(current, idx)
                self.game.next_turn()
                continue

            # ----- 턴 시간 초과 -----
            while time.time() - self.turn_start < self.turn_time:
                time.sleep(0.2)

            # 시간 초과 시 자동 패스
            if self.game.players[self.game.turn] == current:
                self.game.next_turn()
 

    # =========================================================
    # ✅ [서버 권위 구조] 명령 처리 및 클라이언트 검증 로직
    # =========================================================
    
    def handle_command(self, player, msg):
        if not self.running or not self.game:
            return

        with self.lock:
            # 1. 턴 검증: 현재 턴인 플레이어의 명령만 허용 (타인 턴 조작 차단)
            if self.game.players[self.game.turn] != player:
                return

            cmd = msg.get("cmd", "")

            if cmd.startswith("PLAY"):
                try:
                    parts = cmd.split()
                    if len(parts) != 2:
                        return
                    idx = int(parts[1])

                    # 2. 카드 소유 검사: 요청 인덱스가 실제 플레이어 손패 범위 내에 있는지 검사
                    if 0 <= idx < len(player.hand):
                        # 3. 규칙 검사: 해당 카드가 낼 수 있는 카드인지 GameState에서 판별 후 제출
                        if self.game.play_card(player, idx):
                            self.game.next_turn()
                    else:
                        # 손패 범위를 벗어난 인덱스 요청 (변조된 패킷 무시)
                        print(f"[보호] {player.name}의 유효하지 않은 카드 인덱스 요청: {idx}")

                except (ValueError, IndexError):
                    return

            elif cmd.upper() == "PASS":
                self.game.next_turn()

            elif cmd.upper() == "UNO":
                player.said_uno = True
