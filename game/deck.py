import random
from .card import Card, Color, CardType

class Deck:
    def __init__(self):
        self.cards = []
        self._build()
        random.shuffle(self.cards)

    def _build(self):
        for color in [Color.RED, Color.YELLOW, Color.GREEN, Color.BLUE]:
            for n in range(10):
                self.cards.append(Card(color, CardType.NUMBER, n))
            for _ in range(2):
                self.cards.append(Card(color, CardType.SKIP))
                self.cards.append(Card(color, CardType.REVERSE))
                self.cards.append(Card(color, CardType.DRAW_TWO))

        for _ in range(4):
            self.cards.append(Card(Color.WILD, CardType.WILD))
            self.cards.append(Card(Color.WILD, CardType.WILD_DRAW_FOUR))

    def draw(self):
        return self.cards.pop()
