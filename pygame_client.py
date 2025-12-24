import socket
import pygame
from protocol import decode

HOST = "127.0.0.1"
PORT = 9009

# ======================
# 네트워크 설정
# ======================
sock = socket.socket()
sock.connect((HOST, PORT))
sock.setblocking(False)

buffer = b""
state = None
my_turn = False

# ======================
# pygame 초기화
# ======================
pygame.init()
WIDTH, HEIGHT = 1000, 650
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("UNO Multiplayer")

FONT = pygame.font.SysFont(None, 28)
BIG_FONT = pygame.font.SysFont(None, 40)

clock = pygame.time.Clock()

# 색상 맵
COLOR_MAP = {
    "RED": (220, 60, 60),
    "YELLOW": (220, 220, 60),
    "GREEN": (60, 200, 60),
    "BLUE": (60, 120, 220),
    "WILD": (180, 180, 180),
}

# ======================
# 렌더링
# ======================
def draw():
    screen.fill((30, 30, 30))

    if not state:
        pygame.display.flip()
        return

    # 턴 표시
    turn_color = (0, 255, 0) if my_turn else (255, 255, 255)
    turn_text = BIG_FONT.render(
        f"Turn: {state['turn']}", True, turn_color
    )
    screen.blit(turn_text, (20, 20))

    # 내 턴 강조
    if my_turn:
        alert = BIG_FONT.render("YOUR TURN!", True, (0, 255, 0))
        screen.blit(alert, (400, 20))

    # 바닥 카드
    top = state["top"]
    top_rect = pygame.Rect(440, 120, 120, 160)
    pygame.draw.rect(
        screen,
        COLOR_MAP.get(top["color"], (200, 200, 200)),
        top_rect
    )
    txt = FONT.render(
        f"{top['type']} {top.get('value','')}",
        True,
        (0, 0, 0)
    )
    screen.blit(txt, (top_rect.x + 10, top_rect.y + 70))

    # 플레이어 카드 수
    y = 320
    for name, count in state["counts"].items():
        info = FONT.render(f"{name}: {count}", True, (255, 255, 255))
        screen.blit(info, (20, y))
        y += 25

    # 내 손패
    for i, c in enumerate(state["hand"]):
        rect = pygame.Rect(80 + i * 95, 470, 85, 130)

        # 내 턴 아닐 때 비활성화 느낌
        color = COLOR_MAP.get(c["color"], (200, 200, 200))
        if not my_turn:
            color = tuple(v // 2 for v in color)

        pygame.draw.rect(screen, color, rect)
        pygame.draw.rect(screen, (0, 0, 0), rect, 2)

        txt = FONT.render(
            f"{c['type']} {c.get('value','')}",
            True,
            (0, 0, 0)
        )
        screen.blit(txt, (rect.x + 5, rect.y + 55))

        c["rect"] = rect  # 클릭 판정용

    pygame.display.flip()

# ======================
# 메인 루프
# ======================
running = True

while running:
    clock.tick(60)

    # 네트워크 수신
    try:
        chunk = sock.recv(4096)
        if chunk:
            buffer += chunk
    except BlockingIOError:
        pass

    while b"\n" in buffer:
        raw, buffer = buffer.split(b"\n", 1)
        msg = decode(raw)

        msg_type = msg.get("type")

        if msg_type == "TURN_START":
            my_turn = True

        elif msg_type == "STATE":
            state = msg
            if state["turn"] != "Player0":
                my_turn = False

    # 이벤트 처리
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if (
            event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
            and my_turn
            and state
        ):
            for i, c in enumerate(state["hand"]):
                if c.get("rect") and c["rect"].collidepoint(event.pos):
                    sock.sendall(f"PLAY,{i}\n".encode())
                    my_turn = False
                    break

    draw()

pygame.quit()
sock.close()
