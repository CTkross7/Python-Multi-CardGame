from PIL import Image
import numpy as np
import os

# =========================
# 설정
# =========================
IMAGE_PATH = "uno_cards.png"
OUTPUT_DIR = "output"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# =========================
# 카드 순서 (좌→우, 상→하)
# =========================
CARD_ORDER = [
    ("WILD", "BACK"),
    ("WILD", "WILD"), ("WILD", "WILD"), ("WILD", "WILD"),
    ("WILD", "WILD"), ("WILD", "WILD"),
    ("WILD", "WILD_DRAW_FOUR"), ("WILD", "WILD_DRAW_FOUR"),
    ("WILD", "WILD_DRAW_FOUR"), ("WILD", "WILD_DRAW_FOUR"),
    ("WILD", "WILD_DRAW_FOUR"), ("WILD", "WILD_DRAW_FOUR"),
    ("WILD", "BACK"),

    *[("YELLOW", str(i)) for i in [1,2,3,4,5,6,7,8,9,0]],
    ("YELLOW", "DRAW_TWO"), ("YELLOW", "SKIP"), ("YELLOW", "REVERSE"),

    *[("RED", str(i)) for i in [1,2,3,4,5,6,7,8,9,0]],
    ("RED", "DRAW_TWO"), ("RED", "SKIP"), ("RED", "REVERSE"),

    *[("BLUE", str(i)) for i in [1,2,3,4,5,6,7,8,9,0]],
    ("BLUE", "DRAW_TWO"), ("BLUE", "SKIP"), ("BLUE", "REVERSE"),

    *[("GREEN", str(i)) for i in [1,2,3,4,5,6,7,8,9,0]],
    ("GREEN", "DRAW_TWO"), ("GREEN", "SKIP"), ("GREEN", "REVERSE"),
]

# =========================
# 이미지 로드
# =========================
img = Image.open(IMAGE_PATH).convert("RGB")
arr = np.array(img)

h, w, _ = arr.shape

# =========================
# 카드 영역 자동 탐지
# =========================
# 흰 배경 기준: 밝은 영역 제외
gray = arr.mean(axis=2)
mask = gray < 240  # 카드 영역

visited = np.zeros_like(mask, dtype=bool)
boxes = []

def flood_fill(x, y):
    stack = [(x, y)]
    minx = maxx = x
    miny = maxy = y

    while stack:
        cx, cy = stack.pop()
        if cx < 0 or cy < 0 or cx >= w or cy >= h:
            continue
        if visited[cy, cx] or not mask[cy, cx]:
            continue

        visited[cy, cx] = True
        minx = min(minx, cx)
        maxx = max(maxx, cx)
        miny = min(miny, cy)
        maxy = max(maxy, cy)

        stack.extend([
            (cx+1, cy), (cx-1, cy),
            (cx, cy+1), (cx, cy-1)
        ])

    return minx, miny, maxx, maxy

for y in range(h):
    for x in range(w):
        if mask[y, x] and not visited[y, x]:
            box = flood_fill(x, y)
            bx, by, ex, ey = box
            area = (ex - bx) * (ey - by)

            # 카드 비율 필터
            if area > 15000 and (ey - by) > (ex - bx):
                boxes.append(box)

# 좌→우, 상→하 정렬
boxes.sort(key=lambda b: (b[1] // 100, b[0]))

print(f"Detected cards: {len(boxes)}")

# =========================
# 카드 저장
# =========================
for i, (x1, y1, x2, y2) in enumerate(boxes):
    if i >= len(CARD_ORDER):
        break

    color, name = CARD_ORDER[i]
    if name == "BACK":
        continue

    folder = os.path.join(OUTPUT_DIR, color)
    os.makedirs(folder, exist_ok=True)

    card = img.crop((x1, y1, x2, y2))
    path = os.path.join(folder, f"{color}_{name}.png")

    card.save(path)  # ✅ 자동 덮어쓰기
    print("Saved:", path)

print("✅ 카드 자동 추출 완료")
