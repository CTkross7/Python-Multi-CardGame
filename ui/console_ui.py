import os
import sys
import time
import shutil


class Color:
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RESET = "\033[0m"
    CLEAR = "\033[2J\033[H"


class ConsoleUI:

    # =====================
    # 기본
    # =====================
    @staticmethod
    def clear():
        print(Color.CLEAR, end="")

    @staticmethod
    def term_width():
        return shutil.get_terminal_size((100, 20)).columns

    # =====================
    # 배너
    # =====================
    @staticmethod
    def banner(text):
        w = ConsoleUI.term_width() - 2
        print(Color.CYAN + Color.BOLD)
        print("╔" + "═" * w + "╗")
        print("║" + text.center(w) + "║")
        print("╚" + "═" * w + "╝")
        print(Color.RESET)

    # =====================
    # 섹션
    # =====================
    @staticmethod
    def section(title):
        w = ConsoleUI.term_width()
        print(Color.BOLD + Color.BLUE + f"\n[{title}]".ljust(w, "─") + Color.RESET)

    # =====================
    # 메시지
    # =====================
    @staticmethod
    def info(msg):
        print(Color.GREEN + "▶ " + msg + Color.RESET)

    @staticmethod
    def warn(msg):
        print(Color.YELLOW + "⚠ " + msg + Color.RESET)

    @staticmethod
    def error(msg):
        print(Color.RED + "✖ " + msg + Color.RESET)

    # =====================
    # 턴 강조
    # =====================
    @staticmethod
    def highlight_turn(turn_name, is_me):
        if is_me:
            print(Color.BOLD + Color.GREEN + f"\n👉 현재 턴: {turn_name} (당신)" + Color.RESET)
        else:
            print(Color.YELLOW + f"\n⏳ 현재 턴: {turn_name}" + Color.RESET)

    # =====================
    # 카드 표현
    # =====================
    @staticmethod
    def card(c):
        if c["type"] == "NUMBER":
            return f"{c['color']} {c['value']}{Color.RESET}"
        return f"{c['color']} {c['type']}{Color.RESET}"

    # =====================
    # 카드 그리드
    # =====================
    @staticmethod
    def grid(items, formatter, cols=6):
        w = ConsoleUI.term_width()
        col_w = w // cols

        for i, item in enumerate(items):
            txt = formatter(item)
            print(txt.ljust(col_w), end="")
            if (i + 1) % cols == 0:
                print()
        print()

    # =====================
    # 타이머 바
    # =====================
    @staticmethod
    def timer_bar(left, total, width=30):
        ratio = max(0, min(1, left / total))
        filled = int(ratio * width)
        bar = "█" * filled + "░" * (width - filled)

        color = Color.GREEN
        if ratio < 0.5:
            color = Color.YELLOW
        if ratio < 0.25:
            color = Color.RED

        print(color + f"[{bar}] {left}s" + Color.RESET)

    # =====================
    # 깜빡임 (UNO 경고)
    # =====================
    @staticmethod
    def blink(text, color=Color.RED, times=2):
        for _ in range(times):
            print(color + Color.BOLD + text + Color.RESET)
            time.sleep(0.2)
            ConsoleUI.clear()
