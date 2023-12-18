# #!/bin/python3
import socket
import sys
import threading
import signal


# Connection Data
host = '192.168.1.72'
port = 55555

# Starting Server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()
server.settimeout(1)

# Dictionary For Clients and Their Nicknames
clients = {}
shutting_down = False

# Sending Messages To All Connected Clients
def broadcast(message):
    for client in clients:
        client.send(message)

# Handling Messages From Clients
def handle(client):
    global shutting_down
    while not shutting_down:
        try:
            # Broadcasting Messages
            message = client.recv(1024)
            broadcast(message)
        except socket.error:
            # Removing And Closing Clients
            nickname = clients[client]
            del clients[client]
            client.close()
            broadcast('{} left!'.format(nickname).encode('utf-8'))
            break

# Receiving / Listening Function
def receive():
    global shutting_down
    while not shutting_down:
        try:
            # Accept Connection
            client, address = server.accept()
            print("Connected with {}".format(str(address)))

            # Request And Store Nickname
            client.send('NICK'.encode('utf-8'))
            nickname = client.recv(1024).decode('utf-8')
            clients[client] = nickname

            # Print And Broadcast Nickname
            print("Nickname is {}".format(nickname))
            broadcast("{} joined!".format(nickname).encode('utf-8'))
            client.send('Connected to server!'.encode('utf-8'))

            # Start Handling Thread For Client
            thread = threading.Thread(target=handle, args=(client,))
            thread.start()
        except socket.timeout:
            pass


def shutdown_server(signal, frame):
    """Shut down the server."""
    global shutting_down
    shutting_down = True
    print('Shutting down the server...')
    for client in clients:
        client.close()
    server.close()

print("Server if listening...")
receive()

# Wait for all threads to finish
for thread in threading.enumerate():
    if thread is not threading.main_thread():
        thread.join()

sys.exit(0)
