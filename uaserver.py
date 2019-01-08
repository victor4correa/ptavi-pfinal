#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""Clase (y programa principal) para un servidor de eco en UDP simple."""

import socketserver
import sys
import os
import time
from xml.sax import make_parser
from xml.sax.handler import ContentHandler


def log(event):
    """Funcion que crea un archivo .txt y escribe mensajes de log."""
    event = (" ").join(event.split())
    tiempo = time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))
    linelog = tiempo + " " + event + "\n"
    with open(PATHLOG, "a") as file_log:
        file_log.write(linelog)


class ClientHandler(ContentHandler):
    """Clase manejadora de la configuracion del servidor."""

    def __init__(self):
        """Creacion del diccionario de configuracion."""
        atb_account = {"username": "", "passwd": ""}
        atb_uaserver = {"ip": "", "puerto": ""}
        atb_rtpaudio = {"puerto": ""}
        atb_regproxy = {"ip": "", "puerto": ""}
        atb_log = {"path": ""}
        atb_audio = {"path": ""}
        self.config = {"account": atb_account, "uaserver": atb_uaserver,
                       "rtpaudio": atb_rtpaudio, "regproxy": atb_regproxy,
                       "log": atb_log, "audio": atb_audio}
        self.datosconfig = []

    def startElement(self, name, attrs):
        """Inicializacion del diccionario de configuracion."""
        if name in self.config:
            dic = {}
            for atb in self.config[name]:
                dic[atb] = attrs.get(atb, "")
            self.datosconfig.append([name, dic])

    def get_tags(self):
        """Devuelve los datos de configuracion dentro del diccionario."""
        return self.datosconfig


class EchoHandler(socketserver.DatagramRequestHandler):
    """Echo server class."""

    def handle(self):
        """Maneja los codigos de respuesta de la parte servidora."""
        line = self.rfile.read().decode('utf-8')
        contenido = line.split()
        print("El cliente nos manda " + line)
        log("Received from " + SERVER + ":" + PROXYPORT + " " + line)

        if contenido[0] == "INVITE":
            if len(contenido) != 13:
                self.wfile.write(b"SIP/2.0 400 Bad Request\r\n\r\n")
                line = "SIP/2.0 400 Bad Request\r\n\r\n"
                log("Sent to " + SERVER + ":" + PROXYPORT + " " + line)
            else:
                userorigin = contenido[6].split("=")[-1]
                audport = contenido[11]
                self.wfile.write(b"SIP/2.0 100 Trying\r\n\r\n")
                line = "SIP/2.0 100 Trying"
                log("Sent to " + SERVER + ":" + PROXYPORT + " " + line)
                self.wfile.write(b"SIP/2.0 180 Ring\r\n\r\n")
                line = "SIP/2.0 180 Ring"
                log("Sent to " + SERVER + ":" + PROXYPORT + " " + line)
                self.wfile.write(b"SIP/2.0 200 OK\r\n\r\nContent-Type: "
                                 + b"application/sdp\r\n\r\nv=0\r\no="
                                 + bytes(userorigin, "utf-8") + b" "
                                 + bytes(SERVER, "utf-8")
                                 + b"\r\ns=VictorSession\r\nt=0\r\nm=audio "
                                 + bytes(audport, "utf-8") + b" RTP\r\n")
                line = "SIP/2.0 200 OK"
                log("Sent to " + SERVER + ":" + PROXYPORT + " " + line)

        elif contenido[0] == "ACK":
                USER_PORT = contenido[1].split(":")[-1]
                FILE = "cancion.mp3"
                os.system("mp32rtp -i 127.0.0.1 -p" + USER_PORT + "< " + FILE)
                self.wfile.write(b"Recibiendo archivo multimedia\r\n\r\n")
                log("Sent to " + SERVER + ":" + PROXYPORT + " " + FILE)
        elif contenido[0] == "BYE":
            if len(contenido) != 3:
                self.wfile.write(b"SIP/2.0 400 Bad Request\r\n\r\n")
                line = "SIP/2.0 400 Bad Request"
                log("Sent to " + SERVER + ":" + PROXYPORT + " " + line)
            else:
                self.wfile.write(b"SIP/2.0 200 OK Terminando llamada\r\n\r\n")
                line = "Terminando llamada"
                log("Sent to " + SERVER + ":" + PROXYPORT + " " + line)

        elif contenido[0] != ["INVITE", "BYE", "ACK"]:
            self.wfile.write(b"SIP/2.0 405 Method Not Allowed\r\n\r\n")
            line = "SIP/2.0 405 Method Not Allowed"
            log("Sent to " + SERVER + ":" + PROXYPORT + " " + line)


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

    PORT = datosconfig[1][1]["puerto"]
    SERVER = datosconfig[1][1]["ip"]
    USER = datosconfig[0][1]["username"]
    AUDPORT = datosconfig[2][1]["puerto"]
    PROXYPORT = datosconfig[3][1]["puerto"]
    PATHLOG = datosconfig[4][1]["path"]
    # Creamos servidor de eco y escuchamos
    serv = socketserver.UDPServer(('', int(PORT)), EchoHandler)
    print("Listening...")
    log("Starting...")
    try:
        serv.serve_forever()
    except KeyboardInterrupt:
        print("Finishing server...")
        log("Finishing...")
