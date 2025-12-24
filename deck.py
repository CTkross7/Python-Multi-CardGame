import random
from card import Card, Color, CardType


class Deck:
    def __init__(self):
        self.cards = []
        self._build()
        self.shuffle()

    def _build(self):
        colors = [Color.RED, Color.BLUE, Color.GREEN, Color.YELLOW]

        # 숫자 카드 (0~9)
        for color in colors:
            for num in range(10):
                self.cards.append(Card(color, CardType.NUMBER, num))
                if num != 0:
                    self.cards.append(Card(color, CardType.NUMBER, num))

            # 특수 카드
            for _ in range(2):
                self.cards.append(Card(color, CardType.SKIP))
                self.cards.append(Card(color, CardType.REVERSE))
                self.cards.append(Card(color, CardType.DRAW_TWO))

        # 와일드 카드 (색 지정 없는 검정)
        for _ in range(4):
            self.cards.append(Card(Color.WILD, CardType.WILD))

    def shuffle(self):
        random.shuffle(self.cards)

    def draw(self):
        if not self.cards:
            raise RuntimeError("Deck is empty")
        return self.cards.pop()
