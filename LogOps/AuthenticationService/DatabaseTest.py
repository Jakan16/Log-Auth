import sqlite3
from sqlite3 import Error
import json



authenticationStringTest = '{ "name":"BigCorp", "license":"1ILI-8TH1-HJ4S-SE78-SD45-45SE", "token":"skjJKHhjk8UJ98G8uiH98gJ098gHJ0" }'
jsonObjectDict = json.loads( authenticationStringTest )

name = jsonObjectDict["name"]
license = jsonObjectDict["license"]
serverToken = jsonObjectDict["token"]
print( serverToken )
def createConnection(db):

    connection = None

    try:
        connection = sqlite3.connect( db )
        print( "Connection to Database succeeded.")
    except Error as exception:
        print( exception )
    return connection

def selectAllCompanies(connectionToDB):
    query = "SELECT CompanyName, Agents.Token, Subscriptions.LicenseKeys FROM Companies JOIN Servers ON Companies.ID = Agents.CompanyID JOIN Subscriptions on Agents.ID = Subscriptions.ServerID WHERE Agents.Token = ? AND Subscriptions.LicenseKeys = ?"
    cursor =  connectionToDB.cursor()
    cursor.execute( query, ( serverToken, license ) )
    
    
    
    rows = cursor.fetchall()
    for row in rows:
        print( row )


def main():
    database = r"/home/thor/Documents/LogOps/AuthenticationService/testDB" #local path, has  to be changed to gereic, or server sided path.
    
    connection = createConnection(database)

    with connection:
        selectAllCompanies(connection)
    

if __name__ == "__main__":
    main()   
