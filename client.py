"""
The `client` module is what runs on each individual students machine. It handles the socket
networking that allows students to connect to server polls.
"""
import socket
import os
import sys
import time
from shared.pollTypes import PollResponse
import json

class VoterClient:
    """
    VoterClient is a client object that handles the socket connection to the teacher server

    Attributes:
        host (string): ip of host to connect to
        port (int): port of host to connet to

    Args:
        host (string): ip of host to connect to
        port (int): port of host to connet to

    """
    def __init__(self, host, port):
        """
        Creates a new VoterClient object

        Args:
            host (string): ip of host to connect to
            port (int): port of host to connet to

        """
        self.host = host
        self.port = int(port)
        
        print(self.toString())

        self.startConnection()

    def startConnection(self):
        """ starts up a connection loop to the server, specified by the host ip and host port """
        clientSocket = socket.socket()

        print('Waiting for Connection To Server')
        try:
            clientSocket.connect((self.host, self.port))
        except socket.error as e:
            print(str(e))

        while True:
            response = clientSocket.recv(1024)
            print(response.decode())
            
            msg = input('Answer: ')
            
            poll_response = PollResponse(msg)
            msg = {
                "endpoint": "Poll_response",
                "Arguments": {
                    "poll": poll_response.toDict()
                }
            }
            
            clientSocket.send(json.dumps(msg).encode())
            time.sleep(1)

        clientSocket.close()
        
    def toString(self):
        return "Client with host: <" + str(self.host) + "> and port: <" + str(self.port) +">"

def main():
    """ Parses command line arguments and creates a new VoterClient Object
            `usage: python3 nameOfFile.py <host> <host-port>`
    """
    
    #TODO: change this out for argparse
    if len(sys.argv) != 3:
        print("usage: python3 %s <host> <host-port>" % sys.argv[0])
        quit(1)
    host = sys.argv[1]
    port = sys.argv[2]

    client = VoterClient(host, port)


    

if __name__ == "__main__":
    main()
