# main.py
from player import Player
from game import UnoGame

def show_hand(player):
    print("\nYour Hand:")
    for i, c in enumerate(player.hand):
        print(f"[{i}] {c}")

def main():
    players = [
        Player("YOU"),
        Player("AI_1", True),
        Player("AI_2", True),
        Player("AI_3", True),
    ]

    game = UnoGame(players)
    game.start()

    while True:
        player = players[game.current_player_index]
        top = game.discard_pile[-1]

        print("\n" + "=" * 40)
        print(f"Top Card: {top} | Current Color: {game.current_color.value}")
        print(f"Turn: {player.name}")

        player.called_uno = False

        if player.is_ai:
            next_p = players[game.next_index()]
            card = player.choose_card_ai(top, game.current_color, len(next_p.hand))
            if card:
                print(f"{player.name} plays {card}")
                game.play_card(player, card)
                if len(player.hand) == 1:
                    player.called_uno = True
                    print(f"{player.name} calls UNO!")
            else:
                print(f"{player.name} draws a card")
                player.draw_card(game.deck)
        else:
            show_hand(player)
            playable = player.playable_cards(top, game.current_color)

            if not playable:
                print("No playable card. Drawing...")
                player.draw_card(game.deck)
            else:
                choice = input("Choose card index or 'd' to draw: ")
                if choice.lower() == 'd':
                    player.draw_card(game.deck)
                else:
                    idx = int(choice)
                    card = player.hand[idx]
                    game.play_card(player, card)
                    if len(player.hand) == 1:
                        call = input("Call UNO? (y/n): ")
                        if call.lower() == 'y':
                            player.called_uno = True

        game.uno_penalty(player)

        if game.check_win(player):
            print(f"\n🏆 {player.name} WINS THE GAME!")
            break

        game.next_turn()

if __name__ == "__main__":
    main()