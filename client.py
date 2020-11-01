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

    Args:
        clientSocket (socket): socket to connect to

    """
    def __init__(self, clientSocket):
        """
        Creates a new VoterClient object

        Args:
            clientSocket (socket): socket to connect to
        """

        self.startConnection(clientSocket)

    def startConnection(self, clientSocket):
        """ starts up a connection loop to the server, specified by the host ip and host port """

        while True:

            print("Waiting for a poll\n")
            data = json.loads(clientSocket.recv(1024).decode()) #recieve a poll (bytestr) from the server

            poll_question = self.getPollQuestion(data)
            if poll_question != None: #question = None if bad response
                response = self.answerPoll(poll_question)
                self.sendResponse(response, clientSocket)    
            time.sleep(1)

        clientSocket.close()
        
    def toString(self):
        return "Client with host: <" + str(self.host) + "> and port: <" + str(self.port) +">"

    def getPollQuestion(self, data):
        """
        requests a new poll from the server and returns the object representing it
        
        Args:
            clientSocket: a socket connected to the server
            
        Returns:
            newPoll: a PollQuestion object consisting of the new question
        """     
        #todo: error handling
        try:
            poll_question = PollQuestion.fromJson(data)
        except:
            print("malformed response: " + data)
            return None    
        else:
            print("you have recieved a new poll")
            return poll_question


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
    


def main(clientSocket):
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



    client = VoterClient(clientSocket)
    # this initializes a VoterClient object
    # which involves starting the connection to the server
    # in startConnection. from there, everything 
    # happens in the object methods 

    

if __name__ == "__main__":
    main()
