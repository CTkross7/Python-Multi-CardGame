# card.py
from enum import Enum

class Color(Enum):
    RED = "Red"
    YELLOW = "Yellow"
    GREEN = "Green"
    BLUE = "Blue"
    WILD = "Wild"

class CardType(Enum):
    NUMBER = "Number"
    SKIP = "Skip"
    REVERSE = "Reverse"
    DRAW_TWO = "Draw Two"
    WILD = "Wild"
    WILD_DRAW_FOUR = "Wild Draw Four"

class Card:
    def __init__(self, color, card_type, value=None):
        self.color = color
        self.card_type = card_type
        self.value = value  # 숫자 카드일 경우만 사용

    def is_playable(self, top_card, current_color):
        if self.color == Color.WILD:
            return True
        return (
            self.color == current_color or
            self.card_type == top_card.card_type or
            self.value == top_card.value
        )

    def __str__(self):
        if self.card_type == CardType.NUMBER:
            return f"{self.color.value} {self.value}"
        return f"{self.color.value} {self.card_type.value}"