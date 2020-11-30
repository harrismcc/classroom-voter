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
import ssl
import pprint
from classroom_voter.shared.pollTypes import Poll, FreeResponseQuestion
import classroom_voter.professor as professor
import classroom_voter.client as client

class LoginTools(object):
    '''an object to securely connect a client to the server
        and authenticate them.

        Parameters:
            ip: string ip for server
            port: port number of server
            cli: boolean for CLI responses
        
        Variables:
            ip: same
            port: same
            cli: same
            sock: the socket to the server
            clientSock: ssl secured socket to server'''
    def __init__(self, ip, port, cli=False):
        
        self.ip = ip
        self.port = port
        self.cli = cli

        self.sock = socket.socket()
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self.sock.connect((self.ip, self.port))
            if self.cli: print('Successful Connection')
            self.connected = True
        except socket.error as e:
            self.connected = False
            if self.cli: print('Failed Connection: ' + str(e))
            return

        self.hostname = "classroom.voter"
        self.client_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        self.client_context.options |= ssl.OP_NO_TLSv1
        self.client_context.options |= ssl.OP_NO_TLSv1_1
        self.client_context.verify_mode |= ssl.CERT_REQUIRED

        certPath = os.path.join(os.path.dirname(__file__) , "shared/newCert.crt")
        self.client_context.load_verify_locations(certPath)
        self.clientSocket = self.client_context.wrap_socket(self.sock, server_hostname=self.hostname)
        # pprint.pprint(self.clientSocket.getpeercert())
        # print(self.clientSocket.getpeername())
        # print(self.clientSocket.cipher())
        self.clientSocket.getpeercert()
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
        result = json.loads(self.clientSocket.recv(2048).decode())
        return result
        
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

    def get_new_password(self):
        """prompts the user for a new password that satisfies comprehensive8 requirements
        Returns:
            password: string password that satisfies comprehensive8"""

        valid = False
        password = ""
        while not valid:
            password = self.safe_prompt_for_password("please enter your new password: \n(note: Password must have atleast 8 characters including an uppercase and lowercase letter, a symbol, and a digit.\n Password: ")
            valid = True
            if len(password) < 8:
                valid = False
                print("password must be at least eight characters! \n")
            if not any(x.isupper() for x in password):
                valid = False
                print("password must contain at least one uppercase character! \n")
            if not any(x.islower() for x in password):
                valid = False
                print("password must contain at least one lowercase character! \n")
            if not any(x.isnumeric() for x in password):
                valid = False
                print("password must contain at least one digit! \n")
            symbols = '!@#$%^&*()-_+=`~[]{},./<>?|'
            if not any(x in symbols for x in password):
                valid = False
                print("password must contain at least one symbol (!@#$%^&*()-_+=`~[]{},./<>?|) \n")
            if valid:
                confirm = self.safe_prompt_for_password("Please enter the password again to confirm: ")
                if confirm != password:
                    valid = False
                    print("Passwords don't match! Try again")

        return password
        
    def safe_prompt_for_password(self, prompt='Enter Password: '):
        if os.isatty(sys.stdin.fileno()):
            os.system("stty -echo")
            password = input(prompt)
            os.system("stty echo")
            print("")
        else:
            password = input(prompt)
        return password


    def main(self):
        while True:
            login_action = input("Login or Forgot Password: ")
            if login_action == "Login":
                username = input("Enter username: ")
                password = self.safe_prompt_for_password()
                login_result = self.attempt_login(username, password)
                if login_result['Arguments']['result'] == 'success' or login_result['Arguments']['result'] == 'must reset':
                    break
                else:
                    print('Invalid credentials. Try again.')
                    
            if login_action == "Forgot Password":
                username = input("Enter username: ")
                login_result = self.recover_password(username)
                if login_result['Arguments']['result'] == 'success':
                    print('Password Recovery Succeeded')
                else:
                    print('Password Recovery Failed. Try again.')
                
        if login_result['Arguments']['result'] == 'must reset':
            new_password = self.get_new_password()
            reset_result = self.reset_password(username, password, new_password)
            if reset_result['Arguments']['result'] == 'success':
                pass
            else:
                print("Password Reset Failed")
                quit()
            
        if login_result['Arguments']['account_type'] == 'students':
            client.main(self.clientSocket, login_result['Arguments']['username'])
        elif login_result['Arguments']['account_type'] == 'professors':
            professor.main(self.clientSocket)


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
    try:
        login = LoginTools(ip, port, cli="True")
    except ssl.SSLError as e:
        print(str(e))
    
    
        


if __name__ == "__main__":
    main()
