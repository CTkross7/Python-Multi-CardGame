import random

# 색상 상수 정의
COLORS = ['Red', 'Yellow', 'Green', 'Blue']
ALL_COLORS = COLORS + ['Black'] # 와일드 카드는 Black으로 간주

# 특수 카드 타입 정의
TYPES = ['Number', 'Skip', 'Reverse', 'Draw2', 'Wild', 'Wild4']

class Card:
    def __init__(self, color, card_type, value):
        """
        color: 'Red', 'Yellow', 'Green', 'Blue', 'Black'
        card_type: 'Number', 'Skip', 'Reverse', 'Draw2', 'Wild', 'Wild4'
        value: 숫자(0-9) 또는 None (특수카드의 경우)
        """
        self.color = color
        self.type = card_type
        self.value = value

    def __repr__(self):
        # 디버깅용 출력 (예: [Red 7], [Blue Skip], [Black Wild4])
        if self.type == 'Number':
            return f"[{self.color} {self.value}]"
        else:
            return f"[{self.color} {self.type}]"

    def to_dict(self):
        # 네트워크 전송을 위해 객체를 딕셔너리로 변환
        return {"color": self.color, "type": self.type, "value": self.value}

class Deck:
    def __init__(self):
        self.cards = []
        self.build()

    def build(self):
        self.cards = []
        # 1. 색상별 숫자 카드 및 액션 카드 생성
        for color in COLORS:
            # 숫자 0은 색깔별로 1장
            self.cards.append(Card(color, 'Number', 0))
            
            # 숫자 1-9는 색깔별로 2장씩
            for i in range(1, 10):
                self.cards.append(Card(color, 'Number', i))
                self.cards.append(Card(color, 'Number', i))
            
            # 색상 액션 카드 (Skip, Reverse, Draw2)는 색깔별로 2장씩
            for action in ['Skip', 'Reverse', 'Draw2']:
                self.cards.append(Card(color, action, None))
                self.cards.append(Card(color, action, None))

        # 2. 와일드 카드 생성 (색깔 없음 -> Black으로 처리)
        for _ in range(4):
            self.cards.append(Card('Black', 'Wild', None))
            self.cards.append(Card('Black', 'Wild4', None))

    def shuffle(self):
        random.shuffle(self.cards)

    def draw(self):
        # 덱에서 카드 한 장을 뽑음. 덱이 비었으면 None 반환
        if len(self.cards) > 0:
            return self.cards.pop()
        return None

# --- 테스트 코드 (이 파일을 직접 실행했을 때만 작동) ---
if __name__ == "__main__":
    deck = Deck()
    print(f"초기 덱 카드 수: {len(deck.cards)}장 (정상: 108장)")
    
    deck.shuffle()
    print("덱을 섞었습니다.")
    
    print("카드 5장 뽑기 테스트:")
    for i in range(5):
        print(f"{i+1}: {deck.draw()}")