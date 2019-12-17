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
        if method == "newcompany":
            name = jsonObject[ "name" ]
            randomKey = uuid.uuid4()
            dbConnection = create_connection( 'testDB' )
            with dbConnection:
                create_new_company( dbConnection, name, str(randomKey) )
            dbConnection.close()
            data["name"] = name
            data["companykey"] = str(randomKey)
            print(data)
            self.wfile.write(json.dumps(data).encode(encoding='utf_8'))

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