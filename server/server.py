import socket
import os
import sys
from _thread import *



def threaded_client(connection):
    connection.send(str.encode('Welcome to the Poll\n'))

    while True:
        data = connection.recv(2048)


        reply = 'Server Says: ' + data.decode('utf-8')
        if not data:
            break

        connection.sendall(str.encode(reply))

    #connection.close()

def main():
    if len(sys.argv) != 2:
        print("usage: python3 %s <port>" % sys.argv[0])
        quit(1)
    port = sys.argv[1]

    serverSocket = socket.socket()
    host = '192.168.86.23'
    port = int(port)
    threadCount = 0

    try:
        serverSocket.bind((host, port))
    except socket.error as e:
        print(str(e))

    print('Waiting for a Connection To Client..')
    serverSocket.listen(5)

    #continuiously accept new connections
    while True:
        client, address = serverSocket.accept()
        print('Connected to: ' + address[0] + ':' + str(address[1]))

        #each individual connection is threaded
        start_new_thread(threaded_client, (client, ))
        threadCount += 1
        print('Thread Number: ' + str(threadCount))
    serverSocket.close()


if __name__ == "__main__":
    main()