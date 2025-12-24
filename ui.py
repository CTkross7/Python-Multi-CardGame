# ui.py
class UI:
    COLORS = {
        "RED": "\033[91m",
        "YELLOW": "\033[93m",
        "GREEN": "\033[92m",
        "BLUE": "\033[94m",
        "RESET": "\033[0m",
        "BOLD": "\033[1m",
    }

    @staticmethod
    def card(card):
        c = UI.COLORS.get(card["color"], "")
        return f"{c}{card['color']} {card['type']} {card.get('value','')}{UI.COLORS['RESET']}"

    @staticmethod
    def banner(text):
        print(f"\n{UI.COLORS['BOLD']}=== {text} ==={UI.COLORS['RESET']}")

    @staticmethod
    def event(text):
        print(f"✨ {text}")
