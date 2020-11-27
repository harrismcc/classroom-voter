"""
The `client` module is what runs on each individual students machine. It handles the socket
networking that allows students to connect to server polls.
"""
import socket
import os
import sys
import time
from shared.pollTypes import PollResponse, PollQuestion, Poll # pylint: disable=import-error
import json

class VoterClient:
    """
    VoterClient is a client object that handles the socket connection to the teacher server

    Args:
        clientSocket (socket): socket to connect to

    """
    def __init__(self, clientSocket, cli=True):
        """
        Creates a new VoterClient object

        Args:
            clientSocket (socket): socket to connect to
        """
        self.clientSocket = clientSocket
        if cli:
            self.startConnection()

    def startConnection(self):
        """ starts up a connection loop to the server, specified by the host ip and host port """

        while True:
            prompt = input("To view new polls, enter  'vp'. To quit, enter 'quit': ")
            if prompt == 'quit':
                break
            if prompt != 'vp':
                print("Unrecognized input")
                continue
            
            msg = {
                "endpoint": "Get_next_poll"
            }
            self.clientSocket.send(json.dumps(msg).encode())
            data = self.clientSocket.recv(1024)
            data = json.loads(data.decode())
            if data is None or data == {}:
                print("No new polls.")
                continue

            poll_question = self.getPollQuestion(data)
            if poll_question is not None:
                response = self.answerPoll(poll_question)
                self.sendResponse(response, data["pollId"])    
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
            poll_question = Poll.fromDict(data)
            print("you have recieved a new poll")
            return poll_question
        except RecursionError:
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
        

    def sendResponse(self, response, pollId):
        """Sends the user's response to a poll to the server

        Args:
            ans: a Response object, the answer to be sent
            clientSocket: the socket with the destination server"""
            
        msg = {
            "endpoint": "Poll_response",
            "Arguments": {
                "poll": response.toDict(),
                "pollId": pollId
            }
        }
        
        self.clientSocket.send(json.dumps(msg).encode())

    def sendServerEndpoint(self, endpoint, data):
        out = {
            'endpoint': endpoint,
            'Arguments': data
        }
        self.clientSocket.send(json.dumps(out).encode())

        #wait for response
        resp = None
        while resp == None:
            resp = self.clientSocket.recv(4096).decode()
        
        try:    
            data = json.loads(resp)
        except json.JSONDecodeError:
            print("JSON decode error (No data)")
        
        return data


def main(clientSocket, userId):
    client = VoterClient(clientSocket, userId)
    # this initializes a VoterClient object
    # which involves starting the connection to the server
    # in startConnection. from there, everything 
    # happens in the object methods 

    

if __name__ == "__main__":
    #main()
    pass
