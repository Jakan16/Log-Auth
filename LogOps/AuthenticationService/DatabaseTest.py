import sqlite3
from sqlite3 import Error
import json



authenticationStringTest = '{ "name":"BigCorp", "license":"1ILI-8TH1-HJ4S-SE78-SD45-45SE", "token":"skjJKHhjk8UJ98G8uiH98gJ098gHJ0" }'
jsonObjectDict = json.loads( authenticationStringTest )

name = jsonObjectDict["name"]
license = jsonObjectDict["license"]
serverToken = jsonObjectDict["token"]
print( serverToken )

def create_connection(db):

    connection = None

    try:
        connection = sqlite3.connect( db )
        print( "Connection to Database succeeded.")
    except Error as exception:
        print( exception )
    return connection

def select_all_companies(connectionToDB):
    query = "SELECT Agents.Token, Subscriptions.LicenseKeys FROM Companies JOIN Agents ON Companies.ID = Agents.CompanyID JOIN Subscriptions ON Agents.ID = Subscriptions.AgentID  WHERE Agents.Token = ? AND Subscriptions.LicenseKeys = ?"
    cursor =  connectionToDB.cursor()
    cursor.execute( query, ( serverToken, license ) )
    
    
    
    rows = cursor.fetchall()
    for row in rows:
        print( row )


def main():
    database = r"/home/thor/Documents/LogOps/AuthenticationService/testDB" #local path, has  to be changed to gereic, or server sided path.
    
    connection = create_connection( "testDB" ) #database path got broken somehow, and cannot find a fix atm.

    with connection:
        select_all_companies( connection )
    

if __name__ == "__main__":
    main()   
