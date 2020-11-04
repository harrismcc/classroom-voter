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
            data = json.loads(clientSocket.recv(1024).decode())

            poll_question = self.getPollQuestion(data)
            if poll_question is not None:
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
        
        try:
            poll_question = PollQuestion.fromDict(data)
            print("you have recieved a new poll")
            return poll_question
        except:
            print("malformed response: ", data)
            return None    
            


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
            
        msg = {
            "endpoint": "Poll_response",
            "Arguments": {
                "poll": response.toDict()
            }
        }
        
        clientSocket.send(json.dumps(msg).encode())
    


def main(clientSocket):

    client = VoterClient(clientSocket)
    # this initializes a VoterClient object
    # which involves starting the connection to the server
    # in startConnection. from there, everything 
    # happens in the object methods 

    

if __name__ == "__main__":
    main()
