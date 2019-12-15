import socket
import sys
import sqlite3
from sqlite3 import Error
import json
import jwcrypto
from jwcrypto import jwt, jwk
import time

def send( socketConnection, msg, end = "EOFEOFEOFEOFX" ):
    socketConnection.sendall( msg + end )

def receive( socketConnection, end = "EOFEOFEOFEOFX" ):
    data = ""
    incomingData = socketConnection.recv( 1024 )
    while incomingData: 
        data += incomingData
        if data.endswith( end ) == True:
            break
        else:
            incomingData = socketConnection.recv( 1024 )
    return data[ :-len( end ) ]


authenticationString = '{ "name":"BigCorp", "license":"1ILI-8TH1-HJ4S-SE78-SD45-45SE", "token":"skjJKHhjk8UJ98G8uiH98gJ098gHJ0", "cpu":"10", "ram":"256", "log":"250" }'


socketConnection = socket.socket()

PORT = 8000
ADDRESS = "localhost"

socketConnection.connect( ( ADDRESS, PORT ) )

send( socketConnection, authenticationString )
jsonTokenFromServer = receive( socketConnection )
print( jsonTokenFromServer )

socketConnection.close()
