# game_state.py
from deck import Deck
from card import Color, CardType

class GameState:
    def __init__(self, players):
        self.players = players
        self.deck = Deck()
        self.discard = []
        self.turn = 0
        self.direction = 1
        self.current_color = None

    def start(self):
        for p in self.players:
            for _ in range(7):
                p.hand.append(self.deck.draw())
        first = self.deck.draw()
        self.discard.append(first)
        self.current_color = first.color

    def next_turn(self, step=1):
        self.turn = (self.turn + step * self.direction) % len(self.players)

    def play_card(self, player, card_idx):
        card = player.hand[card_idx]
        top = self.discard[-1]

        if not card.playable(top, self.current_color):
            return False

        player.hand.pop(card_idx)
        self.discard.append(card)

        if card.color == Color.WILD:
            self.current_color = player.choose_color()
        else:
            self.current_color = card.color

        if card.type == CardType.REVERSE:
            self.direction *= -1
        elif card.type == CardType.SKIP:
            self.next_turn()
        elif card.type == CardType.DRAW_TWO:
            self.next_turn()
            self.players[self.turn].hand += [self.deck.draw(), self.deck.draw()]
        elif card.type == CardType.WILD_DRAW_FOUR:
            self.next_turn()
            for _ in range(4):
                self.players[self.turn].hand.append(self.deck.draw())

        return True