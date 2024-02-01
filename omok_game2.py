# 필요한 라이브러리 및 모듈 임포트
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import eventlet
import pygame
import sys
from threading import Thread

# Flask 애플리케이션 및 SocketIO 초기화
app = Flask(__name__)
socketio = SocketIO(app)

# 게임 관련 변수 초기화
player_turn = 1
board_size = 20
board = [[0] * board_size for _ in range(board_size)]

# Pygame 초기화
pygame.init()

# 창 크기 및 색상 정의
WIDTH, HEIGHT = 800, 800
BLACK, WHITE = (0, 0, 0), (255, 255, 255)
LINE_COLOR = (150, 150, 150)
cell_size = WIDTH // board_size

# 화면 생성
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("오목 게임")

# 플레이어 정보
players = {}

# 게임 로직 관련 함수
def is_valid_move(row, col):
    return 0 <= row < board_size and 0 <= col < board_size and board[row][col] == 0

def switch_turn():
    global player_turn
    player_turn = 3 - player_turn

def check_winner(row, col, player_id):
    directions = [(0, 1), (1, 0), (1, 1), (1, -1)]

    for dr, dc in directions:
        count = 1
        count += count_same_color(row, col, player_id, dr, dc)
        count += count_same_color(row, col, player_id, -dr, -dc)

        if count >= 5:
            return True

    return False

def count_same_color(row, col, player_id, dr, dc):
    count = 0
    r, c = row + dr, col + dc

    while 0 <= r < board_size and 0 <= c < board_size and board[r][c] == player_id:
        count += 1
        r, c = r + dr, c + dc

    return count

# 서버 라우트 설정
@app.route('/')
def index():
    return render_template('index.html')

# 소켓 이벤트 핸들러
@socketio.on('connect')
def handle_connect():
    global player_turn
    player_id = len(players) + 1 # 새로운 연결이 들어올 때마다 고유한 ID 부여
    players[request.sid] = {"id": player_id, "turn": player_turn}
    emit('set_player', {"id": player_id, "turn": player_turn}) # 클라이언트에게 플레이어 정보 전송
    player_turn = 3 - player_turn  # 턴 전환
    emit('set_turn', {"player_id": player_turn}, broadcast=True)  # 모든 클라이언트에게 턴 정보 전달

# 클라이언트가 연결을 해제할 때 호출되는 함수
@socketio.on('disconnect')
def handle_disconnect():
    del players[request.sid]

# 클라이언트가 수를 둘 때 호출되는 함수
@socketio.on('make_move')
def handle_make_move(data):
    row, col, player_id = data['row'], data['col'], data['player_id']

    if is_valid_move(row, col) and player_id == player_turn:
        board[row][col] = player_id
        if check_winner(row, col, player_id):
            emit('game_over', {"winner": player_id}, broadcast=True)
        else:
            switch_turn()
            emit('update_board', {"row": row, "col": col, "player_id": player_id}, broadcast=True)
            emit('set_turn', {"player_id": player_turn}, broadcast=True)

# Pygame 무한 루프를 별도의 스레드에서 실행
def run_game_loop():
    clock = pygame.time.Clock()

    while True:
        pygame.event.pump()  # Pygame 이벤트 루프 업데이트

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # 마우스 클릭 이벤트 처리
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if player_turn == players[request.sid]["turn"]:
                    col = event.pos[0] // cell_size
                    row = event.pos[1] // cell_size
                    # 클라이언트에게 수를 두었다는 정보 전송
                    emit('make_move', {'row': row, 'col': col, 'player_id': players[request.sid]["id"]}) 

        draw_board()
        pygame.display.flip()
        clock.tick(30)  # 30 프레임으로 제한
        pygame.time.delay(10)

        # Flask-SocketIO의 이벤트 루프
        socketio.sleep(0.01)

# 게임 보드 그리기
def draw_board():
    screen.fill(WHITE)

    # 수평선 그리기
    for i in range(board_size + 1):
        pygame.draw.line(screen, LINE_COLOR, (0, i * cell_size), (WIDTH, i * cell_size), 1)

    # 수직선 그리기
    for j in range(board_size + 1):
        pygame.draw.line(screen, LINE_COLOR, (j * cell_size, 0), (j * cell_size, HEIGHT), 1)

    # 돌 그리기
    for row in range(board_size):
        for col in range(board_size):
            if board[row][col] == 1:
                pygame.draw.circle(screen, BLACK, (col * cell_size + cell_size // 2, row * cell_size + cell_size // 2), cell_size // 2 - 5)
            elif board[row][col] == 2:
                pygame.draw.circle(screen, (255, 0, 0), (col * cell_size + cell_size // 2, row * cell_size + cell_size // 2), cell_size // 2 - 5)  # 빨간색으로 수정

# 스레드를 생성하고 Pygame 무한 루프를 실행
pygame_thread = Thread(target=run_game_loop)
pygame_thread.start()

# Flask-SocketIO를 비동기로 실행
if __name__ == "__main__":
    socketio.start_background_task(target=run_game_loop)
    socketio.run(app, host='0.0.0.0', port=5000)
