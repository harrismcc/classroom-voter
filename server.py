#!/usr/bin/env python3
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

dirname = os.path.dirname(__file__)
db_path = os.path.join(dirname, 'shared/example.db')
database = DatabaseSQL(db_path)
database_lock = RWLock()

connection_list = {}
connection_list_lock = RWLock()

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
        salt = user[username]["salt"]
        given_password_hash = sha256((password + salt).encode('utf-8')).hexdigest()

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
        "user" : user_object
    }

def add_connection(username, connection):
    """
        Add an authenticated user to the connection list
        
        Args:
            username (key): the username associated with the connection
            connection (value): the connection socket
            
        Returns:
            True: if username is not in connection list
            False: if username is in connection list
    """
    connection_list_lock.acquire_write()
    connection_list[username] = connection
    connection_list_lock.release()

def remove_connection(username):
    connection_list_lock.acquire_write()
    if username in connection_list:
        del connection_list[username]
    connection_list_lock.release()

def threaded_client(connection):
    """
    Creates a new threaded client connection loop

    Args:
        connection (socket): socket connection to client

    """
    
    authenticated_username = None
    
    try:    
        authenticated = False
        isReedemed = False
        while not authenticated:
            data = connection.recv(2048)
            if not data:
                break

            data = json.loads(data.decode())

            print(data)
            
            endpoint = data["endpoint"]
            
            if endpoint == "Login":
                arguments = data["Arguments"]
                username = arguments["username"]
                password = arguments["password"]
                
                authentication_result = authenticate_user(username, password)
                
                user = authentication_result["user"]
                isAuthenticated = authentication_result["isAuthenticated"]
                                
                authentication_msg = ""
                account_type = None
                if isAuthenticated and (user is not None):
                                             
                    isReedemed = user[username]["reedemed"]
                    if isReedemed:
                        authentication_msg = "success"
                        authenticated_username = username
                        authenticated = True
                    else:
                        authentication_msg = "must reset"
                        
                    account_type = user[username]["role"]

                else:
                    authentication_msg = "failure"
                    
                authentication_response = {
                    "endpoint" : "Login_result",
                    "Arguments" : {
                        "result" : authentication_msg,
                        "account_type" : account_type, 
                        "username" : username
                    }
                }
                
                connection.send(json.dumps(authentication_response).encode())
                continue
                
            if endpoint == "Reset_password":
                arguments = data["Arguments"]
                username = arguments["username"]
                old_password = arguments["old_password"]
                new_password = arguments["new_password"]
                
                authentication_result = authenticate_user(username, old_password)
                
                user = authentication_result["user"]
                isAuthenticated = authentication_result["isAuthenticated"]
                                
                reset_msg = ""
                account_type = None
                if isAuthenticated and (user is not None):
                    salt = user['salt']
                    new_password_hash = sha256((new_password+salt).encode('utf-8')).hexdigest()
                    
                    database_lock.acquire_write()
                    database.updateFieldViaId("users", username, "hashedPassword", new_password_hash)
                    database.updateFieldViaId("users", username, "reedemed", "1")
                    database_lock.release()
                    
                    reset_msg = "success"
                    account_type = user[username]["role"]
                    authenticated_username = username
                    authenticated = True

                else:
                    reset_msg = "failure"

                reset_response = {
                    "endpoint" : "Reset_result",
                    "Arguments" : {
                        "result" : reset_msg,
                        "account_type" : account_type,
                        "username" : username
                    }
                }
                
                connection.send(json.dumps(reset_response).encode())
                continue
        
        
        # At this point the user is autheticated.
        # User should never be None here but just in case
        if authenticated_username is None:
            return
        
        # Make sure we are not already connected to this user
        connection_list_lock.acquire_read()
        already_connected = authenticated_username in connection_list
        connection_list_lock.release()
        
        if already_connected:
            # Already connected to this user
            print("Already Connected")
            authenticated_username = None
            return
        else:
            # Add the authenticated user to the connection list
            add_connection(authenticated_username, connection)
                
        while True:
            data = connection.recv(2048)
            if not data:
                break

            data = json.loads(data.decode())

            print(data)
            
            endpoint = data["endpoint"]
            
            if endpoint == "Announce_poll":
                poll = Poll.fromDict(data["Arguments"]["poll"])
                                
                database_lock.acquire_write()
                database.addPoll(poll)
                database_lock.release()
                continue
            
            if endpoint == "Get_next_poll":
                # Send out the next unseen poll
                connection_list_lock.acquire_read()
                student_connection = connection_list[authenticated_username]
                next_poll = database.getNextPollForUser(authenticated_username)
                if not next_poll:
                    student_connection.send("No new polls".encode())

                next_poll_question = {
                    "prompt": next_poll['question']
                }
                student_connection.send(json.dumps(next_poll_question).encode())
                connection_list_lock.release()
            
            if endpoint == "Poll_response":
                poll_response = PollResponse.fromDict(data["Arguments"]["poll"])
                print(authenticated_username)

                database.addResponse(authenticated_username, int(data["Arguments"]["pollId"]), json.dumps(poll_response.toDict()))
                
                """database_lock.acquire_write()
                add_response_to_poll(poll_response)
                database_lock.release()"""
                
                continue
            
            if endpoint == "Aggregate_poll":
                # outgoing_msg = aggregate_poll()
                # broadcast(json.dumps(outgoing_msg))
                # get poll from id

                continue
            
            if endpoint == "Get_polls_for_user":
                """gets all polls for user"""
                username = data["Arguments"]["username"]
                role = data["Arguments"]["role"]
                filterValue = None
                try:
                    filterValue = data["Arguments"]["filter"]
                except KeyError:
                    pass
            
                resp = database.getPollsForUser(username, role)
                out = []

                if filterValue == "active":
                    responded = database.getAnsweredPollIdsForUser(username)
                    for poll in resp:
                        if poll["pollId"] not in responded:
                            out.append(poll)
                elif filterValue == "answered":
                    responded = database.getAnsweredPollIdsForUser(username)
                    for poll in resp:
                        if poll["pollId"] in responded:
                            out.append(poll)
                else:
                    out = resp

                connection.send(json.dumps(out).encode())
                



                
    finally:
        print("Closing Connection!")
        remove_connection(authenticated_username)
        connection.close()
        print(connection_list)
    

def main():
    """ Accepts incoming connections from clients and puts each client connection in a new thread """
    #TODO: Change this out for argparse
    if len(sys.argv) != 2:
        print("usage: python3 %s <port>" % sys.argv[0])
        quit(1)
    port = sys.argv[1]

    serverSocket = socket.socket()
    serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
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
