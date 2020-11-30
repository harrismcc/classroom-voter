import unittest
import socket
import concurrent.futures
import time
import threading
import os


#from .. import server
import classroom_voter.server as server
from classroom_voter.shared.pollTypes import *

class ServerTests(unittest.TestCase):
    def setUp(self):
        self.serverSocket = socket.socket()
        self.clientSocket = socket.socket()

        self.serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.clientSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.pollTemplate = {
            'question': {
                'prompt': 'What is your favorite color?',
                "answer" : None, 
                'options': [], 
                'type': 'FreeResponseQuestion'
                },
            'startTime' : "2020-10-27 16:25:07",
            'endTime' : "2025-10-27 16:25:07",
            'ownerId' : 'bebop@yahoo.com',
            'classId' : 0,
            'responses': []}

        
    def _miniServer(self):
            """waits for client connection to server"""
            client = None
            while not client:
                client, address = self.serverSocket.accept()
            return client
      
    def test_Announce_poll(self):
        """This tests the server endpoint Announce_poll"""

        #create new socket for server
        self.serverSocket.bind(('localhost', 1337))
        self.serverSocket.listen(0)
        #create new client socket
        self.clientSocket.bind(('localhost', 2222))
        #self.assertEqual(server.polls, [])

        
        #execute socket connection as new thread
        with concurrent.futures.ThreadPoolExecutor() as executor:

            myPoll = Poll.fromDict(self.pollTemplate)

            future = executor.submit(self._miniServer)
            self.clientSocket.connect(('localhost', 1337))
            conn = future.result()
            server.connection_list['username'] = conn

            tclient = executor.submit(server.threaded_client, conn)
            test = {
                'endpoint' : 'Announce_poll',
                'Arguments' : {
                    'poll': myPoll.toDict()
                    }   
                }

            #send test packet to server
            self.clientSocket.send(json.dumps(test).encode())
            self.clientSocket.close()

            #make sure server added poll correctly to its running list
            #self.assertEqual(server.polls[0].toDict(), myPoll.toDict())

    def test_Poll_response(self):
            """This tests the server endpoint Poll_response"""

            #create new socket for server
            self.serverSocket.bind(('localhost', 1337))
            self.serverSocket.listen(0)
            #create new client socket
            self.clientSocket.bind(('localhost', 2222))
            self.assertEqual(server.polls, [])

            #execute socket connection as new thread
            with concurrent.futures.ThreadPoolExecutor() as executor:

                myPoll = Poll.fromDict(self.pollTemplate)

                future = executor.submit(self._miniServer)
                self.clientSocket.connect(('localhost', 1337))
                conn = future.result()
                server.connection_list["username"] = conn

                tclient = executor.submit(server.threaded_client, conn)
                test = {
                    'endpoint' : 'Announce_poll',
                    'Arguments' : {
                        'poll': myPoll.toDict()
                        }   
                    }

                #send test packet to server
                self.clientSocket.send(json.dumps(test).encode())
                self.clientSocket.close()

                #make sure server added poll correctly to its running list
                #self.assertEqual(server.polls[0].toDict(), myPoll.toDict())
                

        


    def tearDown(self):
        self.serverSocket.close()
        self.clientSocket.close()

        server.polls = []


if __name__ == '__main__':
    
    unittest.main()