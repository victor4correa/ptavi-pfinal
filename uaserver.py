#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""Clase (y programa principal) para un servidor de eco en UDP simple."""

import socketserver
import sys
import os


class EchoHandler(socketserver.DatagramRequestHandler):
    """Echo server class."""

    def handle(self):

        line = self.rfile.read().decode('utf-8')
        contenido = line.split()
        print("El cliente nos manda " + line)
        """
        if len(contenido) != 4:
            self.wfile.write(b"SIP/2.0 400 Bad Request\r\n\r\n")
       
        else:
         """
        if contenido[0] == "INVITE":
            if len(contenido) != 13:
                self.wfile.write(b"SIP/2.0 400 Bad Request\r\n\r\n")
            else:
                self.wfile.write(b"SIP/2.0 100 Trying\r\n\r\n")
                self.wfile.write(b"SIP/2.0 180 Ringing\r\n\r\n")
                self.wfile.write(b"SIP/2.0 200 OK\r\n\r\n")
        elif contenido[0] == "ACK":
                os.system("mp32rtp -i 127.0.0.1 -p 23032 < " + FILE)
        elif contenido[0] == "BYE":
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
        PORT = sys.argv[2]
        FILE = sys.argv[3]
        # Creamos servidor de eco y escuchamos
        serv = socketserver.UDPServer(('', int(PORT)), EchoHandler)
        print("Listening...")
        serv.serve_forever()
    except IndexError:
        sys.exit("Usage: python3 uaserver.py IP port audio_file")
