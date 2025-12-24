import random
from .card import Color, CardType

class Player:
    def __init__(self, pid, name, conn=None, is_ai=False):
        self.id = pid
        self.name = name
        self.conn = conn
        self.hand = []
        self.is_ai = is_ai

    def choose_color(self):
        colors = [c.color for c in self.hand if c.color != Color.WILD]
        return random.choice(colors) if colors else random.choice(list(Color))

    def ai_think(self, game):
        top = game.discard[-1]
        for i, c in enumerate(self.hand):
            if c.playable(top, game.current_color):
                return i
        return None
