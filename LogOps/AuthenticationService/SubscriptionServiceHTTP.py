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
import socket
import sys
import pymysql
from pymysql import Error
import uuid
import argparse
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import random
import sys
import os



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
        self._set_headers()
        content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
        post_data = self.rfile.read(content_length).decode('UTF-8') # <--- Gets the data itself
        jsonObject = json.loads( post_data )
        method = jsonObject["method"]
        data = {}       

        # Handles the differents types of the methods requests. 
        process_request( method, jsonObject, data )
        self.wfile.write(json.dumps(data).encode(encoding='utf_8'))   


def run(server_class=HTTPServer, handler_class=S, addr="0.0.0.0.", port=8000):    #localhost replaced with 0.0.0.0

    server_address = (addr, port)
    httpd = server_class(server_address, handler_class)

    print(f"Starting Subscription Service on {addr}:{port}")
    httpd.serve_forever()


def process_request( method, jsonObject, data ):
    # Create a new company in the database.
    if method == "newcompany":
        name = jsonObject[ "name" ]
        serverKey = jsonObject[ "serverkey" ]

        if serverKey == SERVERKEY:
            companyKey = uuid.uuid4()
            seq = "ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"
            publicKey = "".join(random.choice(seq) for _ in range(16))

            dbConnection = create_connection(  )
            with dbConnection:
                create_new_company( dbConnection, name, str(companyKey), publicKey )
                success = check_if_company_exists( dbConnection, str(companyKey) )
            dbConnection.close()
            data["response"] = success
        else:
            data["response"] = False
    

    # Checks if a company exists in the database.
    if method == "companykeycheck":
        companyKey = jsonObject["companykey"]
        serverKey = jsonObject["serverkey"]
        if serverKey == SERVERKEY:
            dbConnection = create_connection(  )
            with dbConnection:
                success = check_if_company_exists( dbConnection, companyKey )
            dbConnection.close()
            data["response"] = success
        else:
            data["response"] = False

    # Fetches all records of companies.
    if method == "getcompanies":
        serverKey = jsonObject["serverkey"]
        if serverKey == SERVERKEY:
            dbConnection = create_connection(  )
            with dbConnection:
                responseList = list_companies( dbConnection )
            dbConnection.close()
            data["listofcompanies"] = responseList
        else:
            data["respose"] = False
    

    # Deletes all traces of a given company, including agents and subscription data. 
    if method == "deletecompany":
        CompanyPublic = jsonObject["companypublic"]
        serverKey = jsonObject["serverkey"]
        if serverKey == SERVERKEY:
            dbConnection = create_connection(  )
            with dbConnection:
                success = delete_company( dbConnection, CompanyPublic )
            dbConnection.close()
            data["response"] = success
        else:
            data["response"] = False


    # Create a new agent in the database.
    if method == "newagent":
        name = jsonObject["name"]
        token = jsonObject["token"]
        claims = verify_token( token )
        if claims is False:
            data["response"] = claims
        else:
            tmp = json.loads( claims )
            companyPublic = tmp["companypublic"]
            seq = "ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"
            licenseKey = "-".join("".join(random.choice(seq) for _ in range(4)) for _ in range(6))

            dbConnection = create_connection(  )
            with dbConnection:
                success = create_new_agent( dbConnection, name, companyPublic, licenseKey ) #Query not done
            dbConnection.close()
            data["response"] = success

    
    # Fetches all agents of a given company.
    if method == "agentlist":
        token = jsonObject["token"]
        claims = verify_token( token )
        if claims is False:
            data["response"] = claims
        else:
            tmp = json.loads( claims )
            companyPublic = tmp["companypublic"]
            dbConnection = create_connection(  )
            with dbConnection:
                responseList = list_agents( dbConnection, companyPublic )
            dbConnection.close()
            data["listofagents"] = responseList


    # Deletes a specified agent in the database.
    if method == "deleteagent":
        token = jsonObject["token"]
        agentID = jsonObject["agentid"]
        claims = verify_token( token )
        if claims is False:
            data["response"] = claims 
        else:          
            tmp = json.loads( claims )
            companyPublic = tmp["companypublic"]
            dbConnection = create_connection(  )
            with dbConnection:
                success = delete_agent( dbConnection, companyPublic, agentID )
            dbConnection.close()
            data["response"] = success


    # Updates subscription values for a given company.
    if method == "updatesubscription":
        cpu = jsonObject["cpu"]
        ram = jsonObject["ram"]
        token = jsonObject["token"]
        claims = verify_token( token )
        if claims is False:
            data["response"] = claims
        else:
            tmp = json.loads( claims )
            companyPublic = tmp["companypublic"]
            dbConnection = create_connection(  )
            with dbConnection:
                success = update_subscription( dbConnection, cpu, ram, companyPublic )
            dbConnection.close()
            data["response"] = success

    
            
    # Fetches cpu, ram records for a given company.
    if method == "getsubscription":
        token = jsonObject["token"]
        claims = verify_token( token )
        if claims is False:
            data["response"] = claims
        else:
            tmp = json.loads( claims )
            companyPublic = tmp["companypublic"]
            dbConnection = create_connection(  )
            with dbConnection:
                cpuAndRamList = get_subscription( dbConnection, companyPublic )
            dbConnection.close()
            if cpuAndRamList is False:
                data["response"] = False
            else:
                data["cpu"] = cpuAndRamList[0][0]
                data["ram"] = cpuAndRamList[0][1]
            

    # Checks if the client is authorized, by looking up CompanyKey and LicenseKey in the databas.
    # If authorized, generates a JWT and sends it to client.
    if method == "gettoken":
        companyKey = jsonObject["companykey"]
        license = jsonObject["licensekey"]
        dbConnection = create_connection(  )
        with dbConnection:
            authorized = check_authorization( dbConnection, license, companyKey )
            if license != "NULL":
                agentlist = get_agent_name_and_id( dbConnection, license )
                agentName = agentlist[0][0]
                agentID = agentlist[0][1]
            companyName = get_company_name( dbConnection, companyKey )
        dbConnection.close()

        if license != "NULL":
            if authorized:
                token = make_token( companyKey, agentName, agentID )
        else:
            if authorized:
                token = make_token( companyKey )
        if token is False:
            data["response"] = token
        else:
            data["token"] = token.serialize()
            data["companyname"] = companyName

            
    if method == "verify":
        encryptedToken = jsonObject["token"]
        claims = verify_token( encryptedToken )
        if claims is False:
            data["response"] = claims
        else:
            data = claims


