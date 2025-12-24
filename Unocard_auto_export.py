import cv2
import numpy as np
from PIL import Image
import os

# =========================
# 설정
# =========================
IMAGE_PATH = "uno_cards.png"
OUTPUT_DIR = "output"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# 카드 순서 (좌→우, 상→하 기준)
CARD_ORDER = [
    # Wild / Back
    ("WILD", "BACK"),
    ("WILD", "WILD"), ("WILD", "WILD"), ("WILD", "WILD"),
    ("WILD", "WILD"), ("WILD", "WILD"),
    ("WILD", "WILD_DRAW_FOUR"), ("WILD", "WILD_DRAW_FOUR"),
    ("WILD", "WILD_DRAW_FOUR"), ("WILD", "WILD_DRAW_FOUR"),
    ("WILD", "WILD_DRAW_FOUR"), ("WILD", "WILD_DRAW_FOUR"),
    ("WILD", "BACK"),

    # Yellow
    *[("YELLOW", str(i)) for i in [1,2,3,4,5,6,7,8,9,0]],
    ("YELLOW", "DRAW_TWO"), ("YELLOW", "SKIP"), ("YELLOW", "REVERSE"),

    # Red
    *[("RED", str(i)) for i in [1,2,3,4,5,6,7,8,9,0]],
    ("RED", "DRAW_TWO"), ("RED", "SKIP"), ("RED", "REVERSE"),

    # Blue
    *[("BLUE", str(i)) for i in [1,2,3,4,5,6,7,8,9,0]],
    ("BLUE", "DRAW_TWO"), ("BLUE", "SKIP"), ("BLUE", "REVERSE"),

    # Green
    *[("GREEN", str(i)) for i in [1,2,3,4,5,6,7,8,9,0]],
    ("GREEN", "DRAW_TWO"), ("GREEN", "SKIP"), ("GREEN", "REVERSE"),
]

# =========================
# 이미지 로드
# =========================
img = cv2.imread(IMAGE_PATH)
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# 흰 테두리 기준 이진화
_, thresh = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY_INV)

# 컨투어 검출
contours, _ = cv2.findContours(
    thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
)

# 카드 후보만 필터링
cards = []
for cnt in contours:
    x, y, w, h = cv2.boundingRect(cnt)
    area = w * h

    # 카드 크기 범위 필터 (이미지에 맞춰 자동 안정화)
    if area > 20000 and h > w:
        cards.append((x, y, w, h))

# 좌→우, 상→하 정렬
cards.sort(key=lambda b: (b[1] // 100, b[0]))

print(f"Detected cards: {len(cards)}")

# =========================
# 카드 저장
# =========================
for i, (x, y, w, h) in enumerate(cards):
    if i >= len(CARD_ORDER):
        break

    color, name = CARD_ORDER[i]

    if name == "BACK":
        continue

    folder = os.path.join(OUTPUT_DIR, color)
    os.makedirs(folder, exist_ok=True)

    card_img = img[y:y+h, x:x+w]
    card_img = cv2.cvtColor(card_img, cv2.COLOR_BGR2RGB)

    pil_img = Image.fromarray(card_img)

    path = os.path.join(folder, f"{color}_{name}.png")
    pil_img.save(path)  # ✅ 자동 덮어쓰기

    print(f"Saved: {path}")

print("✅ 카드 자동 추출 완료")
