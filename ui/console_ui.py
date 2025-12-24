import os
import shutil

class Color:
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    BOLD = "\033[1m"
    RESET = "\033[0m"
    CLEAR = "\033[2J\033[H"


class ConsoleUI:
    # 배너 최소 / 최대 폭
    MIN_WIDTH = 30
    MAX_WIDTH = 100
    PADDING = 4  # 텍스트 좌우 여백

    @staticmethod
    def section(title):
        width = ConsoleUI._terminal_width()
        print("\n" + Color.CYAN + f"[ {title} ]".ljust(width, "─") + Color.RESET)

    @staticmethod
    def grid(items, render_func, cols=None):
        term_width = ConsoleUI._terminal_width()
        card_width = 14  # 카드 하나당 가로 폭
        if cols is None:
            cols = max(1, term_width // card_width)

        for i, item in enumerate(items):
            print(render_func(item).ljust(card_width), end="")
            if (i + 1) % cols == 0:
                print()
        print()

    @staticmethod
    def blink(text, color=Color.YELLOW, times=3, delay=0.3):
        for _ in range(times):
            print(color + Color.BOLD + text + Color.RESET)
            time.sleep(delay)
            print(Color.CLEAR, end="")
            time.sleep(delay)

    @staticmethod
    def highlight_turn(name, is_me):
        if is_me:
            print(Color.GREEN + Color.BOLD + f"▶▶ 당신의 턴입니다! ({name})" + Color.RESET)
        else:
            print(Color.YELLOW + f"▶ 현재 턴: {name}" + Color.RESET)

    @staticmethod
    def clear():
        print(Color.CLEAR, end="")

    @staticmethod
    def _terminal_width():
        try:
            return shutil.get_terminal_size().columns
        except Exception:
            return 80  # fallback

    @staticmethod
    def banner(text: str):
        term_width = ConsoleUI._terminal_width()

        # 텍스트 길이 기준으로 박스 폭 계산
        text_len = len(text)
        content_width = text_len + ConsoleUI.PADDING * 2

        # 터미널, 최소/최대 폭 고려
        box_width = min(
            max(content_width, ConsoleUI.MIN_WIDTH),
            ConsoleUI.MAX_WIDTH,
            term_width - 2  # 터미널 밖으로 안 나가게
        )

        # 실제 내부 텍스트 영역
        inner_width = box_width - 2

        # 중앙 정렬 (넘치면 자름)
        display_text = text[:inner_width].center(inner_width)

        print(Color.BOLD + Color.CYAN)
        print("╔" + "═" * inner_width + "╗")
        print("║" + display_text + "║")
        print("╚" + "═" * inner_width + "╝")
        print(Color.RESET)

    @staticmethod
    def info(msg):
        print(Color.GREEN + "▶ " + msg + Color.RESET)

    @staticmethod
    def warn(msg):
        print(Color.YELLOW + "⚠ " + msg + Color.RESET)

    @staticmethod
    def error(msg):
        print(Color.RED + "✖ " + msg + Color.RESET)

    @staticmethod
    def card(c):
        # 카드 문자열도 너무 길면 잘라서 출력
        if c["type"] == "NUMBER":
            text = f"{c['color']} {c['value']}"
        else:
            text = f"{c['color']} {c['type']}"

        max_len = ConsoleUI._terminal_width() - 10
        return text[:max_len]