def make_token( companyKey, agentName = None, agentID = None ):

    dbConnection = create_connection(  )
    with dbConnection:
        companyPublic = get_company_public( dbConnection, companyKey )
    dbConnection.close()
    if companyPublic is False:
        return False
    else:
        tmp = {"agentid": agentID, "agentname": agentName, "companypublic": companyPublic}
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
        return ST.claims
    except:
        return False


def check_authorization( connectionToDB, license, companyKey ):
    queryWithoutLicense = "SELECT CompanyKey FROM SubscriptionDB.Companies WHERE CompanyKey = %s"
    cursor = connectionToDB.cursor()
    query = "SELECT Agents.LicenseKey FROM Companies JOIN Agents ON Companies.ID = Agents.CompanyID WHERE Agents.LicenseKey = %s AND Companies.CompanyKey = %s"
    
    if license == "NULL":
        cursor.execute( queryWithoutLicense, ( companyKey, ) ) 
    else: 
        cursor.execute( query, ( license, companyKey, ) )

    rows = cursor.fetchall()
    if len(rows) is 0:
        return False
    else: 
        return True


def create_connection():
    connection = None
    try:
        connection = pymysql.connect( host = HOST, user = USERNAME, passwd = PASSWORD, db = DATABASE )
    except Error as exception:
        print( exception )
    return connection


def create_new_company( connectionToDB, name, companyKey, publicKey ):
    queryCreateCompany = "INSERT INTO Companies VALUES (NULL, %s, %s, %s)"
    queryCreateBlankSubscription = "INSERT INTO Subscriptions SELECT NULL, Companies.ID, 0, 0 FROM Companies WHERE Companies.CompanyKey = %s"
    cursor = connectionToDB.cursor()
    cursor.execute( queryCreateCompany, ( name, companyKey, publicKey, ) )
    cursor.execute( queryCreateBlankSubscription, ( companyKey, ) )
    


def check_if_company_exists( connectionToDB, companyKey ):
    queryCheckCreation = "SELECT * FROM Companies JOIN Subscriptions ON Companies.ID = Subscriptions.CompanyID WHERE Companies.CompanyKey = %s"
    cursor = connectionToDB.cursor()
    cursor.execute( queryCheckCreation, ( companyKey, ) )

    rows = cursor.fetchall()

    if len(rows) is 0:
        return False
    else: 
        return True


def list_companies( connectionToDB ): 
    query = "SELECT CompanyName, CompanyKey, CompanyPublic FROM Companies"
    cursor = connectionToDB.cursor( pymysql.cursors.DictCursor )
    cursor.execute( query )

    rows = cursor.fetchall()
    print(rows)
    listOfRecords = [dict(ix) for ix in rows]
    return listOfRecords


def get_company_public( connectionToDB, companyKey ):
    query = "SELECT CompanyPublic FROM Companies WHERE CompanyKey = %s"
    cursor = connectionToDB.cursor()
    cursor.execute( query, ( companyKey, ) )

    record = cursor.fetchone()

    if len( record ) is 0:
        return False
    else:
        return record[0]


def get_company_name( connectionToDB, companyKey ):
    query = "SELECT CompanyName FROM Companies WHERE CompanyKey = %s"
    cursor = connectionToDB.cursor()
    cursor.execute( query, ( companyKey, ) )

    record = cursor.fetchone()

    if len( record ) is 0:
        return False
    else:
        return record[0]


