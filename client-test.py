import socket
import os
import sys
import json
import getpass
from shared.pollTypes import Poll, FreeResponseQuestion
import professor
import client
import ssl


hostname = 'Classroom Voter'
context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2,)
context.load_verify_locations('./certificate.pem')

with socket.create_connection((localhost, 8800)) as sock:
    with context.wrap_socket(sock, server_hostname=hostname) as ssock:
        print(ssock.version())
