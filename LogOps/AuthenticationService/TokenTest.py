import jwcrypto
from jwcrypto import jwt, jwk
import json
import socket
import sys
import sqlite3
from sqlite3 import Error

def create_connection(db):

    connection = None

    try:
        connection = sqlite3.connect( db )
    except Error as exception:
        print( exception )
    return connection

def check_authorization(connectionToDB):
    query = "SELECT Agents.Token, Subscriptions.LicenseKeys FROM Companies JOIN Servers ON Companies.ID = Servers.CompanyID JOIN Subscriptions on Servers.ID = Subscriptions.ServerID WHERE Agents.Token = ? AND Subscriptions.LicenseKeys = ?"
    cursor =  connectionToDB.cursor()
    cursor.execute( query, ( serverToken, license, ) )

    rows = cursor.fetchall()
    
    if rows is None:
        print("Token or license key not valid")
# TODO!!! def on_new_client( clientSocket, address ):
#     while True:

#         clientSocket.close
            
database = r"/home/thor/Documents/LogOps/AuthenticationService/testDB" #local path, has  to be changed to gereic, or server sided path.

key = jwk.JWK( generate = 'oct', size = 256 ) 
keyString = key.export()
# print( keyString )


token = jwt.JWT( header = { "alg": "HS256" }, claims = { "info": "I am a signed Token" }) 
token.make_signed_token( key )
token.serialize()

encryptedToken = jwt.JWT( header = { "alg": "A256KW", "enc": "A256CBC-HS512" }, claims = token.serialize() )
encryptedToken.make_encrypted_token( key )
encryptedTokenString = encryptedToken.serialize()

socketConnection = socket.socket()
port = 8000
socketConnection.bind( ( '', port ) )
socketConnection.listen( 5 )



while True:

    connection, address = socketConnection.accept()

    # TODO!!! _thread.start_new_thread( on_new_client, ( socketConnection, address ) )
    
    
    authenticationString = connection.recv( 256 )
    jsonObject = json.loads( authenticationString )
    # print( jsonObject )    
    name = jsonObject["name"]
    license = jsonObject["license"]
    serverToken = jsonObject["token"]

    dbConnection = create_connection( 'testDB' )
    with dbConnection:
        check_authorization( dbConnection )
    dbConnection.close()

    connection.send( keyString, encryptedToken.serialize() )
    connection.send( encryptedToken.serialize() )


