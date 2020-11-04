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


def prompt_for_poll():
    question_str = input("[Required] Enter your poll question: ")
    answer_str = input("[Optional] Enter your poll answer: ")
    question = FreeResponseQuestion(question_str, answer_str)
    
    args = {
        "startTime" : datetime.date.today(),
        "endTime" : datetime.date.today(),
        "ownerId" : "12345",
        "classId" : "1"
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
        print('Failed to send message: ' + str(e))

def send_poll(clientSocket, poll):
    msg = {
        "endpoint": "Announce_poll",
        "Arguments": {
            "poll": poll.toDict()
        }
    }
    send_msg(clientSocket, msg)

def collect_responses(clientSocket):
    # msg = {
    #     "endpoint": "Aggregate_poll",
    #     "Arguments": {}
    # }
    # send_msg(clientSocket, msg)
    # data = json.loads(clientSocket.recv(2048).decode())
    # return data
    return "pass"

def main(clientSocket):

    while True:
        prompt = input("Would you like to:\n 1: Send a new poll\n 2: Quit\n\n")
 
        if prompt == '1':
            poll = prompt_for_poll()
            send_poll(clientSocket, poll)
        elif prompt == 'cr':
            responses = collect_responses(clientSocket)
            print("Results: ", responses)
        elif prompt == '2':
            print("#"*80)
            print('\t\t\tClosing session')
            print("#"*80)
            return

        else:
            print('Unrecognized input ' + prompt + ". Expected '1', '2'")

if __name__ == "__main__":
    main()
