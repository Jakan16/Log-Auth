import socket
import sys
import sqlite3
from sqlite3 import Error
import json
import jwcrypto
from jwcrypto import jwt, jwk

authenticationString = '{ "name":"BigCorp", "license":"1ILI-8TH1-HJ4S-SE78-SD45-45SE", "token":"skjJKHhjk8UJ98G8uiH98gJ098gHJ0" }'


socketConnection = socket.socket()

port = 8000
address = "localhost"

socketConnection.connect( ( address, port ) )

socketConnection.send( authenticationString )

encryptionKeyString = socketConnection.recv(512)
encryptedTokenFromServer = socketConnection.recv(512)
print( encryptionKeyString )
print( encryptedTokenFromServer )

encryptionKey = json.loads( encryptionKeyString )

socketConnection.close()
