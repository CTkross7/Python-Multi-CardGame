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
    def __init__(self, color, type_, value=None):
        self.color = color
        self.type = type_
        self.value = value

    def playable(self, top, current_color):
        if self.color == Color.WILD:
            return True
        if self.color == current_color:
            return True
        if self.type == top.type and self.type != CardType.NUMBER:
            return True
        if self.type == CardType.NUMBER and self.value == top.value:
            return True
        return False

    def serialize(self):
        return {
            "color": self.color.value,
            "type": self.type.value,
            "value": self.value
        }
