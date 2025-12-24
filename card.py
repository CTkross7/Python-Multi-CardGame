# card.py
from enum import Enum

class Color(Enum):
    RED = "RED"
    YELLOW = "YELLOW"
    GREEN = "GREEN"
    BLUE = "BLUE"
    WILD = "WILD"

class CardType(Enum):
    NUMBER = "NUMBER"
    SKIP = "SKIP"
    REVERSE = "REVERSE"
    DRAW_TWO = "DRAW_TWO"
    WILD = "WILD"
    WILD_DRAW_FOUR = "WILD_DRAW_FOUR"

class Card:
    def __init__(self, color, ctype, value=None):
        self.color = color
        self.type = ctype
        self.value = value

    def playable(self, top, current_color):
        if self.color == Color.WILD:
            return True
        return (
            self.color == current_color or
            self.type == top.type or
            self.value == top.value
        )

    # ✅ 이 함수가 누락되어 있었음
    def serialize(self):
        return {
            "color": self.color.value,
            "type": self.type.value,
            "value": self.value
        }

    @staticmethod
    def deserialize(data):
        return Card(
            Color(data["color"]),
            CardType(data["type"]),
            data["value"]
        )

    def __str__(self):
        return f"{self.color.value} {self.type.value} {self.value}"
