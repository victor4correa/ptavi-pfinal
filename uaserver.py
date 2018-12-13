#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""Clase (y programa principal) para un servidor de eco en UDP simple."""

import socketserver
import sys
import os
from xml.sax import make_parser
from xml.sax.handler import ContentHandler

class ClientHandler(ContentHandler):
    
    
    def __init__(self):
        atb_account = {"username": "", "passwd": ""}
        atb_uaserver = {"ip": "", "puerto": ""}
        atb_rtpaudio = {"puerto":""}
        atb_regproxy = {"ip":"", "puerto":""}
        atb_log = {"path":""}
        atb_audio = {"path":""}
        self.config = {"account": atb_account, "uaserver": atb_uaserver,
                       "rtpaudio": atb_rtpaudio, "regproxy": atb_regproxy, 
                       "log": atb_log, "audio": atb_audio}
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


        if contenido[0] == "INVITE":
            if len(contenido) != 13:
                self.wfile.write(b"SIP/2.0 400 Bad Request\r\n\r\n")
            else:
                userorigin = contenido[6].split("=")[-1]
                audport = contenido[11]
                self.wfile.write(b"SIP/2.0 100 Trying\r\n\r\n")
                self.wfile.write(b"SIP/2.0 180 Ring\r\n\r\n")
                self.wfile.write(b"SIP/2.0 200 OK\r\n\r\nContent-Type: "
                                 + b"application/sdp\r\n\r\nv=0\r\no="
                                 + bytes(userorigin, "utf-8") + b" " 
                                 + bytes(SERVER, "utf-8")
                                 + b"\r\ns=VictorSession\r\nt=0\r\nm=audio "
                                 + bytes(audport, "utf-8") + b" RTP\r\n")

        elif contenido[0] == "ACK":
                FILE = "cancion.mp3"
                os.system("mp32rtp -i 127.0.0.1 -p 23032 < " + FILE)
        elif contenido[0] == "BYE":
            if len(contenido) != 3:
                self.wfile.write(b"SIP/2.0 400 Bad Request\r\n\r\n")
            else:
                self.wfile.write(b"Terminando llamada\r\n\r\n")

        elif contenido[0] == "REGISTER":
            if len(contenido) != 4:
                self.wfile.write(b"SIP/2.0 400 Bad Request\r\n\r\n")
            else:
                self.wfile.write(b"Registrando...")
        elif contenido[0] != ["REGISTER", "INVITE", "BYE", "ACK"]:
            self.wfile.write(b"SIP/2.0 405 Method Not Allowed\r\n\r\n")


if __name__ == "__main__":
    
    try:
        config_file = sys.argv[1]
    except IndexError:
        sys.exit("Usage: python3 uaserver.py config")

    parser = make_parser()
    cHandler = ClientHandler()
    parser.setContentHandler(cHandler)
    parser.parse(open(config_file))
    datosconfig = cHandler.get_tags()
    print(datosconfig)
    
    PORT = datosconfig[1][1]["puerto"]
    SERVER = datosconfig[1][1]["ip"]
    USER = datosconfig[0][1]["username"]
    AUDPORT = datosconfig[2][1]["puerto"]
    # Creamos servidor de eco y escuchamos
    serv = socketserver.UDPServer(('', int(PORT)), EchoHandler)
    print("Listening...")
    serv.serve_forever()
    
