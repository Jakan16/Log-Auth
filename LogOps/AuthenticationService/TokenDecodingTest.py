import jwcrypto
from jwcrypto import jwt, jwk
import json
import socket
import sys

 
socketConnection = socket.socket()

port = 8001

socketConnection.bind( ( '', port ) )
socketConnection.listen(5)

while True:

    encryptionKeyString = socketConnection.recv(512)
    encryptedTokenFromServer = socketConnection.recv(512)
    encryptionKey = json.loads( encryptionKeyString )


    key = jwk.JWK( **encryptionKey )

    encryptedToken = jwt.JWT( key = key, jwt = encryptedTokenFromServer )   
    decryptedToken = jwt.JWT( key = key, jwt = encryptedToken.claims )                  
    decryptedToken.claims                                                   

    print( decryptedToken.claims )


    socketConnection.close()
