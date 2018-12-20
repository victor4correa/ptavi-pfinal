#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 20 10:49:59 2018

@author: victor4correa
"""
import socketserver
import sys
import os
from xml.sax import make_parser
from xml.sax.handler import ContentHandler


class ClientHandler(ContentHandler):
    
    
    def __init__(self):
        atb_server = {"name": "", "ip": "", "puerto": ""}
        atb_database = {"path":"", "passwdpath":""}
        atb_log = {"path":""}
        self.config = {"server": atb_server, "database": atb_database, 
                       "log": atb_log}
        self.datosconfig = []
        
    def startElement(self, name, attrs):

        if name in self.config:
            dic = {}
            for atb in self.config[name]:
                dic[atb] = attrs.get(atb, "")
            self.datosconfig.append([name, dic])

    def get_tags(self):
        return self.datosconfig

class EchoHandler(socketserver.DatagramRequestHandler):
    """Echo server class."""

    def handle(self):

        line = self.rfile.read().decode('utf-8')
        contenido = line.split()
        print("El cliente nos manda " + line)

        if contenido[0] == "REGISTER":
            if len(contenido) != 4:
                self.wfile.write(b"SIP/2.0 400 Bad Request\r\n\r\n")
            else:
                self.wfile.write(b"Registrando...")
                
                
                
        elif contenido[0] != ["REGISTER", "INVITE", "BYE", "ACK"]:
            self.wfile.write(b"SIP/2.0 405 Method Not Allowed\r\n\r\n")        

if __name__=="__main__":    
    try:

        config_file = sys.argv[1]

    except IndexError:
        sys.exit("Usage: python proxy_registrar.py  config")

    parser = make_parser()
    cHandler = ClientHandler()
    parser.setContentHandler(cHandler)
    parser.parse(open(config_file))
    datosconfig = cHandler.get_tags()
    print(datosconfig)

    PROXYPORT = datosconfig[0][1]["puerto"]
    SERVER = datosconfig[0][1]["name"]


    serv = socketserver.UDPServer(('', int(PROXYPORT)), EchoHandler)
    Line = "Server " + SERVER + " listening at port " + PROXYPORT
    print(Line)
    serv.serve_forever()