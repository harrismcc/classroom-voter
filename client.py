"""
The `client` module is what runs on each individual students machine. It handles the socket
networking that allows students to connect to server polls.
"""
import socket
import os
import sys
import time
from shared.pollTypes import PollResponse, PollQuestion
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
            quit(1)

        # while True:  
        # newPoll = self.getPoll(clientSocket)
        # ans = self.answer(newPoll)
        # self.sendResponse(ans, clientSocket)
        while True:
            # may want to prompt for user input here,
            # let them look at old responses before 
            # asking for a new poll

            print("Waiting for a poll\n")
            question = self.getPoll(clientSocket)
            if question != None: #question = None if bad response
                response = self.answerPoll(question)
                self.sendResponse(response, clientSocket)    
            time.sleep(1)

        clientSocket.close()
        
    def toString(self):
        return "Client with host: <" + str(self.host) + "> and port: <" + str(self.port) +">"

    def getPoll(self, clientSocket):
        """
        requests a new poll from the server and returns the object representing it
        
        Args:
            clientSocket: a socket connected to the server
            
        Returns:
            newPoll: a PollQuestion object consisting of the new question
        """     
        #todo: error handling
        try:
            response = clientSocket.recv(1024) #recieve a poll (bytestr) from the server
            question = PollQuestion.fromJson(response.decode())

        except:
            print("malformed response: " + response.decode())
            return None    
        else:
            print("you have recieved a new poll")
            return question


    def answerPoll(self, question):
        """
        Prompts the user to answer a poll

        Args:
            poll: a PollQuestion object

        Returns:
            ans: a PollResponse object (the user's response to the poll)
        """
        print(question.getPrompt())
        resp = input("Answer: ")
        return PollResponse(resp)
        

    def sendResponse(self, response, clientSocket):
        """Sends the user's response to a poll to the server

        Args:
            ans: a Response object, the answer to be sent
            clientSocket: the socket with the destination server"""
        #clientSocket.send(ans.toBytes())
        msg = {
            "endpoint": "Poll_response",
            "Arguments": {
                "poll": response.toDict()
            }
        }
        
        clientSocket.send(json.dumps(msg).encode())
    


def main():
    """ Parses command line arguments and creates a new VoterClient Object
            `usage: python3 nameOfFile.py <host> <host-port>`
    """
    
    #TODO: change this out for argparse
    if len(sys.argv)!=1 and len(sys.argv)!= 3: # either need no args or both ip and port
        print("usage: python3 %s or python3 %s <server-ip> <server-port>" % sys.argv[0])
        quit(1)

    host = None
    port = None

    print("#"*80)
    print('\t\t\tWelcome to classroom voter')
    print("#"*80)

    if len(sys.argv) == 3:
        host = sys.argv[1]
        port = sys.argv[2]
    else:
        host = input("Enter the IP address of the server (eg 192.168.61.1): ")
        port = int(input("Enter the port of the server (eg 1500): "))



    client = VoterClient(host, port)
    # this initializes a VoterClient object
    # which involves starting the connection to the server
    # in startConnection. from there, everything 
    # happens in the object methods 

    

if __name__ == "__main__":
    main()
