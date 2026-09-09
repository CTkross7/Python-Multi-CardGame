# Python-Multi-CardGame

Python Socket을 활용한 LAN 환경 멀티플레이어 **UNO 카드 게임** 프로젝트입니다.  
TCP 기반의 실시간 게임 상태 동기화와 UDP 브로드캐스트 기반의 서버 자동 탐색(Discovery) 시스템을 구현하여, 별도의 IP 입력 없이도 편리하게 네트워크 게임을 즐길 수 있습니다.

---

## 📌 원저작자 및 라이선스 표기 (Credits)

본 프로젝트는 Ben Nuttall의 [bennuttall/uno](https://github.com/bennuttall/uno) 프로젝트를 기반으로 네트워크 기능 및 서버 구조를 확장·재설계한 작품입니다.  
원저작자의 오픈소스 라이선스 및 저작권을 준수하며 제작되었습니다.

---

## ✨ 주요 기능 (Key Features)

* **서버 권위(Server-Authoritative) 검증 구조**
  * 턴 순서 유효성, 실제 카드 소유 여부, 카드 인덱스 범위(`0 <= idx < len(hand)`)를 서버에서 검증하여 클라이언트의 부정 패킷 조작을 차단합니다.
* **UDP 기반 서버 자동 탐색**
  * 동일한 LAN 네트워크 내에 구축된 게임 서버를 브로드캐스트 패킷으로 자동 발견하고 연결합니다.
* **방(Room) 기반 세션 관리 및 자동 cleanup**
  * 방 생성, 비밀번호 설정, 정원 체크(2~4명)를 지원하며, 방 인원이 0명이 되면 메모리에서 자동으로 방을 삭제합니다.
* **AI 자동 채우기 및 단조 증가 PID**
  * 최소 인원 입주시 부족한 플레이어 자리를 AI로 자동 채웁니다.
  * 플레이어 퇴장/재입장 시 ID 충돌이 없도록 단조 증가(Monotonic Increasing) PID 발급 방식을 채택했습니다.
* **고성능 콘솔 모니터링 (ANSI Escape Sequence)**
  * 서버 모니터링 시 `os.system("cls")` 대신 ANSI 이스케이프 코드(`\033[H\033[J`)를 사용하여 화면 깜빡임과 CPU 점유율을 최소화했습니다.
* **턴 타이머 및 콘솔 UI**
  * 각 플레이어의 턴 제한 시간(15초) 카운트다운 및 직관적인 CLI 기반 카드를 제공합니다.

---

## 🏗️ 시스템 아키텍처 (System Architecture)

본 프로젝트는 안정적인 상태 관리를 위해 계층화된 **Client-Server 아키텍처**로 구성되어 있으며, 각 구성 요소의 역할은 다음과 같습니다.

| 계층 (Layer) | 구성 요소 (Component) | 주요 역할 및 기능 |
| :--- | :--- | :--- |
| **Server Root** | **Game Server** | 전체 소켓 바인딩, TCP/UDP 수신 대기 및 모니터링 스레드 관리 |
| **Connection** | **Client Manager** | 클라이언트 접속 시 전용 스레드(`client_thread`)를 생성하여 메뉴 처리 및 소켓 통신 담당 |
| **Session** | **Room Manager** | 생성된 방들의 딕셔너리 관리, 방 정원/비밀번호 검증 및 빈 방 Cleanup 수행 |
| **Room Thread** | **Room Instance** | 독립적인 스레드로 구동되며, 해당 방의 턴 타이머 관리 및 클라이언트 패킷 수신 처리 |
| **Game Logic** | **Game State** | 실제 UNO 게임 규칙(카드 소유, 턴 전환, 바닥 패 계산 등)의 유효성을 최종 검증 및 관리 |

---

## 🌐 네트워크 아키텍처 (Network Architecture)

역할에 따라 TCP와 UDP를 분리한 혼합 통신 방식을 채택했습니다.

| 구분 | 포트 (Port) | 역할 및 설명 |
| :--- | :--- | :--- |
| **TCP** | `9009` | **Game Communication**: 로비 이동, 카드 제출, 턴 동기화 등 핵심 데이터 전송 |
| **UDP** | `9010` | **Server Discovery**: 클라이언트의 서버 자동 탐색 탐지용 브로드캐스트 |

### 서버 자동 탐색 메커니즘 (Discovery Protocol)

```text
Client                       Server
  │                            │
  ├────── UNO_DISCOVER ───────>│ (UDP Broadcast)
  │                            │
  │<── UNO_SERVER:<IP>:<PORT> ─┤ (UDP Unicast)
  │                            │
```

---

## 🔄 흐름도 (Flowcharts)

### 1. 게임 루프 흐름 (Game Loop Flow)

```text
Room Created
     │
     ▼
Waiting Players (인원 대기)
     │
     ├─► (인원 2명 이상 수용 시)
     │
     ▼
Game Start & AI Auto-fill
     │
     ▼
Turn Loop (턴 루프)
     │
     ├───► Send Game State (상태 브로드캐스트)
     │
     ├───► Receive Player Command (서버 권위 검증)
     │
     ├───► Apply Game Logic (규칙 적용)
     │
     └───► Next Turn (턴 전환)
```

### 2. 클라이언트 접속 흐름 (Client Connection Flow)

```text
Client Start
     │
     ▼
UDP Server Discovery (서버 탐색)
     │
     ▼
Receive Server Address (서버 IP/포트 획득)
     │
     ▼
TCP Connection (서버 접속)
     │
     ▼
Main Menu
  ├───► 1. Create Room (방 생성)
  ├───► 2. Join Room (방 참가 - 비밀번호 및 정원 검사)
  └───► 3. Room List (방 목록 조회)
```

---

## 💬 통신 프로토콜 (Message Protocol)

서버와 클라이언트 간의 모든 데이터 전송은 **JSON** 포맷을 기반으로 이루어집니다.  
TCP 스트림 특성상 발생할 수 있는 패킷 뭉침 현상(TCP Packet Sticking)을 방지하기 위해 개행 문자(`\n`)를 구분자(Delimiter)로 사용합니다.

* **패킷 구조**: `<JSON_MESSAGE>\n`

### 메시지 예시 (STATE 패킷)

```json
{
  "type": "STATE",
  "turn": "Player1",
  "top": {
    "color": "RED",
    "value": "5"
  },
  "counts": {
    "Player1": 4,
    "Player2": 2
  },
  "turn_time": 15,
  "turn_left": 12
}
```

---

## 🖥️ 서버 모니터링 출력 예시 (Server Console)

```text
서버 IP: 192.168.0.15:9009
----------------------------------------
[AB12C] UNO ROOM 🔒 2/4 대기중
[Q8X2D] UNO ROOM    4/4 진행중
----------------------------------------
```

---

## 📝 패치 노트 (Patch Notes)

### v1.1.0 (Current)
* **보안 강화**: 서버 권위(Server-Authoritative) 구조 적용 (턴 검증, 카드 인덱스 범위 및 규칙 검사)
* **버그 수정**: 
  * 단조 증가 PID 도입으로 플레이어 재입장 시 발생하던 ID 충돌 문제 해결
  * 방 입장 시 정원 초과(`max_players`) 체크 로직 추가
  * 방 인원 0명 진입 시 메모리 자동 정리(Clean-up) 구문 추가
* **성능 최적화**: 콘솔 모니터링 출력 방식을 ANSI Escape Sequence(`\033[H\033[J`)로 개선

### v1.0.0
* Initial release
* TCP 멀티플레이어 게임 시스템 구축 및 UDP 서버 자동 탐색 구현
* Room 기반 세션 시스템, AI 플레이어, 턴 타이머 및 Console UI 탑재
