import socket
import threading

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

while True:
    client_socket, addr = server.accept()
    client_id = len(clients) + 1
    print(f"Client {client_id} connected from {addr}")
    clients.append(client_socket)
    client_handler = threading.Thread(target=handle_client, args=(client_socket, client_id))
    client_handler.start()