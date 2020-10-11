#! python3
import socket
import json
from shared.pollTypes import Poll, FreeResponseQuestion


def prompt_for_poll():
    question_str = input("[Required] Enter your poll question: ")
    answer_str = input("[Optional] Enter your poll answer: ")
    question = FreeResponseQuestion(question_str, answer_str)
    poll = Poll(question)
    return poll


def prompt_for_ip():
    ip = input("Enter the IP address of the server (eg 192.168.61.1): ")
    port = int(input("Enter the port of the server (eg 1500): "))
    return (ip, port)


def send_msg_to_ip(ip, port, msg):
    clientSocket = socket.socket()
    try:
        clientSocket.connect((ip, port))
        clientSocket.send(str.encode(json.dumps(msg)))
        print('Successfully sent poll')
    except socket.error as e:
        print('Failed to send poll: ' + str(e))


def main():
    print("#"*80)
    print('\t\t\tWelcome to classroom voter')
    print("#"*80)

    poll = prompt_for_poll()
    ip, port = prompt_for_ip()
    msg = {
        "endpoint": "Announce_poll",
        "Arguments": {
            "poll": poll.toDict()
        }
    }
    send_msg_to_ip(ip, port, msg)


if __name__ == "__main__":
    main()
