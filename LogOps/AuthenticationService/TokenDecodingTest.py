import jwcrypto
from jwcrypto import jwt, jwk
import json
import socket
import sys

 
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


socketConnection = socket.socket()

PORT = 8001
socketConnection = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
socketConnection.bind( ( '', PORT ) )
socketConnection.listen( 128 )

while True:

    connection, address = socketConnection.accept()
    print( "Got connection from ", address )

    encryptionKeyString = receive( connection )
    encryptionKey = json.loads( encryptionKeyString )
    print( encryptionKey )


    connection, address = socketConnection.accept()
    print( "Got connection from ", address )

    jsonStringFromClient = receive( connection )
    print( jsonStringFromClient )
    try:
        jsonObject = json.loads( jsonStringFromClient )
        encryptedTokenFromClient = jsonObject["authtoken"]
        print( encryptedTokenFromClient )
    except:
        print( "No json object." )
        

    try:     
        key = jwk.JWK( **encryptionKey )

        encryptedToken = jwt.JWT( key = key, jwt = encryptedTokenFromClient ) 
        decryptedToken = jwt.JWT( key = key, jwt = encryptedToken.claims )  
        decryptedToken.claims  
        
        print( decryptedToken.claims )
    except:
        print( "Failed to decode token")
    


    connection.close()
