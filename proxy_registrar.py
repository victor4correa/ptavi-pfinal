#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Servidor proxy intermediario en la comunicacion y encargado del registro."""
import socket
import socketserver
import sys
import time
import hashlib
import json
from random import randint
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
        atb_server = {"name": "", "ip": "", "puerto": ""}
        atb_database = {"path": "", "passwdpath": ""}
        atb_log = {"path": ""}
        self.config = {"server": atb_server, "database": atb_database,
                       "log": atb_log}
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

    database = []
    portsend = [0]
    NONCE = str(randint(0, 999999999999999999999))

    def handle(self):
        """Maneja los codigos de respuesta de la parte servidora."""
        USERPORT = self.client_address[1]
        line = self.rfile.read().decode('utf-8')
        contenido = line.split()
        print("El cliente nos manda " + line)
        log("Received from " + str(self.client_address[0]) + ":"
            + str(USERPORT) + " " + line)
        if contenido[0] == "REGISTER":
            if len(contenido) != 4:
                if len(contenido) != 7:
                    self.wfile.write(b"SIP/2.0 400 Bad Request\r\n\r\n")
                    line = "SIP/2.0 400 Bad Request"
                    log("Sent to " + str(self.client_address[0]) + ":"
                        + str(USERPORT) + " " + line)
                else:
                    reg_user = {}
                    user = contenido[1].split(":")[1]
                    with open("./passwords", "r") as usuarios:
                        reg_user = json.load(usuarios)
                        if user in reg_user:
                            password = reg_user[user]
                        else:
                            self.wfile.write(b"SIP/2.0 404 User Not Found"
                                             + b"\r\n\r\n")
                    hashreceived = contenido[6].split('"')[1]
                    hashcode = hashlib.md5()
                    hashcode.update(bytes(password, 'utf-8'))
                    hashcode.update(bytes(self.NONCE, 'utf-8'))
                    hashcode.digest
                    if hashreceived == hashcode.hexdigest():
                        """AQUI REGISTRAMOS AL USUARIO"""
                        if contenido[3].split(":")[-1] == "0":
                            line = "SIP/2.0 200 OK USUARIO BORRADO"
                            self.wfile.write(bytes(line, 'utf-8'))
                            log("Sent to " + str(self.client_address[0]) + ":"
                                + str(self.client_address[1]) + " " + line)
                        else:
                            line = "SIP/2.0 200 OK USUARIO REGISTRADO"
                            self.wfile.write(bytes(line, 'utf-8'))
                            line = "USUARIO REGISTRADO"
                            log("Sent to " + str(self.client_address[0]) + ":"
                                + str(self.client_address[1]) + " " + line)
                            user = contenido[1].split(":")[1]
                            ip = IP
                            port = contenido[1].split(":")[-1]
                            tiempo = time.strftime("%Y%m%d%H%M%S",
                                                   time.localtime(time.time()))
                            expires = contenido[3].split(":")[-1]

                            listausuarios = {"user": user, "ip": ip,
                                             "port": port, "tiempo": tiempo,
                                             "expires": expires}
                            self.database.append([listausuarios])
                            print(self.database)
                            with open("./database.txt", "a") as file_db:
                                file_db.write(str(listausuarios) + "\n")
                            print("USUARIO REGISTRADO CON EXITO")
                    else:
                        self.NONCE = str(randint(0, 999999999999999999999))
                        self.wfile.write(b"SIP/2.0 401 Unauthorized\r\n"
                                         + b"WWW Authenticate: Digest nonce="
                                         + b'"' + bytes(self.NONCE, "utf-8")
                                         + b'"\r\n\r\n')
            elif len(contenido) == 4:
                self.wfile.write(b"SIP/2.0 401 Unauthorized\r\n"
                                 + b"WWW Authenticate: Digest nonce="
                                 + b'"' + bytes(self.NONCE, "utf-8")
                                 + b'"\r\n\r\n')
                line = "SIP/2.0 401 Unauthorized WWWAuthenticate:Digest nonce="

                log("Sent to " + str(self.client_address[0]) + ":"
                    + str(self.client_address[1]) + " " + line
                    + self.NONCE)

        elif contenido[0] == "INVITE":
            try:
                user1 = self.database[1][0]['user']
                user2 = self.database[0][0]['user']
                if contenido[1].split(":")[-1] == user1:
                    self.portsend[0] = self.database[1][0]["port"]
                elif contenido[1].split(":")[-1] == user2:
                    self.portsend[0] = self.database[0][0]["port"]
                with socket.socket(socket.AF_INET,
                                   socket.SOCK_DGRAM) as my_socket:
                    my_socket.setsockopt(socket.SOL_SOCKET,
                                         socket.SO_REUSEADDR, 1)
                    my_socket.connect((IP, int(self.portsend[0])))
                    my_socket.send(bytes(line, 'utf-8') + b'\r\n')
                    log("Sent to " + IP + ":" + self.portsend[0] + " " + line)
                    data = my_socket.recv(1024)
                    datos = data.decode('utf-8')
                    log("Received from " + IP + ":" + self.portsend[0] + " "
                        + line)
                    print(datos)
                self.wfile.write(bytes(datos, 'utf-8'))
            except IndexError:
                line = "SIP/2.0 404 User Not Found\r\n\r\n"
                log("Sent to " + IP + ":" + str(self.portsend[0]) + " " + line)
                self.wfile.write(b"SIP/2.0 404 User Not Found\r\n\r\n")
                print("SIP/2.0 404 User Not Found")

        elif contenido[0] == "ACK":
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as my_socket:
                my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                my_socket.connect((IP, int(self.portsend[0])))
                my_socket.send(bytes(line, 'utf-8') + b'\r\n')
                log("Sent to " + IP + ":" + self.portsend[0] + " " + line)
                data = my_socket.recv(1024)
                datos = data.decode('utf-8')
                log("Received from " + IP + ":" + self.portsend[0] + " "
                    + line)
                print(datos)
            self.wfile.write(bytes(datos, 'utf-8'))

        elif contenido[0] == "BYE":
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as my_socket:
                my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                my_socket.connect((IP, int(self.portsend[0])))
                my_socket.send(bytes(line, 'utf-8') + b'\r\n')
                log("Sent to " + IP + ":" + self.portsend[0] + " " + line)
                data = my_socket.recv(1024)
                datos = data.decode('utf-8')
                log("Received from " + IP + ":" + self.portsend[0] + " "
                    + line)
                print(datos)
            self.wfile.write(bytes(datos, 'utf-8'))

        elif contenido[0] != ["REGISTER", "INVITE", "BYE", "ACK"]:
            self.wfile.write(b"SIP/2.0 405 Method Not Allowed\r\n\r\n")
            line = "SIP/2.0 405 Method Not Allowed"
            log("Sent to " + str(self.client_address[0]) + ":"
                + str(self.client_address[1]) + " " + line)

        if len(self.database) >= 1:
            exp_user = 0.0
            for i in [0, (len(self.database)-1)]:
                tiempo_actual = time.time()
                exp_user = (float(self.database[i][0]['tiempo'])
                            + float(self.database[i][0]['expires']))
                if tiempo_actual >= exp_user:
                        print(self.database[i][0]['user'] + "ha expirado...")
                        del self.database[i]


if __name__ == "__main__":
    try:

        config_file = sys.argv[1]

    except IndexError:
        sys.exit("Usage: python proxy_registrar.py  config")

    parser = make_parser()
    cHandler = ClientHandler()
    parser.setContentHandler(cHandler)
    parser.parse(open(config_file))
    datosconfig = cHandler.get_tags()
    IP = datosconfig[0][1]["ip"]
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
