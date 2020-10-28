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

sys.path.append(os.path.dirname(__file__)) #gets pdoc working

database = DatabaseSQL("./shared/example.db")
database_lock = RWLock()

def authenticate_user(username, password):
    """
        Authenticate a user by checking their existance in database and validating passwordHash
        
        Args:
            username: the username (email) trying to be authenticated
            password: the password used for authentication
            
        Returns:
            True and user if authenticated
            False and none of not authenticated
    """
    isAuthenticated = False
    user_object = None
    
    database_lock.acquire_read()
    user = database.getUser(username)
    database_lock.release()
    
    if user is not None:
        stored_password_hash = user[username]["password"]
        given_password_hash = sha256(password.encode('utf-8')).hexdigest()

        if given_password_hash == stored_password_hash:
            isAuthenticated = True
            user_object = user
        else:
            isAuthenticated = False
            user_object = None
    else:
        isAuthenticated = False
        user_object = None
    
    return {
        "isAuthenticated" : isAuthenticated,
        "user" : user
    }

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
                
                authentication_result = authenticate_user(username, password)
                isAuthenticated = authentication_result["isAuthenticated"]
                user = authentication_result["user"]
                
                authentication_msg = ""
                if isAuthenticated and (user is not None):
                                    
                    isReedemed = user[username]["reedemed"]
                    if isReedemed:
                        authentication_msg = "success"
                        authenticated = True
                    else:
                        authentication_msg = "reset required"

                else:
                    authentication_msg = "failure"
                    
                authentication_response = {
                    "endpoint" : "Login_result",
                    "Arguments" : {
                        "result" : authentication_msg
                    }
                }
                
                connection.send(json.dumps(authentication_response).encode())
                continue
                
            if endpoint == "Reset_password" and not isReedemed:
                arguments = data["Arguments"]
                username = arguments["username"]
                old_password = arguments["old_password"]
                new_password = arguments["new_password"]
                
                authentication_result = authenticate_user(username, old_password)
                isAuthenticated = authentication_result["isAuthenticated"]
                user = authentication_result["user"]
                                
                reset_msg = ""
                if isAuthenticated and (user is not None):
                    new_password_hash = sha256(new_password.encode('utf-8')).hexdigest()
                    
                    database_lock.acquire_write()
                    database.updateFieldViaId("users", username, "hashedPassword", new_password_hash)
                    database.updateFieldViaId("users", username, "reedemed", "1")
                    database_lock.release()
                    
                    reset_msg = "success"
                    authenticated = True
                else:
                    reset_msg = "failure"

                reset_response = {
                    "endpoint" : "Reset_result",
                    "Arguments" : {
                        "result" : reset_msg
                    }
                }
                
                connection.send(json.dumps(reset_response).encode())
                continue
    
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
