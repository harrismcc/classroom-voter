#! python3
"""
The `professor` module is what runs on the professor's. It handles the socket
networking that allows professors to create new polls and to collect the student
responses from existing ones.
"""

import socket
import sys
import json
from shared.pollTypes import Poll, FreeResponseQuestion
import datetime


currentCourseId = None

def prompt_for_poll():
    question_str = input("[Required] Enter your poll question: ")
    answer_str = input("[Optional] Enter your poll answer: ")
    question = FreeResponseQuestion(question_str, answer_str)
    
    args = {
        "startTime" : datetime.date.today(),
        "endTime" : datetime.date.today(),
        "ownerId" : "12345",
        "classId" : currentCourseId
    }
    
    poll = Poll(question, **args)
    return poll

def prompt_for_ip():
    ip = input("Enter the IP address of the server (eg 192.168.61.1): ")
    port = int(input("Enter the port of the server (eg 1500): "))
    return (ip, port)

def send_msg(clientSocket, msg):
    try:
        clientSocket.send(str.encode(json.dumps(msg)))
    except socket.error as e:
        print("Failed to send message: " + str(e))

def send_poll(clientSocket, poll):
    msg = {
        "endpoint": "Announce_poll",
        "Arguments": {
            "poll": poll.toDict()
        }
    }
    send_msg(clientSocket, msg)

def collect_responses(clientSocket, pollId):
    msg = {
        "endpoint": "Aggregate_poll",
        "Arguments": {
            "pollId" : pollId
        }
    }
    send_msg(clientSocket, msg)
    data = json.loads(clientSocket.recv(2048).decode())
    return data

def getCourses(clientSocket):
    msg = {
        "endpoint" : "Get_enrolled"
    }

    send_msg(clientSocket, msg)
    data = json.loads(clientSocket.recv(2048).decode())
    return data



def main(clientSocket):
    #Get class to interact with
    enrolled = getCourses(clientSocket)
    out = [str(course["classId"])+" : "+str(course["courseCode"]) for course in enrolled["courses"]]

    print("Enrolled Courses:")
    for line in out: print(line)

    global currentCourseId
    while currentCourseId not in [course["classId"] for course in enrolled["courses"]]:
        currentCourseId = int(input("Select a course id: "))

    while True:
        prompt = input("To create a new poll, enter  'np'. To collect responses, enter 'cr'. To quit, enter 'quit': ")
        if prompt == "cr":
            pollId = input("Collect reponses for pollId: ")
            responses = collect_responses(clientSocket, pollId)
            print("Results: ", responses)
        elif prompt == "np":
            poll = prompt_for_poll()
            send_poll(clientSocket, poll)
        elif prompt == "gc":
            test = getCourses(clientSocket)
            print("Classes: ", test)
        elif prompt == "quit":
            print("#"*80)
            print("\t\t\tClosing session")
            print("#"*80)
            return
        else:
            print("Unrecognized input " + prompt + ". Expected 'np', 'cr', or 'quit'")

if __name__ == "__main__":
    main()
