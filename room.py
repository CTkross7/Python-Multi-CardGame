import random, string
from game.game_state import GameState
from game.player import Player

class Room:
    def __init__(self, max_players, password=None):
        self.code = "".join(random.choices(string.ascii_uppercase + string.digits, k=5))
        self.password = password
        self.max_players = max_players
        self.players = []
        self.game = None
        self.started = False

    def check_password(self, pw):
        return self.password == pw

    def add_player(self, player):
        if self.started or len(self.players) >= self.max_players:
            return False
        self.players.append(player)
        return True

    def can_start(self):
        return len(self.players) >= 2

    def start_game(self):
        while len(self.players) < self.max_players:
            self.players.append(
                Player(
                    1000 + len(self.players),
                    f"AI{len(self.players)}",
                    is_ai=True
                )
            )
        self.game = GameState(self.players)
        self.game.start()
        self.started = True
