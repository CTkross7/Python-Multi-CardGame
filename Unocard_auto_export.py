from PIL import Image
import os

# ======================
# 설정
# ======================
IMAGE_PATH = "uno_cards.png"   # 입력 이미지
OUTPUT_DIR = "output"

COLS = 16   # 가로 카드 수
ROWS = 4    # 세로 카드 수

# 카드 순서 정의 (이미지의 실제 배치 순서 기준)
CARD_ORDER = [
    # 1행 (와일드 + 노랑)
    ("WILD", "BACK"),
    ("WILD", "WILD"),
    ("WILD", "WILD"),
    ("WILD", "WILD"),
    ("WILD", "WILD"),
    ("WILD", "WILD"),
    ("WILD", "WILD_DRAW_FOUR"),
    ("WILD", "WILD_DRAW_FOUR"),
    ("WILD", "WILD_DRAW_FOUR"),
    ("WILD", "WILD_DRAW_FOUR"),
    ("WILD", "WILD_DRAW_FOUR"),
    ("WILD", "WILD_DRAW_FOUR"),
    ("WILD", "BACK"),

    ("YELLOW", "1"), ("YELLOW", "2"), ("YELLOW", "3"),

    # 2행 (노랑 + 빨강)
    ("YELLOW", "4"), ("YELLOW", "5"), ("YELLOW", "6"),
    ("YELLOW", "7"), ("YELLOW", "8"), ("YELLOW", "9"),
    ("YELLOW", "0"), ("YELLOW", "DRAW_TWO"), ("YELLOW", "SKIP"),

    ("RED", "REVERSE"),
    ("RED", "1"), ("RED", "2"), ("RED", "3"),

    # 3행 (빨강 + 파랑)
    ("RED", "4"), ("RED", "5"), ("RED", "6"),
    ("RED", "7"), ("RED", "8"), ("RED", "9"),
    ("RED", "0"), ("RED", "DRAW_TWO"), ("RED", "SKIP"),

    ("BLUE", "REVERSE"),
    ("BLUE", "1"), ("BLUE", "2"), ("BLUE", "3"),

    # 4행 (파랑 + 초록)
    ("BLUE", "4"), ("BLUE", "5"), ("BLUE", "6"),
    ("BLUE", "7"), ("BLUE", "8"), ("BLUE", "9"),
    ("BLUE", "0"), ("BLUE", "DRAW_TWO"), ("BLUE", "SKIP"),

    ("GREEN", "REVERSE"),
    ("GREEN", "1"), ("GREEN", "2"), ("GREEN", "3"),
    ("GREEN", "4"), ("GREEN", "5"), ("GREEN", "6"),
    ("GREEN", "7"), ("GREEN", "8"), ("GREEN", "9"),
    ("GREEN", "0"), ("GREEN", "DRAW_TWO"), ("GREEN", "SKIP"),
]

# ======================
# 실행
# ======================
img = Image.open(IMAGE_PATH)
w, h = img.size

card_w = w // COLS
card_h = h // ROWS

os.makedirs(OUTPUT_DIR, exist_ok=True)

index = 0

for row in range(ROWS):
    for col in range(COLS):
        if index >= len(CARD_ORDER):
            break

        color, name = CARD_ORDER[index]
        index += 1

        # BACK 카드 제외 (선택)
        if name == "BACK":
            continue

        # 폴더 생성
        folder = os.path.join(OUTPUT_DIR, color)
        os.makedirs(folder, exist_ok=True)

        # 카드 자르기
        x1 = col * card_w
        y1 = row * card_h
        x2 = x1 + card_w
        y2 = y1 + card_h

        card_img = img.crop((x1, y1, x2, y2))

        filename = f"{color}_{name}.png"
        path = os.path.join(folder, filename)

        card_img.save(path)
        print(f"Saved: {path}")

print("✅ 모든 카드 추출 완료")
