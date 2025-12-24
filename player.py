from card import CardType, Color
import random

class Player:
    def __init__(self, pid, name, conn=None, is_ai=False):
        self.id = pid
        self.name = name
        self.conn = conn
        self.hand = []
        self.is_ai = is_ai

    def dominant_color(self):
        count = {}
        for c in self.hand:
            if c.color != Color.WILD:
                count[c.color] = count.get(c.color, 0) + 1
        return max(count, key=count.get) if count else random.choice(
            [Color.RED, Color.YELLOW, Color.GREEN, Color.BLUE]
        )

    def choose_color(self):
        return self.dominant_color()

    def ai_think(self, game):
        top = game.discard[-1]
        playable = []

        for i, c in enumerate(self.hand):
            if c.playable(top, game.current_color):
                if c.type == CardType.WILD_DRAW_FOUR:
                    if any(x.color == game.current_color for x in self.hand):
                        continue
                playable.append((i, c))

        if not playable:
            return None

        next_player = game.players[game.next_index()]
        if len(next_player.hand) <= 2:
            for i, c in playable:
                if c.type in (
                    CardType.DRAW_TWO,
                    CardType.SKIP,
                    CardType.WILD_DRAW_FOUR
                ):
                    return i

        dominant = self.dominant_color()
        for i, c in playable:
            if c.color == dominant:
                return i

        return playable[0][0]
