import time
from .deck import Deck
from .card import Color, CardType

TURN_LIMIT = 20  # 초

class GameState:
    def __init__(self, players):
        self.players = players
        self.deck = Deck()
        self.discard = []
        self.turn = 0
        self.direction = 1
        self.current_color = None
        self.turn_start = time.time()

    def start(self):
        for p in self.players:
            for _ in range(7):
                p.hand.append(self.deck.draw())
        first = self.deck.draw()
        self.discard.append(first)
        self.current_color = first.color
        self.turn_start = time.time()

    def next_turn(self):
        self.turn = (self.turn + self.direction) % len(self.players)
        self.turn_start = time.time()

    def is_timeout(self):
        return time.time() - self.turn_start > TURN_LIMIT

    def play_card(self, player, idx):
        card = player.hand[idx]
        if not card.playable(self.discard[-1], self.current_color):
            return False
        player.hand.pop(idx)
        self.discard.append(card)
        self.current_color = card.color if card.color != Color.WILD else player.choose_color()
        return True
