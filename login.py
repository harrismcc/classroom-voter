#! python3
"""
The `login` module is the main entry point for any client.
The client enters credentials, and if authenticated, enters they main
loop for either students or professors, depending on who they authenticated as.
"""

import socket
import sys
import json
import getpass
from shared.pollTypes import Poll, FreeResponseQuestion
import professor
import client


def prompt_for_ip():
    ip = input("Enter the IP address of the server (eg 192.168.61.1): ")
    port = int(input("Enter the port of the server (eg 1500): "))
    return (ip, port)

def send_msg(clientSocket, msg):
    try:
        clientSocket.send(str.encode(json.dumps(msg)))
    except socket.error as e:
        print('Failed to send message: ' + str(e))

def attempt_login(clientSocket, username, password):
    msg = {
        "endpoint": "Login",
        "Arguments": {
            "username": username,
            "password": password
        }
    }
    send_msg(clientSocket, msg)
    response = json.loads(clientSocket.recv(2048).decode())
    return response

def reset_password(clientSocket, username, password, new_password):
    msg = {
        "endpoint": "Reset_password",
        "Arguments": {
            "username": username,
            "old_password": password,
            "new_password": new_password
        }
    }
    send_msg(clientSocket, msg)


def main():
    if len(sys.argv)!=1 and len(sys.argv)!= 3: # either need no args or both ip and port
        print("usage: python3 %s or python3 %s <server-ip> <server-port>" % sys.argv[0])
        quit(1)
    ip = None
    port = None

    print("#"*80)
    print('\t\t\tLog in to classroom voter')
    print("#"*80)
    
    if len(sys.argv) == 3:
        ip = sys.argv[1]
        port = int(sys.argv[2])
    else:
        ip, port = prompt_for_ip()

    clientSocket = socket.socket()
    try:
        clientSocket.connect((ip, port))
        print('Successful Connection')
    except socket.error as e:
        print('Failed Connection: ' + str(e))
        return


    while True:
        username = input("Enter username: ")
        password = getpass.getpass()
        result = attempt_login(clientSocket, username, password)
        if result['Arguments']['result'] == 'success' or result['Arguments']['result'] == 'must reset':
            break
        print('Invalid credentials. Try again.')
    
    if result['Arguments']['result'] == 'must reset':
        new_password = getpass.getpass(prompt="Please choose a new password: ")
        reset_password(clientSocket, username, password, new_password)

    if result['Arguments']['account_type'] == 'student':
        client.main(clientSocket)
    elif result['Arguments']['account_type'] == 'professor':
        professor.main(clientSocket)

if __name__ == "__main__":
    main()
