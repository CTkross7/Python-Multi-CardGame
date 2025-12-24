# player.py
from card import CardType, Color
import random

class Player:
    def __init__(self, pid, name, conn=None, is_ai=False):
        self.id = pid
        self.name = name
        self.conn = conn
        self.hand = []
        self.is_ai = is_ai
        self.called_uno = False

    def choose_color(self):
        counts = {}
        for c in self.hand:
            if c.color != Color.WILD:
                counts[c.color] = counts.get(c.color, 0) + 1
        return max(counts, key=counts.get) if counts else random.choice(
            [Color.RED, Color.YELLOW, Color.GREEN, Color.BLUE]
        )