import socket
import sys

# Get the command-line arguments
hostname = sys.argv[1]
port = int(sys.argv[2])
password = sys.argv[3]

# Create a socket and connect to the server
with socket.socket() as client_socket:
    address = (hostname, port)
    client_socket.connect(address)
    client_socket.send(password.encode())

    # Receive the server's response
    response = client_socket.recv(1024).decode()

    # Print the server's response
    print(response)