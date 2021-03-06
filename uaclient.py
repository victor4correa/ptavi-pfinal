#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""Programa cliente que abre un socket a un servidor."""
import hashlib
import socket
import sys
import time
from xml.sax import make_parser
from xml.sax.handler import ContentHandler
# Cliente UDP simple.


def log(event):
    """Funcion que crea un archivo .txt y escribe mensajes de log."""
    event = (" ").join(event.split())
    tiempo = time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))
    linelog = tiempo + " " + event + "\n"
    with open(PATHLOG, "a") as file_log:
        file_log.write(linelog)


class ClientHandler(ContentHandler):
    """Clase manejadora de la configuracion del cliente."""

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


if __name__ == "__main__":

    try:

        METHOD = sys.argv[2]
        OPTION = sys.argv[3]
        config_file = sys.argv[1]

    except IndexError:
        sys.exit("Usage: python uaclient.py  config method option")

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
    PASSWORD = datosconfig[0][1]["passwd"]

    log("Starting...")

    if METHOD == "REGISTER":
        LINE = (METHOD + " sip:" + USER + ":" + PORT + " SIP/2.0\r\n"
                + "Expires:" + OPTION + "\r\n")
    elif METHOD == "INVITE":
        LINE = (METHOD + " sip:" + OPTION + " SIP/2.0\r\n"
                + "Content-Type: application/sdp\r\n\r\nv=0\r\no="
                + USER + " " + SERVER + "\r\ns=VictorSession\r\nt=0\r\nm=audio"
                + " " + AUDPORT + " RTP\r\n")
    elif METHOD == "BYE":
        LINE = (METHOD + " sip:" + USER + " SIP/2.0\r\n")

    try:
        # Creamos el socket, lo configuramos y lo atamos a un servidor/puerto
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as my_socket:
            my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            my_socket.connect((SERVER, int(PROXYPORT)))

            print("Enviando: " + LINE)
            log("Sent to " + SERVER + ":" + PROXYPORT + " " + LINE)
            my_socket.send(bytes(LINE, 'utf-8') + b'\r\n')
            data = my_socket.recv(1024)
            datos = data.decode('utf-8')
            print(datos)
            listadatos = datos.split(" ")
            log("Received from " + SERVER + ":" + PROXYPORT + " "
                + data.decode("utf-8"))
            if METHOD == "REGISTER":
                if listadatos[1] == "401":
                    listanonce = listadatos[-1].split('"')
                    NONCE = listanonce[1]
                    hashcode = hashlib.md5()
                    hashcode.update(bytes(PASSWORD, 'utf-8'))
                    hashcode.update(bytes(NONCE, 'utf-8'))
                    hashcode.digest
                    LINE = (METHOD + " sip:" + USER + ":" + PORT
                            + " SIP/2.0\r\nExpires:" + OPTION + "\r\n"
                            + 'Authorization: Digest response="'
                            + hashcode.hexdigest() + '"')
                    my_socket.send(bytes(LINE, 'utf-8') + b'\r\n')
                    print("Enviando: " + LINE)
                    log("Sent to " + SERVER + ":" + PROXYPORT + " " + LINE)
                    data = my_socket.recv(1024)
                    datos = data.decode('utf-8')
                    print(datos)
                    log("Received from " + SERVER + ":" + PROXYPORT + " "
                        + data.decode("utf-8"))
            if datos[54:56] == "OK":
                if METHOD == "INVITE":
                    LINE = "ACK sip:" + USER + ":" + PORT + " SIP/2.0"
                    my_socket.send(bytes(LINE, "utf-8") + b'\r\n')
                    log("Sent to " + SERVER + ":" + PROXYPORT + " " + LINE)
                    data = my_socket.recv(1024)
                    log("Received from " + SERVER + ":" + PROXYPORT + " "
                        + data.decode("utf-8"))
    except ConnectionRefusedError:
        print("No Server listening at " + SERVER + " port " + PROXYPORT)
        log("Error: No Server listening at " + SERVER + " port " + PROXYPORT)
    log("Finishing...")
