import socket
import os
import sys
import time
from shared import encryption_tools

def main():

    if len(sys.argv) != 3:
        print("usage: python3 %s <host> <host-port>" % sys.argv[0])
        quit(1)
    host = sys.argv[1]
    port = sys.argv[2]


    clientSocket = socket.socket()

    print('Waiting for Connection To Server')
    try:
        clientSocket.connect((host, int(port)))
    except socket.error as e:
        print(str(e))

    while True:
        msg = input('Say Something: ')
        clientSocket.send(str.encode(msg))
        time.sleep(1)
        response = clientSocket.recv(1024)
        print(response.decode('utf-8'))

    clientSocket.close()

if __name__ == "__main__":
    main()