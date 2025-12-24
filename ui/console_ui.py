import shutil
import time

class Color:
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    RESET = "\033[0m"
    BOLD = "\033[1m"
    CLEAR = "\033[2J\033[H"

class ConsoleUI:
    @staticmethod
    def clear():
        print(Color.CLEAR, end="")

    @staticmethod
    def banner(text):
        print(Color.BOLD + Color.BLUE + "="*40)
        print(text.center(40))
        print("="*40 + Color.RESET)

    @staticmethod
    def section(text):
        print(Color.BOLD + f"\n[{text}]" + Color.RESET)

    @staticmethod
    def info(text):
        print(Color.GREEN + f"ℹ {text}" + Color.RESET)

    @staticmethod
    def error(text):
        print(Color.RED + f"⚠ {text}" + Color.RESET)

    @staticmethod
    def highlight_turn(turn_name, is_me):
        if is_me:
            print(Color.BOLD + Color.GREEN + f"\n👉 YOUR TURN ({turn_name}) 👈" + Color.RESET)
        else:
            print(Color.YELLOW + f"\n⏳ {turn_name}의 턴..." + Color.RESET)

    @staticmethod
    def card(c_dict):
        # 딕셔너리 형태의 카드 데이터 처리
        color = c_dict["color"]
        ctype = c_dict["type"]
        val = c_dict.get("value")

        c_code = Color.RESET
        if color == "RED": c_code = Color.RED
        elif color == "BLUE": c_code = Color.BLUE
        elif color == "GREEN": c_code = Color.GREEN
        elif color == "YELLOW": c_code = Color.YELLOW
        
        display = str(val) if ctype == "NUMBER" else ctype
        return f"{c_code}[{color} {display}]{Color.RESET}"

    @staticmethod
    def grid(items, formatter, cols=4):
        for i, item in enumerate(items):
            print(formatter(item).ljust(20), end="")
            if (i+1) % cols == 0:
                print()
        print()

    @staticmethod
    def timer_bar(current, total):
        # 게이지 바 출력
        length = 20
        ratio = max(0, min(1, current / total))
        filled = int(ratio * length)
        bar = "█" * filled + "░" * (length - filled)
        print(f"Time: [{bar}] {int(current)}s")