from logging.config import listen
import socket
import pygame
import threading

pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 1600, 600
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
paddle1 = pygame.Rect(WIDTH // 4 - PADDLE_WIDTH // 2, HEIGHT - 30, PADDLE_WIDTH, PADDLE_HEIGHT)
paddle2 = pygame.Rect(WIDTH * 3 // 4 - PADDLE_WIDTH // 2, HEIGHT - 30, PADDLE_WIDTH, PADDLE_HEIGHT)
paddle_speed = 10

# Ball
BALL_RADIUS = 10
ball = pygame.Rect(WIDTH // 4, HEIGHT // 2, BALL_RADIUS, BALL_RADIUS)
ball_dx, ball_dy = 5, -5

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Global variables to store opponent's state
opp_paddle = pygame.Rect(WIDTH * 3 // 4 - PADDLE_WIDTH // 2, HEIGHT - 30, PADDLE_WIDTH, PADDLE_HEIGHT)
opp_ball = pygame.Rect(WIDTH * 3 // 4, HEIGHT // 2, BALL_RADIUS, BALL_RADIUS)

def handle_client(client_socket, client_id):
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if message:
                print(f"Received from {client_id}: {message}")
                # Relay the message to the other client
                for cs in clients:
                    if cs != client_socket:
                        cs.send(message.encode('utf-8'))
        except:
            print(f"Client {client_id} disconnected")
            clients.remove(client_socket)
            client_socket.close()
            break
        
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('0.0.0.0', 5555))
server.listen(2)
print("Server started, waiting for connections...")

clients = []
client_socket, addr = server.accept()

if listen(2)==0:
    def send_data():
        while True:
            message = f"{paddle2.x},{paddle2.y},{ball.x},{ball.y},{ball_dx},{ball_dy}"
            client.send(message.encode('utf-8'))

    def receive_data():
        global opp_paddle, opp_ball, ball_dx, ball_dy
        while True:
            data = client.recv(1024).decode('utf-8')
            if data:
                p2_x, p2_y, b_x, b_y, b_dx, b_dy = map(int, data.split(','))
                opp_paddle.x = WIDTH // 2 + p2_x
                opp_paddle.y = p2_y
                opp_ball.x = WIDTH // 2 + b_x
                opp_ball.y = b_y
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
        if keys[pygame.K_RIGHT] and paddle1.right < WIDTH // 2:
            paddle1.x += paddle_speed

        ball.x += ball_dx
        ball.y += ball_dy

        if ball.left <= 0 or ball.right >= WIDTH // 2:
            ball_dx = -ball_dx
        if ball.top <= 0 or ball.bottom >= HEIGHT:
            ball_dy = -ball_dy

        if ball.colliderect(paddle1):
            ball_dy = -ball_dy

        screen.fill(BLACK)
        pygame.draw.rect(screen, RED, paddle1)
        pygame.draw.rect(screen, BLUE, opp_paddle)
        pygame.draw.ellipse(screen, WHITE, ball)
        pygame.draw.ellipse(screen, WHITE, opp_ball)

    # Draw the divider
        pygame.draw.line(screen, WHITE, (WIDTH // 2, 0), (WIDTH // 2, HEIGHT))

        pygame.display.flip()
        pygame.time.Clock().tick(60)

    pygame.quit()
    client.close()

    while True:
        client_socket, addr = server.accept()
        client_id = len(clients) + 1
        print(f"Client {client_id} connected from {addr}")
        clients.append(client_socket)
        client_handler = threading.Thread(target=handle_client, args=(client_socket, client_id))
        client_handler.start()