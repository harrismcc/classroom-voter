import socket
import os
import sys
import time


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

        self.startConnection

    def startConnection(self):
        """ starts up a connection loop to the server, specified by the host ip and host port """
        clientSocket = socket.socket()

        print('Waiting for Connection To Server')
        try:
            clientSocket.connect((self.host, self.port))
        except socket.error as e:
            print(str(e))

        while True:
            msg = input('Say Something: ')
            clientSocket.send(str.encode(msg))
            time.sleep(1)
            response = clientSocket.recv(1024)
            print(response.decode('utf-8'))

        clientSocket.close()

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