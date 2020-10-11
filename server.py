"""
The `server` module handles the socket networking with the clients, placing them each into
their own threaded connection.
"""
import socket
import os
import sys
import json
from _thread import *
from threading import Thread
import threading

CONNECTION_LIST = []
clients_lock = threading.Lock()

answers = []

def broadcast(msg):
    with clients_lock:
        for c in CONNECTION_LIST:
            c.sendall(msg.encode())
            
def aggregate_poll():
    msg = {
        "responses": answers
    }
    return msg

def threaded_client(connection):
    """
    Creates a new threaded client connection loop

    Args:
        connection (socket): socket connection to client

    """
    try:
        while True:
            data = json.loads(connection.recv(2048).decode())

            if not data:
                break
            
            endpoint = data["endpoint"]
            print(data)
            
            if endpoint == "Announce_poll":
                outgoing_msg = data["Arguments"]["poll"]["question"]
                broadcast(outgoing_msg)
            elif endpoint == "Poll_response":
                answers.append(data["Arguments"]["poll"]["question"])
            elif endpoint == "Aggregate_poll":
                outgoing_msg = aggregate_poll()
                broadcast(json.dumps(outgoing_msg))
                
    finally:
        with clients_lock:
            CONNECTION_LIST.remove(connection)
            connection.close()
    

def main():
    """ Accepts incoming connections from clients and puts each client connection in a new thread """
    #TODO: Change this out for argparse
    if len(sys.argv) != 2:
        print("usage: python3 %s <port>" % sys.argv[0])
        quit(1)
    port = sys.argv[1]

    serverSocket = socket.socket()
    host = '127.00.00.1'
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
        
        with clients_lock:
            CONNECTION_LIST.append(client)
                
        print('Connected to: ' + address[0] + ':' + str(address[1]))

        #each individual connection is threaded
        start_new_thread(threaded_client, (client, ))
        threadCount += 1
        print('Thread Number: ' + str(threadCount))
    serverSocket.close()


if __name__ == "__main__":
    main()
