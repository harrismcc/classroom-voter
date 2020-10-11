"""
The `client` module is what runs on each individual students machine. It handles the socket
networking that allows students to connect to server polls.
"""
import socket
import os
import sys
import time
sys.path.append("./shared")
from pollTypes import Poll



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
        self.startConnection()

    def startConnection(self):
        """ starts up a connection loop to the server, specified by the host ip and host port """
        clientSocket = socket.socket()

        print('Waiting for Connection To Server')
        try:
            clientSocket.connect((self.host, self.port))
        except socket.error as e:
            print(str(e))
            #quit(1)

        #while True:  
        newPoll = self.getPoll(clientSocket)
        ans = self.answer(newPoll)
        self.sendResponse(ans, clientSocket)

        clientSocket.close()

    def getPoll(self, clientSocket):
        """requests a new poll from the server and returns the object representing it
        
        Args:
            clientSocket: a socket connected to the server
            
        Returns:
            newPoll: a Poll object consisting of the new Poll"""     
        #todo: implement    
        # message = [endpoint to get poll] 
        # clientSocket.send(str.encode(msg))
        # time.sleep(1)
        # response = clientSocket.recv(1024)
        # newPoll = None
        # poll.fromBytes(newPoll, response)
        d = {'question': {'prompt': 'What is your favorite color?', 'answer': None, 'options': [], 'type': 'FreeResponseQuestion'}, 'responses': []}
        poll = Poll.fromDict(d)
        
        return poll

    def answer(self, poll):
        """Prompts the user to answer a poll

        Args:
            poll: a Poll object

        Returns:
            ans: a Response object (the user's response to the poll)"""
        print(poll.getPrompt())
        # can also get from poll.question.getPrompt()
        resp = input("")
        return None
        #todo: turn input into response object
        

    def sendResponse(self, ans, clientSocket):
        """Sends the user's response to a poll to the server

        Args:
            ans: a Response object, the answer to be sent
            clientSocket: the socket with the destination server"""
        #clientSocket.send(ans.toBytes())
        print("pass")
    


def main():
    """ Parses command line arguments and creates a new VoterClient Object
            `usage: python3 nameOfFile.py <host> <host-port>`
    """
    
    #TODO: change this out for argparse
    if len(sys.argv) != 3:
        print("usage: python3 %s <host> <host-port>" % sys.argv[0])
        #quit(1)
        sys.argv.append('127.0.0.1')
        sys.argv.append('8180')
    host = sys.argv[1]
    port = sys.argv[2]


    client = VoterClient(host, port)
    # this initializes a VoterClient object
    # which involves starting the connection to the server
    # in startConnection. from there, everything 
    # happens in the object methods 

    

if __name__ == "__main__":
    main()