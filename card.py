from enum import Enum, auto


class Color(Enum):
    RED = "RED"
    BLUE = "BLUE"
    GREEN = "GREEN"
    YELLOW = "YELLOW"
    WILD = "WILD"


class CardType(Enum):
    NUMBER = auto()
    SKIP = auto()
    REVERSE = auto()
    DRAW_TWO = auto()
    WILD = auto()


class Card:
    def __init__(self, color: Color, type_: CardType, value=None):
        self.color = color
        self.type = type_
        self.value = value  # 숫자 카드일 때만 사용

    def is_playable(self, top_card, current_color):
        # 색이 같으면 가능
        if self.color == current_color:
            return True

        # 숫자/기호가 같으면 가능
        if self.type == top_card.type and self.value == top_card.value:
            return True

        # 와일드는 항상 가능
        if self.color == Color.WILD:
            return True

        return False

    def image_name(self):
        """
        텍스처 파일명 반환
        """
        if self.color == Color.WILD:
            return "WILD.png"

        if self.type == CardType.NUMBER:
            return f"{self.color.value}_{self.value}.png"

        return f"{self.color.value}_{self.type.name}.png"

    def __repr__(self):
        if self.type == CardType.NUMBER:
            return f"{self.color.value} {self.value}"
        return f"{self.color.value} {self.type.name}"
