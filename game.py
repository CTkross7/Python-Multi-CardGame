# game.py
from card import Color, CardType
from deck import Deck

class UnoGame:
    def __init__(self, players):
        self.players = players
        self.deck = Deck()
        self.discard_pile = []
        self.current_player_index = 0
        self.direction = 1
        self.current_color = None

    def start(self):
        for p in self.players:
            p.draw_card(self.deck, 7)
        first = self.deck.draw()
        self.discard_pile.append(first)
        self.current_color = first.color

    def next_index(self, step=1):
        return (self.current_player_index + step * self.direction) % len(self.players)

    def next_turn(self):
        self.current_player_index = self.next_index()

    def play_card(self, player, card):
        player.hand.remove(card)
        self.discard_pile.append(card)

        if card.color == Color.WILD:
            chosen = player.dominant_color()
            self.current_color = chosen
            print(f"🎨 Color changed to {chosen.value}")
        else:
            self.current_color = card.color

        if card.card_type == CardType.SKIP:
            print("⏭️ Next player skipped!")
            self.current_player_index = self.next_index()

        elif card.card_type == CardType.REVERSE:
            self.direction *= -1
            print("🔄 Direction reversed!")

        elif card.card_type == CardType.DRAW_TWO:
            idx = self.next_index()
            print(f"💥 {self.players[idx].name} draws 2 cards!")
            self.players[idx].draw_card(self.deck, 2)
            self.current_player_index = idx

        elif card.card_type == CardType.WILD_DRAW_FOUR:
            idx = self.next_index()
            print(f"🔥 {self.players[idx].name} draws 4 cards!")
            self.players[idx].draw_card(self.deck, 4)
            self.current_player_index = idx

    def uno_penalty(self, player):
        if len(player.hand) == 1 and not player.called_uno:
            print(f"❗ {player.name} forgot UNO! +2 cards")
            player.draw_card(self.deck, 2)

    def check_win(self, player):
        return len(player.hand) == 0