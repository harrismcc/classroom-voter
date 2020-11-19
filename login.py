#!/usr/bin/env python3
"""
The `login` module is the main entry point for any client.
The client enters credentials, and if authenticated, enters they main
loop for either students or professors, depending on who they authenticated as.
"""

import socket
import os
import sys
import json
import getpass
from shared.pollTypes import Poll, FreeResponseQuestion
import professor
import client

class LoginTools(object):
    def __init__(self, ip, port, cli=False):
        self.ip = ip
        self.port = port
        self.cli = cli

        self.clientSocket = socket.socket()
        self.clientSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self.clientSocket.connect((self.ip, self.port))
            if self.cli: print('Successful Connection')
            self.connected = True
        except socket.error as e:
            self.connected = False
            if self.cli: print('Failed Connection: ' + str(e))
            return


        if cli:
            self.main()

    def send_msg(self, msg):
        try:
            self.clientSocket.send(str.encode(json.dumps(msg)))
        except socket.error as e:
            if self.cli: print('Failed to send message: ' + str(e))

    def attempt_login(self, username, password):
        msg = {
            "endpoint": "Login",
            "Arguments": {
                "username": username,
                "password": password
            }
        }
        self.send_msg(msg)
        response = json.loads(self.clientSocket.recv(2048).decode())
        return response

    def reset_password(self, username, password, new_password):
        msg = {
            "endpoint": "Reset_password",
            "Arguments": {
                "username": username,
                "old_password": password,
                "new_password": new_password
            }
        }
        self.send_msg(msg)
        
    def recover_password(self, username):
        msg = {
            "endpoint": "Recover_password",
            "Arguments" : {
                "username" : username
            }
        }
        self.send_msg(msg)
        response = json.loads(self.clientSocket.recv(2048).decode())
        return response


    def main(self):
        while True:
            login_action = input("Login or Forgot Password: ")
            if login_action == "Login":
                username = input("Enter username: ")
                password = self.safe_prompt_for_password()
                result = self.attempt_login(username, password)
                if result['Arguments']['result'] == 'success' or result['Arguments']['result'] == 'must reset':
                    break
                else:
                    print('Invalid credentials. Try again.')
                    
            if login_action == "Forgot Password":
                username = input("Enter username: ")
                result = self.recover_password(username)
                if result['Arguments']['result'] == 'success':
                    print('Password Recovery Succeeded')
                else:
                    print('Password Recovery Failed. Try again.')
                
        if result['Arguments']['result'] == 'must reset':
            new_password = self.safe_prompt_for_password("Please choose a new password:")
            self.reset_password(username, password, new_password)
        
        if result['Arguments']['account_type'] == 'students':
            client.main(self.clientSocket, result['Arguments']['username'])
        elif result['Arguments']['account_type'] == 'professors':
            professor.main(self.clientSocket)
        
    def safe_prompt_for_password(self, prompt='Enter Password: '):
        if os.isatty(sys.stdin.fileno()):
            os.system("stty -echo")
            password = input(prompt)
            os.system("stty echo")
            print("")
        else:
            password = input(prompt)
        return password



def prompt_for_ip():
    ip = input("Enter the IP address of the server (eg 192.168.61.1): ")
    port = int(input("Enter the port of the server (eg 1500): "))
    return (ip, port)

def main():
    if len(sys.argv)!=1 and len(sys.argv)!= 3: # either need no args or both ip and port
        print("usage: python3 %s or python3 %s <server-ip> <server-port>" % sys.argv[0])
        quit(1)
    ip = None
    port = None

    print("#"*80)
    print('\t\t\tLog in to classroom voter')
    print("#"*80)

    if len(sys.argv) == 3:
            ip = sys.argv[1]
            port = int(sys.argv[2])
    else:
        ip, port = prompt_for_ip()
    
    login = LoginTools(ip, port, cli="True")
    
    
    
        


if __name__ == "__main__":
    main()
