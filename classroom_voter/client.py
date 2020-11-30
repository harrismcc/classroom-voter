"""
The `client` module is what runs on each individual students machine. It handles the socket
networking that allows students to connect to server polls.
"""
import socket
import os
import sys
import time
from classroom_voter.shared.pollTypes import PollResponse, PollQuestion, Poll # pylint: disable=import-error
import json
import datetime

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
        self.currentCourseId = None
        if cli:
            self.startConnection()


    def setCurrentCourseId(self):
        self.currentCourseId = None
        enrolled = self.sendServerEndpoint("Get_enrolled", None)
        if enrolled != None and enrolled["courses"] != [None]:
            out = [str(course["classId"])+" : "+str(course["courseCode"]) for course in enrolled["courses"]]

            print("Enrolled Courses:")
            for line in out: print(line)

            while self.currentCourseId not in [course["classId"] for course in enrolled["courses"]]:
                self.currentCourseId = int(input("Select a course id: "))

    def startConnection(self):
        """ starts up a connection loop to the server, specified by the host ip and host port """

        self.setCurrentCourseId()
        if self.currentCourseId != None:
            while True:
                prompt = input("To view new polls, enter  'vp'. To change course, enter 'cc'. To quit, enter 'quit': ")
                if prompt == 'quit':
                    return
                elif prompt == 'cc':
                    self.setCurrentCourseId()
                elif prompt == "vp":
                    
                    msg = {
                        "endpoint": "Get_next_poll",
                        "Arguments" : {
                            "classId" : self.currentCourseId
                        }
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
                if prompt == "ep":
                    poll_id = input("Enter pollId: ")
                    msg = {
                        "endpoint": "Edit_poll_request",
                        "Arguments": {
                            "pollId": poll_id
                        }
                    }
                    self.clientSocket.send(json.dumps(msg).encode())
                    
                    data = json.loads(self.clientSocket.recv(1024))
                    print(data)
                    
                    arguments = data["Arguments"]
                    result = arguments["result"]
                    poll = arguments["poll"]
                    previous_response = arguments["previousResponse"]
                                                    
                    if result == "failed":
                        print("Edit request failed!")
                        continue
                    if result == "expired":
                        print("Poll has expired, cannot edit!")
                        continue
                    
                    if result == "success":
                        poll_question = self.getPollQuestion(poll)
                        print("Prompt: ", poll_question.getPrompt())
                        print("Previous Response: ", previous_response["responseBody"])
                        
                        updated_str_response = input("Update your response: ")
                        
                        time_submitted = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        
                        msg = {
                            "endpoint": "Update_response",
                            "Arguments": {
                                "pollId": poll_id,
                                "updated_response": PollResponse(updated_str_response).toDict(),
                                "time_submitted": time_submitted
                            }
                        }
                        self.clientSocket.send(json.dumps(msg).encode())
                    
                        data = json.loads(self.clientSocket.recv(1024))
                        print(data)
                else:
                    print("Unrecognized input")
                    continue
        else:
            print("You are not enrolled in any courses!")

        #clientSocket.close()


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
        
        time_submitted = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
        msg = {
            "endpoint": "Poll_response",
            "Arguments": {
                "poll": response.toDict(),
                "pollId": pollId,
                "time-submitted": time_submitted
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
        print(resp)
        try:    
            data = json.loads(resp)
        except json.JSONDecodeError:
            print("JSON decode error (No data) for endpoint ", endpoint)
        
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
