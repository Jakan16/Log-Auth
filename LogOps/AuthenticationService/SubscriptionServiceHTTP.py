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
        self.send_header("Content-type", "application/json")
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
        # Does not do anything with posted data.
        content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
        post_data = self.rfile.read(content_length).decode('UTF-8') # <--- Gets the data itself
        jsonObject = json.loads( post_data )
        method = jsonObject["method"]
        data = {}
        
        # Create a new company in the database.
        if method == "newcompany":
            name = jsonObject[ "name" ]
            serverKey = jsonObject[ "serverkey" ]

            if serverKey == SERVERKEY:
                companyKey = uuid.uuid4()
                seq = "ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"
                publicKey = "".join(random.choice(seq) for _ in range(16))

                dbConnection = create_connection( 'testDB' )
                with dbConnection:
                    create_new_company( dbConnection, name, str(companyKey), publicKey )
                    succes = check_if_company_exists( dbConnection, companyKey )
                dbConnection.close()
                data["response"] = succes
                # print(data)
                self.wfile.write(json.dumps(data).encode(encoding='utf_8'))
            else:
                data["response"] = False
                self.wfile.write(json.dumps(data).encode(encoding='utf_8'))
        

        # Checks if a company exists in the database.
        if method == "companykeycheck":
            companyKey = jsonObject["companykey"]
            serverKey = jsonObject["serverkey"]
            if serverKey == SERVERKEY:
                dbConnection = create_connection( 'testDB' )
                with dbConnection:
                    succes = check_if_company_exists( dbConnection, companyKey )
                dbConnection.close()
                data["response"] = succes
                self.wfile.write(json.dumps(data).encode(encoding='utf_8'))
            else:
                data["response"] = False
                self.wfile.write(json.dumps(data).encode(encoding='utf_8'))

        # Fetches all records of companies.
        if method == "getcompanies":
            serverKey = jsonObject["serverkey"]
            if serverKey == SERVERKEY:
                dbConnection = create_connection( 'testDB' )
                with dbConnection:
                    responseList = list_companies( dbConnection )
                dbConnection.close()
                data["listofcompanies"] = responseList
                self.wfile.write(json.dumps(data).encode(encoding='utf_8'))
            else:
                data["respose"] = False
                self.wfile.write(json.dumps(data).encode(encoding='utf_8'))
        

        # Deletes all traces of a given company, including agents and subscription data. 
        if method == "deletecompany":
            publicKey = jsonObject["publickey"]
            serverKey = jsonObject["serverkey"]
            if serverKey == SERVERKEY:
                dbConnection = create_connection( 'testDB' )
                with dbConnection:
                    succes = delete_company( dbConnection, publicKey )
                dbConnection.close()
                data["response"] = succes
                self.wfile.write(json.dumps(data).encode(encoding='utf_8'))
            else:
                data["response"] = False
                self.wfile.write(json.dumps(data).encode(encoding='utf_8'))
                

        # Create a new agent in the database.
        if method == "newagent":
            name = jsonObject["name"]
            companyKey = jsonObject["companykey"]

            seq = "ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"
            licenseKey = "-".join("".join(random.choice(seq) for _ in range(4)) for _ in range(6))

            dbConnection = create_connection( 'testDB' )
            with dbConnection:
                succes = create_new_agent( dbConnection, name, companyKey, licenseKey ) #Query not done
            dbConnection.close()
            data["response"] = succes

            self.wfile.write(json.dumps(data).encode(encoding='utf_8'))
        
        # Fetches all agents of a given company.
        if method == "agentlist":
            companyKey = jsonObject["companykey"]
            dbConnection = create_connection( 'testDB' )
            with dbConnection:
                responseList = list_agents( dbConnection, companyKey )
            dbConnection.close()
            data["listofagents"] = responseList
            self.wfile.write(json.dumps(data).encode(encoding='utf_8'))

        # Deletes a specified agent in the database.
        if method == "deleteagent":
            companyKey = jsonObject["companykey"]
            agentID = jsonObject["agentid"]
            dbConnection = create_connection( 'testDB' )
            with dbConnection:
                succes = delete_agent( dbConnection, companyKey, agentID )
            dbConnection.close()
            data["response"] = succes

            self.wfile.write(json.dumps(data).encode(encoding='utf_8'))

        # Updates subscription values for a given company.
        if method == "updatesubscription":
            cpu = jsonObject["cpu"]
            ram = jsonObject["ram"]
            companyKey = jsonObject["companykey"]
            dbConnection = create_connection( 'testDB' )
            with dbConnection:
                succes = update_subscription( dbConnection, cpu, ram, companyKey )
            dbConnection.close()
            data["response"] = succes

            self.wfile.write(json.dumps(data).encode(encoding='utf_8'))
        
                
        # Fetches cpu, ram records for a given company.
        if method == "getsubscription":
            companyKey = jsonObject["companykey"]
            dbConnection = create_connection( 'testDB' )
            with dbConnection:
                cpuAndRamList = get_subscription( dbConnection, companyKey )
            dbConnection.close()
            print( cpuAndRamList )
            data["cpu"] = cpuAndRamList[0][0]
            data["ram"] = cpuAndRamList[0][1]

            self.wfile.write(json.dumps(data).encode(encoding='utf_8'))

        # Checks if the client is authorized, by looking up CompanyKey and LicenseKey in the databas.
        # If authorized, generates a JWT and sends it to client.
        if method == "gettoken":
            companyKey = jsonObject["companykey"]
            license = jsonObject["license"]

            dbConnection = create_connection( 'testDB' )
            with dbConnection:
                authorized = check_authorization( dbConnection, license, companyKey )
                agentlist = get_agent_name_and_id( dbConnection, license )
                agentName = agentlist[0][0]
                agentID = agentlist[0][1]
            dbConnection.close()
            if authorized:
                token = make_token( companyKey, agentName, agentID )
                print( token.serialize() )
                data["token"] = token.serialize()

                self.wfile.write(json.dumps(data).encode(encoding='utf_8'))
                
        if method == "verify":
            encryptedToken = jsonObject["token"]
            tmp = verify_token( encryptedToken )
            if tmp is False:
                data["response"] = tmp
                self.wfile.write(json.dumps(data).encode(encoding='utf_8'))
            else:
                # print( tmp )
                data = tmp
                self.wfile.write(data.encode(encoding='utf_8'))
            
        
        print(jsonObject) # <-- Print post data
        self._set_headers()


