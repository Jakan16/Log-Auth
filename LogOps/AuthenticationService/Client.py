import socket
import jwcrypto
from jwcrypto import jwt, jwk
import json






socketConnection = socket.socket()

port = 8000
address = "localhost" #Should be changed to web address
socketConnection.connect((address, port))

print(socketConnection.recv(1024))
socketConnection.close()