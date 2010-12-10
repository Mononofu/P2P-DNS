#! /usr/bin/env python
# -*- coding: utf-8 -*-

import threading
import re
from config import *
from database import *
import socket, ssl

class Domain(object):
    def __init__(self, domain, ip, key):
        self.domain = domain
        self.ip = ip
        self.key = key

class Server(threading.Thread):
    def __init__(self, db):
        threading.Thread.__init__(self)
        self._stopped = threading.Event()
        self.port = default_port
        self.database = db

    def isP2PMessage(self, msg):
        return "P2P-DNS" in msg

    def handle_data(self, socket, address):
        print("got data")

        msg = ""
        while True:
            msg += str( socket.read() )
            if msg[-1] == "\0":
                socket.close()
                break
        print(msg)
        return self.handle_message(msg[:-1], socket, address)

    def handle_message(self, msg, socket, address):
        if self.isP2PMessage(msg):
            print("got p2p message")
            if "REQUEST" in msg:
                print("requesting sth")
                if "CONNECTION" in msg:
                    print("a connection!")
                    self.send_message("ACCEPT CONNECTION\nPORT %d" % listen_port,
                                      address)
                    port = int( re.findall(r'PORT (\d+)', msg)[0] )

                    self.database.add_node_to_db(address, port)                
                    print("have new node: %s:%s" % (address, port))
                elif "NODES" in msg:
                    print("all the nodes I know!")
                    msg = "DATA NODES"
                    for (ip, port) in self.nodes.items():
                        msg += "\n%s %s" % (ip, port)
                    self.send_message(msg, address)
            elif "ACCEPT" in msg:
                if "CONNECTION" in msg:
                    print("node accepted the connection")
                    port = int( re.findall(r'PORT (\d+)', msg)[0] )
                    self.add_node_to_db(address, port)
                    self.send_message("REQUEST NODES", address)            
            elif "DATA" in msg:
                if "NODES" in msg:
                    for l in msg.split('\n')[2:]:
                        n = l.split(' ')

                        if n[0] != address and n[0] != my_address:
                            self.send_message("REQUEST CONNECTION\nPORT %d" % listen_port,
                                          n[0],
                                          n[1])
                        
        return True

    def send_message(self, msg, host, port = None):
        if port == None:
            try:
                port = self.nodes[host]
            except KeyError:
                port = default_port
        print("connect to %s:%s" % (host, port))
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ssl_sock = ssl.wrap_socket(s, cert_reqs=ssl.CERT_NONE)
        try:
            ssl_sock.connect((host, port))
        except socket.error:
            print("host %s doesn't accept connection" % host)
            return
        msg = "P2P-DNS 0.1\n" + msg

        # all messages are null-terminated so we know when we have
        # reached the end of it
        # the null will be stripped by the receiver
        if msg[-1] == '\0':
            ssl_sock.write(msg)
        else:
            ssl_sock.write(msg + '\0')
        ssl_sock.close()
                
    def add_node(self, host, port):
        self.send_message("REQUEST CONNECTION\nPORT %s" % listen_port,
                          host,
                          port)
        # that's the port this server is listening on

    def stop(self):
        self._stopped.set()

    def stopped(self):
        return self._stopped.is_set()

    def run(self):
        s = socket.socket()
        s.bind(('', listen_port))
        s.listen(5)
        s.settimeout(0.1)
        
        while not self.stopped():
            try:
                sck, addr = s.accept()
                ssl_socket = ssl.wrap_socket(sck,
                                             server_side=True,
                                             certfile="server.pem",
                                             keyfile="server.pem",
                                             ssl_version=ssl.PROTOCOL_SSLv3)
                self.handle_data(ssl_socket, addr[0])
            except socket.timeout:
                pass
        
        

        
