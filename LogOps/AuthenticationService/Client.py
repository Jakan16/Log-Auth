import socket
import jwcrypto
from jwcrypto import jwt, jwk
import json






socketConnection = socket.socket()

port = 8000
address = "localhost" #Should be changed to web address
socketConnection.connect((address, port))

msg = socketConnection.recv(1024)
print( msg )

msg2 = "Are we still connected?"
socketConnection.send( msg2 )
socketConnection.close()