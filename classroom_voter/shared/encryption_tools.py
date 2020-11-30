#This file holds shared functions for encryption. This way, we can decide to change our encryption protocols on the fly

import sys
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Hash import HMAC, SHA256
from os import _exit as quit
import json



def _test():
    """This is a test function blah"""
    pass


def encrypt_message(msg, key):
    """
    Encrypts message using RSA key

    Args:
        msg (string): message to be encrypted
        key (RSA key): RSA keypair object

    Returns:
        bytes: the byte encoded RSA encrypted message

    """
    msg = msg.encode()
    cipher = PKCS1_OAEP.new(key.publickey())
    return cipher.encrypt(msg)
    

def create_mac(msg, key):
    """
    Uses RSA private key to create SHA-256 MAC from Message
    

    Args:
        msg (string): message to verify
        key (RSA key): RSA keypair object

    Returns:
        string: hex representation of message MAC

    """
    secret = key.exportKey('PEM')
    h = HMAC.new(secret, digestmod=SHA256)
    h.update(msg.encode())
    mac = h.hexdigest()
    return mac


def verify_MAC(message, mac, key):
    """
    verify a hex MAC and a byte-array message

    Args:
        message (string): message to be verified
        mac (string): hex representation of message MAC
        key (RSA key): RSA keypair object
    
    Returns:
        bool: true if message and MAC match

    """
    
    secret = key.exportKey('PEM')
    h = HMAC.new(secret, digestmod=SHA256)
    h.update(message.encode())

    try:
        h.hexverify(mac)
        return True
    except ValueError:
        return False

    return False