def run(server_class=HTTPServer, handler_class=S, addr="localhost", port=8000):
    

    server_address = (addr, port)
    httpd = server_class(server_address, handler_class)

    print(f"Starting httpd server on {addr}:{port}")
    httpd.serve_forever()

def make_token( companyKey, agentName, agentID ):
    tmp = {"agentid": agentID, "agentname": agentName, "companykey": companyKey}
    tmp2 = json.dumps(tmp)
    token = jwt.JWT( header = {"alg": "HS256"},
                     claims = tmp2)
    token.make_signed_token( key )
    encryptedToken = jwt.JWT( header = {"alg":"A256KW", "enc":"A256CBC-HS512"}, 
                              claims = token.serialize() )
    encryptedToken.make_encrypted_token( key )
    return encryptedToken


def verify_token( token ):
    try:
        ET = jwt.JWT( key = key, jwt = token )
        ST = jwt.JWT( key = key, jwt = ET.claims )
        # print( ST.claims )
        return ST.claims
    except:
        return False


def check_authorization( connectionToDB, license, key ):
    query = "SELECT Agents.LicenseKey FROM Companies JOIN Agents ON Companies.ID = Agents.CompanyID  WHERE Agents.LicenseKey = ? AND Companies.CompanyKey = ?"
    cursor = connectionToDB.cursor()
    cursor.execute( query, ( license, key, ) )

    rows = cursor.fetchall()
    if len(rows) is 0:
        return False
    else: 
        return True


