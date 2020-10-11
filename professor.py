#! python3
import socket
from shared.pollTypes import Poll
import json


def prompt_for_poll():
    question = input("Enter your poll question: ")
    poll = Poll(question)
    return poll

def prompt_for_ip():
    ip = input("Enter the IP address of the server (eg 192.168.61.1): ")
    port = int(input("Enter the port of the server (eg 1500): "))
    return (ip, port)

def send_msg(clientSocket, msg):
    try:
        clientSocket.send(json.dumps(msg).encode())
        print('Successfully sent poll')
    except socket.error as e:
        print('Failed to send poll: ' + str(e))


def main():
    print("#"*80)
    print('\t\t\tWelcome to classroom voter')
    print("#"*80)
    
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
    
    send_msg(clientSocket, msg)
    
    while True:
        prompt = input("Would you like to collect responses? (y/n)")
        if prompt == "y":
            msg = {
                "endpoint": "Aggregate_poll",
                "Arguments": {}
            }
            send_msg(clientSocket, msg)
            data = clientSocket.recv(2048).decode()
            print("Results: ", data)


if __name__ == "__main__":
    main()
