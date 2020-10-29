"""
The `professor` module is what runs on the professor's. It handles the socket
networking that allows professors to create new polls and to collect the student
responses from existing ones.
"""
#! python3
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
        print('Successfully sent poll')
    except socket.error as e:
        print('Failed to send poll: ' + str(e))


def main():
    if len(sys.argv)!=1 and len(sys.argv)!= 3: # either need no args or both ip and port
        print("usage: python3 %s or python3 %s <server-ip> <server-port>" % sys.argv[0])
        quit(1)
    ip = None
    port = None

    print("#"*80)
    print('\t\t\tWelcome to classroom voter')
    print("#"*80)
    
    if len(sys.argv) == 3:
        ip = sys.argv[1]
        port = int(sys.argv[2])
    else:
        ip, port = prompt_for_ip()

    clientSocket = socket.socket()
    try:
        clientSocket.connect((ip, port))
        print('Successful Connection')
    except socket.error as e:
        print('Failed Connection: ' + str(e))

    poll = prompt_for_poll()
    msg = {
        "endpoint": "Announce_poll",
        "Arguments": {
            "poll": poll.toDict()
        }
    }
    
    print(msg)
    send_msg(clientSocket, msg)
    
    while True:
        prompt = input("Would you like to collect responses? (y/n)")
        if prompt == "y":
            msg = {
                "endpoint": "Aggregate_poll",
                "Arguments": {}
            }
            send_msg(clientSocket, msg)
            data = json.loads(clientSocket.recv(2048).decode())
            print("Results: ", data)


if __name__ == "__main__":
    main()
