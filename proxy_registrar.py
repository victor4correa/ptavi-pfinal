#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 20 10:49:59 2018

@author: victor4correa
"""
import socketserver
import sys
import time
from random import randint
from xml.sax import make_parser
from xml.sax.handler import ContentHandler

def log(event):
    event = (" ").join(event.split())
    tiempo = time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))
    linelog = tiempo + " " + event + "\n"
    with open(PATHLOG, "a") as file_log:
        file_log.write(linelog)
        
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
        log("Received from " + str(self.client_address[0]) + ":" 
            + str(self.client_address[1])+ " " + line)
        if contenido[0] == "REGISTER":
            print(len(contenido))
            if len(contenido) != 4:
                if len(contenido) != 7:
                    self.wfile.write(b"SIP/2.0 400 Bad Request\r\n\r\n")
                else:
                    """AQUI REGISTRAMOS AL USUARIO"""
                    self.wfile.write(b"REGISTRANDO...")
                    
            else:
                if len(contenido) !=7:
                    NONCE = str(randint(0,999999999999999999999))
                    self.wfile.write(b"SIP/2.0 401 Unauthorized\r\n"
                                     + b"WWW Authenticate: Digest nonce="+ b'"'
                                     + bytes(NONCE, "utf-8") + b'"')
                    
                
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
    PATHLOG = datosconfig[2][1]["path"]
    log("Starting proxy...")
    serv = socketserver.UDPServer(('', int(PROXYPORT)), EchoHandler)
    Line = "Server " + SERVER + " listening at port " + PROXYPORT
    print(Line)
    try:
        serv.serve_forever()
    except KeyboardInterrupt:
        print("Finishing proxy...")
        log("Finishing proxy...")