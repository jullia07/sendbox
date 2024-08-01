import pygame
import socket
import threading

# Initialize pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("2 Player Brick Breaker")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Paddle
PADDLE_WIDTH = 100
PADDLE_HEIGHT = 10
paddle1 = pygame.Rect(WIDTH//2 - PADDLE_WIDTH//2, HEIGHT - 30, PADDLE_WIDTH, PADDLE_HEIGHT)
paddle2 = pygame.Rect(WIDTH//2 - PADDLE_WIDTH//2, 20, PADDLE_WIDTH, PADDLE_HEIGHT)
paddle_speed = 10

# Ball
BALL_RADIUS = 10
ball = pygame.Rect(WIDTH//2, HEIGHT//2, BALL_RADIUS, BALL_RADIUS)
ball_dx, ball_dy = 5, -5

# Networking setup
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('localhost', 5555))

def send_data():
    while True:
        message = f"{paddle1.x},{paddle1.y},{ball.x},{ball.y},{ball_dx},{ball_dy}"
        client.send(message.encode('utf-8'))

def receive_data():
    while True:
        data = client.recv(1024).decode('utf-8')
        if data:
            p2_x, p2_y, b_x, b_y, b_dx, b_dy = map(int, data.split(','))
            paddle2.x = p2_x
            paddle2.y = p2_y
            ball.x = b_x
            ball.y = b_y
            global ball_dx, ball_dy
            ball_dx = b_dx
            ball_dy = b_dy

send_thread = threading.Thread(target=send_data)
receive_thread = threading.Thread(target=receive_data)
send_thread.start()
receive_thread.start()

# Main game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and paddle1.left > 0:
        paddle1.x -= paddle_speed
    if keys[pygame.K_RIGHT] and paddle1.right < WIDTH:
        paddle1.x += paddle_speed

    ball.x += ball_dx
    ball.y += ball_dy

    if ball.left <= 0 or ball.right >= WIDTH:
        ball_dx = -ball_dx
    if ball.top <= 0 or ball.bottom >= HEIGHT:
        ball_dy = -ball_dy

    if ball.colliderect(paddle1) or ball.colliderect(paddle2):
        ball_dy = -ball_dy

    screen.fill(BLACK)
    pygame.draw.rect(screen, RED, paddle1)
    pygame.draw.rect(screen, BLUE, paddle2)
    pygame.draw.ellipse(screen, WHITE, ball)
    pygame.display.flip()
    pygame.time.Clock().tick(60)

pygame.quit()
client.close()