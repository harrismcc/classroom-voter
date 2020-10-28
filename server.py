"""
The `server` module handles the socket networking with the clients, placing them each into
their own threaded connection.
"""
import os
import sys
import json
import socket
import threading

from _thread import *
from threading import Thread

from hashlib import sha256

from shared.pollTypes import *
from shared.database import *
from shared.locks import *
from shared.authenticationTools import *

sys.path.append(os.path.dirname(__file__)) #gets pdoc working

database = DatabaseSQL("./shared/example.db")
database_lock = locks.RWLock()

def authenticate_user(username, password):
    """
        Authenticate a user by checking their existance in database and validating passwordHash
        
        Args:
            username: the username (email) trying to be authenticated
            password: the password used for authentication
            
        Returns:
            True if user is authenticated, False if user is not authenticated
    """
    
    
    

def threaded_client(connection):
    """
    Creates a new threaded client connection loop

    Args:
        connection (socket): socket connection to client

    """
    
    try:    
        authenticated = False
        isReedemed = False
        while not authenticated:
            data = json.loads(connection.recv(2048).decode())
        
            print(data)
        
            if not data:
                break
            
            endpoint = data["endpoint"]
            
            if endpoint == "Login":
                arguments = data["Arguments"]
                username = arguments["username"]
                password = arguments["password"]
                
                authenticate_user(username, password)
            
                database_lock.acquire_read()
                user_object = database.getUser(username)
                database_lock.release()
                
                # User does not exist
                if user_object is None:
                    authentication_response = {
                        "endpoint" : "Login_result",
                        "Arguments" : {
                            "result" : "failure"
                        }
                    }
                    connection.send(json.dumps(authentication_response).encode())
                    continue
                    
                user = user_object[username]
                
                # If user exists check password
                password_hash = sha256(password.encode('utf-8')).hexdigest()
                
                authentication_result = ""
                if password_hash == user["password"]:
                                    
                    isReedemed = user["reedemed"]
                    if isReedemed:
                        authentication_result = "success"
                    else:
                        authentication_result = "reset required"

                        
                else:
                    authentication_result = "failure"
                    
                authentication_response = {
                    "endpoint" : "Login_result",
                    "Arguments" : {
                        "result" : authentication_result
                    }
                }
                
                connection.send(json.dumps(authentication_response).encode())
                
            if endpoint == "Reset_password" and not isReedemed:
                arguments = data["Arguments"]
                username = arguments["username"]
                old_password = arguments["old_password"]
                new_password = arguments["new_password"]
                
                # User does not exist
                if user_object is None:
                    reset_response = {
                        "endpoint" : "Reset_result",
                        "Arguments" : {
                            "result" : "failure"
                        }
                    }
                    connection.send(json.dumps(reset_response).encode())
                    continue
                
                user = user_object[username]
                
                # If user exists check password
                old_password_hash = sha256(old_password.encode('utf-8')).hexdigest()

                reset_result = ""
                if password_hash == user["password"]:
                    new_password_hash = sha256(new_password.encode('utf-8')).hexdigest()
                    
                    database_lock.acquire_write()
                    database.updateFieldViaId("users", username, "hashedPassword", new_password_hash)
                    database.updateFieldViaId("users", username, "reedemed", "1")
                    database_lock.release()
                    
                    reset_result = "success"
                else:
                    reset_result = "failure"

                reset_response = {
                    "endpoint" : "Reset_result",
                    "Arguments" : {
                        "result" : reset_result
                    }
                }
                
                connection.send(json.dumps(reset_response).encode())
    
    
    
        while True:
            data = json.loads(connection.recv(2048).decode())
            
            print(data)

            if not data:
                break
            
            endpoint = data["endpoint"]
            
            if endpoint == "Announce_poll":
                poll = Poll.fromDict(data["Arguments"]["poll"])
                polls.append(poll)
                outgoing_msg = poll.question.toDict()
                broadcast(json.dumps(outgoing_msg))
                continue
            
            if endpoint == "Poll_response":
                poll_response = PollResponse.fromDict(data["Arguments"]["poll"])
                add_response_to_poll(poll_response)
                continue
            
            if endpoint == "Aggregate_poll":
                outgoing_msg = aggregate_poll()
                broadcast(json.dumps(outgoing_msg))
                continue
                
    finally:
        print("Closing Connection!")
        connection.close()
    

def main():
    """ Accepts incoming connections from clients and puts each client connection in a new thread """
    #TODO: Change this out for argparse
    if len(sys.argv) != 2:
        print("usage: python3 %s <port>" % sys.argv[0])
        quit(1)
    port = sys.argv[1]

    serverSocket = socket.socket()
    host = 'localhost'
    port = int(port)
    threadCount = 0

    try:
        serverSocket.bind((host, port))
    except socket.error as e:
        print(str(e))

    print('Waiting for a Connection To Client..')
    serverSocket.listen(5)
    
    #continuiously accept new connections
    while True:
        client, address = serverSocket.accept()
                
        print('Connected to: ' + address[0] + ':' + str(address[1]))

        #each individual connection is threaded
        start_new_thread(threaded_client, (client, ))
        threadCount += 1
        print('Thread Number: ' + str(threadCount))
    serverSocket.close()


if __name__ == "__main__":
    main()
