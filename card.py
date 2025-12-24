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

    def serialize(self):
        return {
            "color": self.color.value,
            "type": self.type.value,
            "value": self.value
        }
