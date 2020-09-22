#This file holds shared functions for encryption. This way, we can decide to change our encryption protocols on the fly

import sys
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Hash import HMAC, SHA256
from os import _exit as quit
import json

#creates a new keypair
def create_key():
    key = RSA.generate(2048)
    return key


#Encrypts message using RSA key
def encrypt_message(msg, key):
    msg = msg.encode()
    cipher = PKCS1_OAEP.new(key.publickey())
    return cipher.encrypt(msg)
    
#Uses RSA private key to create MAC from Message
def create_mac(msg, key):
    secret = key.exportKey('PEM')
    h = HMAC.new(secret, digestmod=SHA256)
    h.update(msg.encode())
    mac = h.hexdigest()

    return mac

#verify a hex MAC and a byte-array message
def verify_MAC(message, mac, key):

    secret = key.exportKey('PEM')
    h = HMAC.new(secret, digestmod=SHA256)
    h.update(message.encode())

    try:
        h.hexverify(mac)
        return True
    except ValueError:
        return False

    return False