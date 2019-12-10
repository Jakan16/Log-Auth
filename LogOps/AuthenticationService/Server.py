import socket
import sys
import jwcrypto
from jwcrypto import jwt, jwk
import json


socketConnection = socket.socket()
print("Socket created.")

port = 8000

socketConnection.bind(('', port))
socketConnection.listen(5)
print("Socket is listening.")

while True:

    client, address = socketConnection.accept()
    print("Got connection from ", address)

    client.send("We are connected.")

    client.close()
