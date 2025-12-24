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

    def next_index(self, step=1):
        return (self.turn + step * self.direction) % len(self.players)

    def next_turn(self):
        self.turn = self.next_index()

    def play_card(self, player, idx):
        card = player.hand[idx]
        if not card.playable(self.discard[-1], self.current_color):
            return False

        player.hand.pop(idx)
        self.discard.append(card)

        self.current_color = (
            player.choose_color() if card.color == Color.WILD else card.color
        )

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

    def ai_turn(self):
        player = self.players[self.turn]
        idx = player.ai_think(self)

        if idx is None:
            player.hand.append(self.deck.draw())
            return f"{player.name} draws"

        card = player.hand[idx]
        self.play_card(player, idx)
        return f"{player.name} plays {card.color.value} {card.type.value}"
