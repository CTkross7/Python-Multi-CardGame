# Python-Multi-CardGame

Python Socket 기반 LAN 멀티플레이 UNO 카드 게임입니다.
TCP 기반 게임 상태 동기화와 UDP 브로드캐스트 기반 서버 자동 탐색 시스템을 제공합니다.

---

System Architecture

본 프로젝트는 Client-Server 아키텍처로 구성됩니다.

+------------------+
                        |      Client      |
                        |   (Player #1)    |
                        +---------+--------+
                                  |
                                  | TCP
                                  |
                        +---------v--------+
                        |    Game Server   |
                        |   <SERVER_IP>    |
                        +---------+--------+
                                  |
               +------------------+------------------+
               |                  |                  |
        +------v------+    +------v------+    +------v------+
        |    Room A   |    |    Room B   |    |    Room C   |
        |  GameLoop   |    |  GameLoop   |    |  GameLoop   |
        +-------------+    +-------------+    +-------------+

서버는 여러 개의 Room 인스턴스를 관리하며 각 방은 독립적인 게임 루프를 실행합니다.


---

Network Architecture

본 시스템은 TCP + UDP 혼합 통신 구조를 사용합니다.

UDP Discovery
 Client  -------------------->  Broadcast
                                     |
                                     v
                           +-------------------+
                           |    Game Server    |
                           |   <SERVER_IP>     |
                           +---------+---------+
                                     |
                                     | TCP
                                     |
                              Game Communication


---

Server Discovery Protocol

클라이언트는 서버를 자동으로 찾기 위해 UDP 브로드캐스트를 사용합니다.

Client → Broadcast (UDP)

"UNO_DISCOVER"

서버 응답

Server → Client

"UNO_SERVER:<SERVER_IP>:<PORT>"

포트 정보

TCP  : 9009  (Game Communication)
UDP  : 9010  (Server Discovery)


---

Game Server Internal Structure

서버 내부 구조

+---------------------------------------------------+
|                    Game Server                    |
|---------------------------------------------------|
|                                                   |
|  Client Manager                                   |
|      │                                            |
|      ▼                                            |
|  Room Manager                                     |
|      │                                            |
|      ├─────────────┬─────────────┐                |
|      ▼             ▼             ▼                |
|  Room Instance  Room Instance  Room Instance      |
|      │             │             │                |
|      ▼             ▼             ▼                |
|  Game State     Game State     Game State         |
|                                                   |
+---------------------------------------------------+

각 Room은 독립적인 게임 상태와 플레이어 목록을 관리합니다.


---

Game Loop Flow

게임 루프 구조

Room Created
     |
     v
Waiting Players
     |
     | (>=2 Players)
     v
Game Start
     |
     v
Turn Loop
     |
     +--> Send Game State
     |
     +--> Receive Player Command
     |
     +--> Apply Game Logic
     |
     +--> Next Turn


---

Client Connection Flow

클라이언트 연결 과정

Client Start
     |
     v
UDP Server Discovery
     |
     v
Receive Server Address
     |
     v
TCP Connection
     |
     v
Main Menu
  |       |
  |       +--> Room List
  |
  +--> Create Room
  |
  +--> Join Room


---

Message Protocol

서버와 클라이언트 간 통신은 JSON 기반 메시지 프로토콜을 사용합니다.

패킷 구조

<JSON_MESSAGE>\n

예시 메시지

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
  }
}

개행 문자(\n)는 TCP 스트림에서 패킷 경계를 구분하기 위한 delimiter로 사용됩니다.


---

Example Server Output

실제 서버 실행 예시

UNO SERVER STARTED : <SERVER_IP>:9009

----------------------------------------
[AB12C] UNO ROOM 🔒 2/4 WAITING
[Q8X2D] UNO ROOM    3/4 RUNNING
----------------------------------------

Patch Notes

v1.0.0

Initial release

Features

- TCP multiplayer game system
- UDP server discovery
- Room-based architecture
- AI player support
- Turn timer system
- Console UI
