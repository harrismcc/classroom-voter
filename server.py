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
from shared.pollTypes import *

CONNECTION_LIST = []
clients_lock = threading.Lock()

polls = []

def broadcast(msg):
    with clients_lock:
        for c in CONNECTION_LIST:
            c.send(json.dumps(msg).encode())
            
def aggregate_poll():
    # Since there is only one poll right now it will be the first
    # Future there needs to be some sort of poll id
    responses = []
    for response in polls[0].responses:
        responses.append(response.responseBody)
    
    return responses
    
def add_response_to_poll(response):
    poll = polls[0]
    poll.addResponse(response)

def threaded_client(connection):
    """
    Creates a new threaded client connection loop

    Args:
        connection (socket): socket connection to client

    """
    try:
        while True:
            data = json.loads(connection.recv(2048).decode())
            
            print(data)

            if not data:
                break
            
            endpoint = data["endpoint"]
            
            if endpoint == "Announce_poll":
                poll = Poll.fromDict(data["Arguments"]["poll"])
                polls.append(poll)
                outgoing_msg = poll.question.toDict()
                broadcast(json.dumps(outgoing_msg))
                continue
            
            if endpoint == "Poll_response":
                poll_response = PollResponse.fromDict(data["Arguments"]["poll"])
                add_response_to_poll(poll_response)
                continue
            
            if endpoint == "Aggregate_poll":
                outgoing_msg = aggregate_poll()
                broadcast(json.dumps(outgoing_msg))
                continue
                
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
    host = 'localhost'
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
