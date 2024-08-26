import socket
import threading

import pygame

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

# Global variables to store opponent's state
opp_paddle = pygame.Rect(WIDTH * 3 // 4 - PADDLE_WIDTH // 2, HEIGHT - 30, PADDLE_WIDTH, PADDLE_HEIGHT)
opp_ball = pygame.Rect(WIDTH * 3 // 4, HEIGHT // 2, BALL_RADIUS, BALL_RADIUS)

def handle_server():

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', 5555))
    server.listen(2)
    print("Server started, waiting for connections...")
    clients = []
#running = True
    while True:
        client_socket, addr = server.accept()
        print("waiting for connections...")
        client_id = len(clients) + 1
        print(f"Client {client_id} connected from {addr}")
        clients.append(client_socket)
        client_handler = threading.Thread(target=handle_client, args=(client_socket, client_id))
        client_handler.start()
    
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



server_handler = threading.Thread(target=handle_server)
server_handler.start()


running = True

while True :
    # print("loop game")
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    if running == False :
        break   
    pygame.display.flip()
    pygame.time.Clock().tick(60)

pygame.quit()



#game_board_handler.join()



#clients = []
#running = True
#while True:
#    pygame.time.delay(2000)
#    for event in pygame.event.get():
#        if event.type == pygame.QUIT:
#            running = False
#    if running == False :
#        print("Quit")
#        break
#    client_socket, addr = server.accept()
#    print("waiting for connections...")
#    client_id = len(clients) + 1
#    print(f"Client {client_id} connected from {addr}")
#    clients.append(client_socket)
#    client_handler = threading.Thread(target=handle_client, args=(client_socket, client_id))
#    client_handler.start()
  