def create_connection( db ):
    connection = None
    try:
        connection = sqlite3.connect( db )
    except Error as exception:
        print( exception )
    return connection


def create_new_company( connectionToDB, name, companyKey, publicKey ):
    queryCreateCompany = "INSERT INTO Companies VALUES (NULL, ?, ?, ?)"
    queryCreateBlankSubscription = "INSERT INTO Subscriptions SELECT NULL, Companies.ID, 0, 0 FROM Companies WHERE Companies.CompanyKey = ?"
    cursor = connectionToDB.cursor()
    cursor.execute( queryCreateCompany, ( name, companyKey, publicKey, ) )
    cursor.execute( queryCreateBlankSubscription, ( companyKey, ) )
    


def check_if_company_exists( connectionToDB, company ):
    queryCheckCreation = "SELECT * FROM Companies JOIN Subscriptions ON Companies.ID = Subscriptions.CompanyID WHERE Companies.CompanyKey = ?"
    cursor = connectionToDB.cursor()
    cursor.execute( queryCheckCreation, ( companyKey, ) )

    rows = cursor.fetchall()

    if len(rows) is 0:
        return False
    else: 
        return True


def list_companies( connectionToDB ):
    connectionToDB.row_factory = sqlite3.Row
    query = "SELECT Name, CompanyKey, CompanyPublic FROM Companies?"
    cursor = connectionToDB.cursor()
    cursor.execute( query )

    rows = cursor.fetchall()
    listOfRecords = [dict(ix) for ix in rows]
    return listOfRecords


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
    listOfRecords = [dict(ix) for ix in rows]
    return listOfRecords

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

def delete_company( connectionToDB, publicKey ):
    queryDeleteCompany = "DELETE FROM Companies WHERE PublicKey = ?"
    queryDeleteAllAgents = "DELETE FROM Agents WHERE CompanyID = (SELECT ID FROM Companies WHERE PublicKey = ?)"
    queryDeleteSubscription = "DELETE FROM Subscriptions WHERE CompanyID = (SELECT ID FROM Companies WHERE PublicKey = ?)"
    queryCheckIfDeleted = "SELECT * FROM Companies JOIN Agents ON Companies.ID = Agents.CompanyID JOIN Subscriptions ON Companies.ID = Subscriptions.CompanyID WHERE Companies.PublicKey = ?"
    cursor = connectionToDB.cursor()
    cursor.execute( queryDeleteSubscription, ( publicKey, ) )
    cursor.execute( queryDeleteAllAgents, ( publicKey, ) )
    cursor.execute( queryDeleteCompany, ( publicKey, ) )
    cursor.execute( queryCheckIfDeleted, ( publicKey, ) )

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


def get_agent_name_and_id( connectionToDB, license ):
    query = "SELECT Name, ID FROM Agents WHERE LicenseKey = ?"
    cursor = connectionToDB.cursor()
    cursor.execute( query, ( license, ) )

    rows = cursor.fetchall()
    return rows


def get_subscription( connectionToDB, companyKey ):
    query = "SELECT Subscriptions.CPU_USE, Subscriptions.RAM_USE FROM Subscriptions JOIN Companies ON Subscriptions.CompanyID = Companies.ID WHERE Companies.CompanyKey = ?"
    cursor = connectionToDB.cursor()
    cursor.execute( query, ( companyKey, ) )

    rows = cursor.fetchall()
    return rows


if __name__ == "__main__":

    # Server Key insures that malicious actions cannot take place
    SERVERKEY = "V%ojaT0pX}w12db3@*M+_cq}xB8s4+"
    print(serverKey)
    # New Key when the service restarts!
    k = {"k":"kASHDEnWf_SW4SAYsO--hyRXPGgTV06ZE1bZBp4ZSxE","kty":"oct"}

    key = jwk.JWK(**k)
    
    # encryptionKey = jwk.JWK( generate = 'oct', size = 256 )


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