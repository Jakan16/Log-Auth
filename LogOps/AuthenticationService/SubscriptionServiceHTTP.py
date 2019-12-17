#!/usr/bin/env python
"""
Very simple HTTP server in python (Updated for Python 3.7)
Usage:
    ./dummy-web-server.py -h
    ./dummy-web-server.py -l localhost -p 8000
Send a GET request:
    curl http://localhost:8000
Send a HEAD request:
    curl -I http://localhost:8000
Send a POST request:
    curl -d "foo=bar&bin=baz" http://localhost:8000
"""


import jwcrypto
from jwcrypto import jwt, jwk
import json
import socket
import sys
import sqlite3
from sqlite3 import Error
import uuid
import argparse
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import random
import sys

class S(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

    def _html(self, message):
        """This just generates an HTML document that includes `message`
        in the body. Override, or re-write this do do more interesting stuff.
        """
        content = f"<html><body><h1>{message}</h1></body></html>"
        return content.encode("utf8")  # NOTE: must return a bytes object!

    def do_GET(self):
        self._set_headers()
        data = {}
        self.wfile.write(json.dumps(data).encode(encoding='utf_8'))

    def do_HEAD(self):
        self._set_headers()

    def do_POST(self):
        # Doesn't do anything with posted data
        content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
        post_data = self.rfile.read(content_length).decode('UTF-8') # <--- Gets the data itself
        jsonObject = json.loads( post_data )
        method = jsonObject["method"]
        data = {}
        
        # Create a new company in the database
        if method == "newcompany":
            name = jsonObject[ "name" ]
            randomKey = uuid.uuid4()
            dbConnection = create_connection( 'testDB' )
            with dbConnection:
                create_new_company( dbConnection, name, str(randomKey) )
            dbConnection.close()
            data["name"] = name
            data["key"] = str(randomKey)
            # print(data)
            self.wfile.write(json.dumps(data).encode(encoding='utf_8'))
        
        # Create a new agent in the database
        if method == "newagent":
            name = jsonObject["name"]
            companyKey = jsonObject["key"]

            seq = "ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"
            licenseKey = "-".join("".join(random.choice(seq) for _ in range(4)) for _ in range(6))

            dbConnection = create_connection( 'testDB' )
            with dbConnection:
                succes = create_new_agent( dbConnection, name, companyKey, licenseKey ) #Query not done
            dbConnection.close()
            data["response"] = succes

            self.wfile.write(json.dumps(data).encode(encoding='utf_8'))
        
        # Fetches all agents of a given company
        if method == "agentlist":
            companyKey = jsonObject["key"]
            dbConnection = create_connection( 'testDB' )
            with dbConnection:
                responseList = list_agents( dbConnection, companyKey )
            dbConnection.close()
            data["listofagents"] = responseList
            self.wfile.write(json.dumps(data).encode(encoding='utf_8'))

        # Deletes a specified agent in the database
        if method == "deleteagent":
            companyKey = jsonObject["key"]
            agentID = jsonObject["agentid"]
            dbConnection = create_connection( 'testDB' )
            with dbConnection:
                succes = delete_agent( dbConnection, companyKey, agentID )
            dbConnection.close()
            data["response"] = succes

            self.wfile.write(json.dumps(data).encode(encoding='utf_8'))

        # Updates subscription values for a given company
        if method == "updatesubscription":
            cpu = jsonObject["cpu"]
            ram = jsonObject["ram"]
            companyKey = jsonObject["key"]
            dbConnection = create_connection( 'testDB' )
            with dbConnection:
                succes = update_subscription( dbConnection, cpu, ram, companyKey )
            dbConnection.close()
            data["response"] = succes

            self.wfile.write(json.dumps(data).encode(encoding='utf_8'))
        
        #Deletes all traces of a given company, including agents and subscription data   
        if method == "deletecompany":
            companyKey = jsonObject["key"]
            dbConnection = create_connection( 'testDB' )
            with dbConnection:
                succes = delete_company( dbConnection, companyKey )
            dbConnection.close()
            data["response"] = succes

            self.wfile.write(json.dumps(data).encode(encoding='utf_8'))
        
        #Fetches cpu, ram records for a given company 
        if method == "getsubscription":
            companyKey = jsonObject["key"]
            dbConnection = create_connection( 'testDB' )
            with dbConnection:
                cpuAndRamList = get_subscription( dbConnection, companyKey )
            dbConnection.close()
            print( cpuAndRamList )
            data["cpu"] = cpuAndRamList[0][0]
            data["ram"] = cpuAndRamList[0][1]

            self.wfile.write(json.dumps(data).encode(encoding='utf_8'))

        if method == "gettoken":
            companyKey = jsonObject["key"]
            license = jsonObject["license"]
            # serverToken = jsonObject["token"]

            dbConnection = create_connection( 'testDB' )
            with dbConnection:
                authorized = check_authorization( dbConnection, license, serverToken, companyKey )
            dbConnection.close()
            if authorized:
                placeholder = ""
        
        
        print(jsonObject) # <-- Print post data
        self._set_headers()


def run(server_class=HTTPServer, handler_class=S, addr="localhost", port=8000):
    server_address = (addr, port)
    httpd = server_class(server_address, handler_class)

    print(f"Starting httpd server on {addr}:{port}")
    httpd.serve_forever()

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

def check_authorization( connectionToDB, license, serverToken, key ):
    query = "SELECT Agents.Token, Agents.LicenseKeys FROM Companies JOIN Agents ON Companies.ID = Agents.CompanyID  WHERE Agents.Token = ? AND Agents.LicenseKeys = ? AND Companies.CompanyKey = ?"
    cursor = connectionToDB.cursor()
    cursor.execute( query, ( serverToken, license, key,) )

    rows = cursor.fetchall()
    if len(rows) is 0:
        return False
    else: 
        return True

def create_new_agent( connectionToDB, name, companyKey, licenseKey ):
    query = "INSERT INTO Agents VALUES (NULL, (SELECT ID FROM Companies WHERE CompanyKey == ?), ?, ? )"
    query2 = "SELECT * FROM Agents WHERE Name == ? AND LicenseKey == ?"
    cursor = connectionToDB.cursor()
    cursor.execute( query, ( companyKey, name, licenseKey, ) )
    cursor.execute( query2, ( name, licenseKey, ) )
    
    rows = cursor.fetchall()

    if len(rows) is 0:
        return False
    else:
        return True

def list_agents( connectionToDB, companyKey ):
    connectionToDB.row_factory = sqlite3.Row
    query = "SELECT Agents.name, Agents.LicenseKey, Agents.ID FROM Agents JOIN Companies ON Companies.ID = Agents.CompanyID WHERE Companies.CompanyKey = ?"
    cursor = connectionToDB.cursor()
    cursor.execute( query, ( companyKey, ) )

    rows = cursor.fetchall()
    tmp = [dict(ix) for ix in rows]
    return tmp

def delete_agent( connectionToDB, companyKey, agentID ):
    query = "DELETE FROM Agents WHERE ID = ? AND companyID IN (SELECT Companies.ID FROM Companies WHERE Companies.CompanyKey = ?)"
    query2 = "SELECT * FROM Agents WHERE ID = ?"
    cursor = connectionToDB.cursor()
    cursor.execute( query, ( agentID, companyKey, ) )
    cursor.execute( query2, ( agentID, ) )
    
    rows = cursor.fetchall()

    if len(rows) is 0:
        return True
    else:
        return False

def delete_company( connectionToDB, companyKey ):
    queryDeleteCompany = "DELETE FROM Companies WHERE CompanyKey = ?"
    queryDeleteAllAgents = "DELETE FROM Agents WHERE CompanyID = (SELECT ID FROM Companies WHERE CompanyKey = ?)"
    queryDeleteSubscription = "DELETE FROM Subscriptions WHERE CompanyID = (SELECT ID FROM Companies WHERE CompanyKey = ?)"
    queryCheckIfDeleted = "SELECT * FROM Companies JOIN Agents ON Companies.ID = Agents.CompanyID JOIN Subscriptions ON Companies.ID = Subscriptions.CompanyID WHERE Companies.CompanyKey = ?"
    cursor = connectionToDB.cursor()
    cursor.execute( queryDeleteSubscription, ( companyKey, ) )
    cursor.execute( queryDeleteAllAgents, ( companyKey, ) )
    cursor.execute( queryDeleteCompany, ( companyKey, ) )
    cursor.execute( queryCheckIfDeleted, ( companyKey, ) )

    rows = cursor.fetchall()

    if len(rows) is 0:
        return True
    else:
        return False

def update_subscription( connectionToDB, cpu, ram, companyKey ):
    query = "UPDATE Subscriptions SET CPU_USE = ?, RAM_USE = ? WHERE CompanyID = ( SELECT ID FROM Companies WHERE CompanyKey = ?)"
    query2 = "SELECT CPU, RAM FROM Subscriptions WHERE CPU_USE = ? AND RAM_USE = ? AND CompanyID = (SELECT ID FROM Companies WHERE CompanyKey = ?)"
    cursor = connectionToDB.cursor()
    cursor.execute( query, ( cpu, ram, companyKey, ) )
    cursor.execute( query2, ( cpu, ram, companyKey ) )
    
    rows = cursor.fetchall()

    if len(rows) is 0:
        return False
    else:
        return True

def get_subscription( connectionToDB, companyKey ):
    query = "SELECT Subscriptions.CPU_USE, Subscriptions.RAM_USE FROM Subscriptions JOIN Companies ON Subscriptions.CompanyID = Companies.ID WHERE Companies.CompanyKey = ?"
    cursor = connectionToDB.cursor()
    cursor.execute( query, ( companyKey, ) )

    rows = cursor.fetchall()
    return rows


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Run a simple HTTP server")
    parser.add_argument(
        "-l",
        "--listen",
        default="localhost",
        help="Specify the IP address on which the server listens",
    )
    parser.add_argument(
        "-p",
        "--port",
        type=int,
        default=8000,
        help="Specify the port on which the server listens",
    )
    args = parser.parse_args()
    run(addr=args.listen, port=args.port)