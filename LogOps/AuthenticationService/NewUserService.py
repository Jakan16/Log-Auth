import jwcrypto
from jwcrypto import jwt, jwk
import json
import socket
import sys
import sqlite3
from sqlite3 import Error
import uuid


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

def create_connection( db ):

    connection = None

    try:
        connection = sqlite3.connect( db )
    except Error as exception:
        print( exception )
    return connection


def create_new_company( connectionToDB, name, autoGenKey ):
    query = "INSERT INTO Companies VALUES (NULL, ?, ?)"
    cursor = connectionToDB.cursor()
    cursor.execute( query, ( name, autoGenKey, ) )

DATABASE = r"/home/thor/Documents/LogOps/AuthenticationService/test.sqlite" #local path, has  to be changed to generic, or server sided path.
PORT = 8002
socketConnection = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
socketConnection.bind( ( '', PORT ) )
socketConnection.listen( 128 )

def service_start():
    while True:
        connection, address = socketConnection.accept()
        print( "Got a connection from ", address )
        newCompanyString = receive( connection )
        newCompanyJson = json.loads ( newCompanyString )

        name = newCompanyJson[ "name" ]
        randomKey = uuid.uuid4()
        dbConnection = create_connection( DATABASE ) 
        with dbConnection:
            create_new_company( dbConnection, name, randomKey )
        dbConnection.close()
        jsonString = '{ "companykey":"' + randomKey + '" }'
        send( connection, jsonString )
        connection.close()

def main():
    service_start()

if __name__ == "__main__":
    main()