def delete_company( connectionToDB, companyPublic ):
    queryDeleteCompany = "DELETE FROM Companies WHERE CompanyPublic = %s"
    queryDeleteAllAgents = "DELETE FROM Agents WHERE CompanyID = (SELECT ID FROM Companies WHERE CompanyPublic = %s)"
    queryDeleteSubscription = "DELETE FROM Subscriptions WHERE CompanyID = (SELECT ID FROM Companies WHERE CompanyPublic = %s)"
    queryCheckIfDeleted = "SELECT * FROM Companies JOIN Agents ON Companies.ID = Agents.CompanyID JOIN Subscriptions ON Companies.ID = Subscriptions.CompanyID WHERE Companies.CompanyPublic = %s"
    cursor = connectionToDB.cursor()
    cursor.execute( queryDeleteSubscription, ( companyPublic, ) )
    cursor.execute( queryDeleteAllAgents, ( companyPublic, ) )
    cursor.execute( queryDeleteCompany, ( companyPublic, ) )
    cursor.execute( queryCheckIfDeleted, ( companyPublic, ) )

    rows = cursor.fetchall()

    if len(rows) is 0:
        return True
    else:
        return False


def create_new_agent( connectionToDB, name, companyPublic, licenseKey ):
    query = "INSERT INTO Agents VALUES (NULL, (SELECT ID FROM Companies WHERE CompanyPublic == %s), %s, %s )"
    query2 = "SELECT * FROM Agents WHERE Name == ? AND LicenseKey == ?"
    cursor = connectionToDB.cursor()
    cursor.execute( query, ( companyPublic, name, licenseKey, ) )
    cursor.execute( query2, ( name, licenseKey, ) )
    
    rows = cursor.fetchall()

    if len(rows) is 0:
        return False
    else:
        return True


def list_agents( connectionToDB, companyPublic ):
    query = "SELECT Agents.name, Agents.LicenseKey, Agents.ID FROM Agents JOIN Companies ON Companies.ID = Agents.CompanyID WHERE Companies.CompanyPublic = %s"
    cursor = connectionToDB.cursor( pymysql.cursors.DictCursor )
    cursor.execute( query, ( companyPublic, ) )

    rows = cursor.fetchall()
    listOfRecords = [dict(ix) for ix in rows]
    return listOfRecords

def delete_agent( connectionToDB, companyPublic, agentID ):
    query = "DELETE FROM Agents WHERE ID = ? AND companyID IN (SELECT Companies.ID FROM Companies WHERE Companies.CompanyPublic = %s)"
    query2 = "SELECT * FROM Agents WHERE ID = ?"
    cursor = connectionToDB.cursor()
    cursor.execute( query, ( agentID, companyPublic, ) )
    cursor.execute( query2, ( agentID, ) )
    
    rows = cursor.fetchall()

    if len(rows) is 0:
        return True
    else:
        return False


def update_subscription( connectionToDB, cpu, ram, companyPublic ):
    query = "UPDATE Subscriptions SET CPU_USE = ?, RAM_USE = ? WHERE CompanyID = ( SELECT ID FROM Companies WHERE CompanyPublic = %s)"
    query2 = "SELECT CPU_USE, RAM_USE FROM Subscriptions WHERE CPU_USE = ? AND RAM_USE = ? AND CompanyID = (SELECT ID FROM Companies WHERE CompanyPublic = %s)"
    cursor = connectionToDB.cursor()
    cursor.execute( query, ( cpu, ram, companyPublic, ) )
    cursor.execute( query2, ( cpu, ram, companyPublic ) )
    
    rows = cursor.fetchall()

    if len(rows) is 0:
        return False
    else:
        return True


def get_subscription( connectionToDB, companyPublic ):
    query = "SELECT Subscriptions.CPU_USE, Subscriptions.RAM_USE FROM Subscriptions JOIN Companies ON Subscriptions.CompanyID = Companies.ID WHERE Companies.CompanyPublic = %s"
    cursor = connectionToDB.cursor()
    cursor.execute( query, ( companyPublic, ) )

    rows = cursor.fetchall()
    if len(rows) is 0:
        return False
    else:
        return rows


def get_agent_name_and_id( connectionToDB, license ):
    query = "SELECT Name, ID FROM Agents WHERE LicenseKey = %s"
    cursor = connectionToDB.cursor()
    cursor.execute( query, ( license, ) )

    rows = cursor.fetchall()
    if len(rows) is 0:
        return False
    else:
        return rows


if __name__ == "__main__":

    # Server Key insures that malicious actions cannot take place
    SERVERKEY = "V%ojaT0pX}w12db3@*M+_cq}xB8s4+"
    # Symmetric key used to encode and decode tokens.
    k = {"k":"kASHDEnWf_SW4SAYsO--hyRXPGgTV06ZE1bZBp4ZSxE","kty":"oct"}

    key = jwk.JWK(**k)
    
    HOST = os.environ['MYSQL_HOST']
    print( HOST )
    USERNAME = "root"
    PASSWORD = "123456"
    DATABASE = "SubscriptionDB"

    parser = argparse.ArgumentParser(description="Run a simple HTTP server")
    parser.add_argument(
        "-l",
        "--listen",
        default="0.0.0.0", #localhost changed to 0.0.0.0
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