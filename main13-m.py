import pygame
import socket
import random
import time

# 게임 화면 크기
SCREEN_WIDTH = 1600
SCREEN_HEIGHT = 600
GAP = 30  # 두 화면 사이의 간격

# 블럭 설정 (10x4 배열에 맞게 크기 조정)
BLOCK_ROWS = 4
BLOCK_COLS = 10
BLOCK_GAP = 5  # 블록 사이의 간격

# 각 플레이어의 화면 너비
PLAYER_SCREEN_WIDTH = (SCREEN_WIDTH - GAP) // 2

# 블럭 크기 설정
BLOCK_WIDTH = (PLAYER_SCREEN_WIDTH - (BLOCK_COLS - 1) * BLOCK_GAP) // BLOCK_COLS
BLOCK_HEIGHT = (SCREEN_HEIGHT // 3 - (BLOCK_ROWS - 1) * BLOCK_GAP) // BLOCK_ROWS

PADDLE_WIDTH = 100
PADDLE_HEIGHT = 10
BALL_RADIUS = 10

# 색상 설정
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BORDER_COLOR = (200, 200, 200)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# 공의 최대 속도
BALL_MAX_SPEED = 7

# 게임을 초기화하는 클래스
class BrickBreakerGame:
    def __init__(self, paddle_color, block_colors=None):
        self.blocks = []
        self.block_colors = block_colors if block_colors else []
        self.paddle_color = paddle_color
        self.paddle_pos = [PLAYER_SCREEN_WIDTH // 2 - PADDLE_WIDTH // 2, SCREEN_HEIGHT - 50]
        self.ball_pos = [PLAYER_SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2]
        self.ball_velocity = [random.choice([-5, 5]), -1]  # 공의 초기 속도 (x축 방향 무작위)
        if block_colors is None:
            self.create_blocks(True)
        else:
            self.create_blocks(False)

    def create_blocks(self, make_block_color):
        self.blocks = []
        if make_block_color is True:
            self.block_colors = []
        for row in range(BLOCK_ROWS):
            for col in range(BLOCK_COLS):
                block_x = col * (BLOCK_WIDTH + BLOCK_GAP)
                block_y = row * (BLOCK_HEIGHT + BLOCK_GAP)
                self.blocks.append(pygame.Rect(block_x, block_y, BLOCK_WIDTH, BLOCK_HEIGHT))
                if make_block_color is True:
                    random_color = [random.randint(50, 255) for _ in range(3)]
                    self.block_colors.append(random_color)

    def draw(self, screen, offset_x):
        for i, block in enumerate(self.blocks):
            if i < len(self.block_colors):
                block_rect = pygame.Rect(block.x + offset_x, block.y, BLOCK_WIDTH, BLOCK_HEIGHT)
                pygame.draw.rect(screen, self.block_colors[i], block_rect)
        
        paddle_rect = pygame.Rect(self.paddle_pos[0] + offset_x, self.paddle_pos[1], PADDLE_WIDTH, PADDLE_HEIGHT)
        pygame.draw.rect(screen, self.paddle_color, paddle_rect)
        
        ball_pos_with_offset = [self.ball_pos[0] + offset_x, self.ball_pos[1]]
        pygame.draw.circle(screen, WHITE, ball_pos_with_offset, BALL_RADIUS)

    def move_ball(self):
        self.ball_pos[0] += self.ball_velocity[0]
        self.ball_pos[1] += self.ball_velocity[1]

        # 벽과 충돌 검사
        if self.ball_pos[0] <= 0 or self.ball_pos[0] >= PLAYER_SCREEN_WIDTH - BALL_RADIUS:
            self.ball_velocity[0] = -self.ball_velocity[0]
        if self.ball_pos[1] <= 0:
            self.ball_velocity[1] = -self.ball_velocity[1]

        # 패들과 충돌 검사
        paddle_rect = pygame.Rect(self.paddle_pos[0], self.paddle_pos[1], PADDLE_WIDTH, PADDLE_HEIGHT)
        if paddle_rect.collidepoint(self.ball_pos[0], self.ball_pos[1]):
            # 패들에 맞은 위치에 따라 반사 각도를 결정
            relative_hit_pos = (self.ball_pos[0] - self.paddle_pos[0]) / PADDLE_WIDTH  # 0~1 사이 값
            bounce_angle = (relative_hit_pos - 0.5) * 2  # -1 (왼쪽 끝)에서 1 (오른쪽 끝)까지의 값
            self.ball_velocity[0] = BALL_MAX_SPEED * bounce_angle  # x축 속도 변경
            self.ball_velocity[1] = -self.ball_velocity[1]  # y축 속도 반전

        # 블록과 충돌 검사
        for i, block in enumerate(self.blocks[:]):
            if block.collidepoint(self.ball_pos[0], self.ball_pos[1]):
                self.blocks.pop(i)  # 블록 제거
                self.block_colors.pop(i)  # 해당 블록의 색상도 제거
                self.ball_velocity[1] = -self.ball_velocity[1]
                break  # 충돌이 발생하면 루프를 종료

    def move_paddle(self, direction):
        if direction == "left" and self.paddle_pos[0] > 0:
            self.paddle_pos[0] -= 5
        if direction == "right" and self.paddle_pos[0] < PLAYER_SCREEN_WIDTH - PADDLE_WIDTH:
            self.paddle_pos[0] += 5

# 서버 (호스트) 역할을 하는 클래스
class Server:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind(('0.0.0.0', 5555))
        self.sock.listen(1)
        print("Waiting for a connection...")
        self.conn, self.addr = self.sock.accept()
        print(f"Connected to {self.addr}")

    def send(self, data):
        try:
            self.conn.sendall(data.encode())
        except (socket.error, BrokenPipeError):
            print("Connection lost.")

    def receive(self):
        try:
            return self.conn.recv(1024).decode()
        except (socket.error, BrokenPipeError):
            print("Connection lost.")
            return None

# 클라이언트 역할을 하는 클래스
class Client:
    def __init__(self, server_ip):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((server_ip, 5555))

    def send(self, data):
        try:
            self.sock.sendall(data.encode())
        except (socket.error, BrokenPipeError):
            print("Connection lost.")

    def receive(self):
        try:
            return self.sock.recv(1024).decode()
        except (socket.error, BrokenPipeError):
            print("Connection lost.")
            return None

# 게임 실행 함수
def run_game(is_host, server_ip=None):
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('1:1 Brick Breaker')

    clock = pygame.time.Clock()

    font = pygame.font.SysFont(None, 74)

    if is_host:
        my_game = BrickBreakerGame(RED) 
        connection = Server()
        my_block_colors_str = ','.join([f'{r}-{g}-{b}' for r, g, b in my_game.block_colors])
        connection.send(my_block_colors_str)
    else:
        my_game = BrickBreakerGame(BLUE)
        connection = Client(server_ip)            
        my_block_colors_str = ','.join([f'{r}-{g}-{b}' for r, g, b in my_game.block_colors])
        connection.send(my_block_colors_str)
        
    opponent_block_colors_str = connection.receive()
    if opponent_block_colors_str is None:
        print("Failed to receive block colors. Exiting...")
        return
    
    opponent_block_colors = [[int(c) for c in color.split('-')] for color in opponent_block_colors_str.split(',')]
    
    opponent_game = BrickBreakerGame(BLUE if is_host else RED, opponent_block_colors)

    countdown = 5
    start_time = time.time()

    running = True
    game_started = False
    game_over = False
    my_result = None  # 승리("WIN") 또는 패배("LOSE") 상태

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        if not game_started:
            current_time = time.time()
            elapsed_time = current_time - start_time
            countdown = max(0, 5 - int(elapsed_time))

            screen.fill(BLACK)
            countdown_text = font.render(f"Starting in {countdown}", True, WHITE)
            screen.blit(countdown_text, (SCREEN_WIDTH // 2 - countdown_text.get_width() // 2, SCREEN_HEIGHT // 2 - countdown_text.get_height() // 2))
            pygame.display.flip()

            if countdown <= 0:
                game_started = True
                start_time = time.time()  # 게임 시작 시간 초기화

        if game_started and not game_over:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                my_game.move_paddle("left")
            if keys[pygame.K_RIGHT]:
                my_game.move_paddle("right")

            # 공이 화면에서 사라지면 패배 처리
            if my_game.ball_pos[1] >= (SCREEN_HEIGHT-49) :
                print("Ball out of screen. You lose!")
                my_result = "LOSE"
                connection.send("WIN")  # 상대방에게 승리 메시지 전송
                game_over = True
                continue
            else:
                # 패들과 공의 위치를 상대에게 보냄
                paddle_data = f"{my_game.paddle_pos[0]},{my_game.ball_pos[0]},{my_game.ball_pos[1]}"
                connection.send(paddle_data)
                opponent_data = connection.receive()

                # 게임 종료 상태인지 확인
                if "WIN" in opponent_data or "LOSE" in opponent_data : #opponent_data in ["WIN", "LOSE"]:
                    print(f"Received game result: {opponent_data}")
                    my_result = "LOSE" if "LOSE" in opponent_data else "WIN"
                    game_over = True
                    continue
                else:
                    try:
                        # 상대방의 패들과 공의 위치를 처리
                        opponent_paddle_x, opponent_ball_x, opponent_ball_y = map(int, opponent_data.split(','))
                        opponent_game.paddle_pos[0] = opponent_paddle_x
                        opponent_game.ball_pos = [opponent_ball_x, opponent_ball_y]
                    except ValueError as e:
                        print(f"Error parsing opponent data: {opponent_data}. Error: {e}")
                        continue

            my_game.move_ball()

            screen.fill(BLACK)

            my_game.draw(screen, 0)
            opponent_game.draw(screen, PLAYER_SCREEN_WIDTH + GAP)

            pygame.draw.rect(screen, BORDER_COLOR, pygame.Rect(0, 0, PLAYER_SCREEN_WIDTH, SCREEN_HEIGHT), 5)
            pygame.draw.rect(screen, BORDER_COLOR, pygame.Rect(PLAYER_SCREEN_WIDTH + GAP, 0, PLAYER_SCREEN_WIDTH, SCREEN_HEIGHT), 5)

            pygame.draw.rect(screen, BLACK, pygame.Rect(PLAYER_SCREEN_WIDTH, 0, GAP, SCREEN_HEIGHT))

            pygame.display.flip()
            clock.tick(60)

        if game_over:
            screen.fill(BLACK)
            result_text = font.render(my_result, True, WHITE)
            screen.blit(result_text, (SCREEN_WIDTH // 2 - result_text.get_width() // 2, SCREEN_HEIGHT // 2 - result_text.get_height() // 2))
            pygame.display.flip()
            print(f"Game result: {my_result}")

    pygame.quit()

if __name__ == "__main__":
    mode = input("Enter 'host' to host the game or 'join' to join: ")
    if mode == "host":
        run_game(is_host=True)
    else:
        server_ip = input("Enter server IP: ")
        run_game(is_host=False, server_ip=server_ip)
