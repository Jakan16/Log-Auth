import jwcrypto
from jwcrypto import jwt, jwk
import json
import socket
import sys
import sqlite3
from sqlite3 import Error

def create_connection( db ):

    connection = None

    try:
        connection = sqlite3.connect( db )
    except Error as exception:
        print( exception )
    return connection

def check_authorization( connectionToDB, license, serverToken, key ):
    query = "SELECT Agents.Token, Subscriptions.LicenseKeys FROM Companies JOIN Agents ON Companies.ID = Agents.CompanyID JOIN Subscriptions ON Agents.ID = Subscriptions.AgentID  WHERE Agents.Token = ? AND Subscriptions.LicenseKeys = ? AND Companies.CompanyKey = ?"
    cursor = connectionToDB.cursor()
    cursor.execute( query, ( serverToken, license, key,) )

    rows = cursor.fetchall()

    if rows is None:
        print("Token or license key not valid")
        return False
    else:
        return True
def check_subscription( connectionToDB, cpuUse, ramUse, logUse ):
    query = "SELECT Resources.CPU_USE, Resources.RAM_USE, Resources.Logs_USE FROM Resources WHERE CPU_USE + ? <= CPU_MAX AND RAM_USE + ? <= RAM_MAX AND Logs_USE + ? <= Logs_MAX" 
    cursor = connectionToDB.cursor()
    cursor.execute( query, ( cpuUse, ramUse, logUse ) )

    rows = cursor.fetchall()

    if rows is None:
        print("Resources are over subscription limit!")
        return False
    else:
        return True

def update_subscription( connectionToDB, cpuUse, ramUse, logUse ):
    query = "UPDATE Resources SET CPU_USE = CPU_USE + ?, RAM_USE = RAM_USE + ?, Logs_USE = Logs_USE + ?"
    cursor = connectionToDB.cursor()
    cursor.execute( query, ( cpuUse, ramUse, logUse ) )

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

def send_key_to_decoder( key ):
    connectionToDecoder = socket.socket()
    PORT_OF_DECODER = 8001
    ADDRESS_OF_DECODER = "localhost"

    connectionToDecoder.connect( ( ADDRESS_OF_DECODER, PORT_OF_DECODER ) )
    send( connectionToDecoder, key.export() )
    connectionToDecoder.close()




DATABASE = r"/home/thor/Documents/LogOps/AuthenticationService/test.sqlite" #local path, has  to be changed to generic, or server sided path.

key = jwk.JWK( generate = 'oct', size = 256 ) #Symmetric key for encrypting and decrypting



PORT = 8000
socketConnection = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
socketConnection.bind( ( '', PORT ) )
socketConnection.listen( 128 )


def start_server():
    while True:

        connection, address = socketConnection.accept()
        print( "Got connection from ", address )

        authenticationString = receive( connection )
        # print( authenticationString )
        jsonObject = json.loads( authenticationString )
        companyKey = jsonObject["key"]
        license = jsonObject["license"]
        serverToken = jsonObject["token"]
        cpu = jsonObject["cpu"]
        ram = jsonObject["ram"]
        log = jsonObject["log"]

        dbConnection = create_connection( 'testDB' ) #DATABASE path got broken somehow, and cannot find a fix atm.
        with dbConnection:
            authorized = check_authorization( dbConnection, license, serverToken, companyKey )
            if authorized:
                subsIsOkay = check_subscription( dbConnection, cpu, ram, log )
                if subsIsOkay:
                    update_subscription( dbConnection, cpu, ram, log )
        dbConnection.close()
        if authorized and subsIsOkay:
            token = jwt.JWT( header = { "alg": "HS256" }, claims = { "info": "I am a signed Token" } ) #Hvad skal claims vaere?
            token.make_signed_token( key )

            encryptedToken = jwt.JWT( header = { "alg": "A256KW", "enc": "A256CBC-HS512" }, claims = token.serialize() )
            encryptedToken.make_encrypted_token( key )
            encryptedTokenString = encryptedToken.serialize()

            jsonString = '{ "authtoken":"' + encryptedTokenString + '" }'
            print( jsonString )
            send( connection, jsonString )
            
            connection.close()
        else:
            connection.close()

        

def main():
    send_key_to_decoder( key )
    start_server()

if __name__ == "__main__":
    main()  












