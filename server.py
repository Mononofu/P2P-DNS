#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import threading
import re
from config import *
import sqlite3
import socket, ssl

class Domain(object):
    def __init__(self, domain, ip, key):
        self.domain = domain
        self.ip = ip
        self.key = key

class Server(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self._stopped = threading.Event()
        self.domains = {}
        self.nodes = {}
        self.port = default_port

        c = sqlite3.connect('./db')
 
        c.execute("create table if not exists nodes (ip text, port text)")
        c.execute("create table if not exists domains (domain text, ip text, key text)")
        c.commit()
        for row in c.execute("select * from nodes"):
            self.nodes[row[0]] = row[1]      
        for row in c.execute("select * from domains"):
            self.domains[row[0]] = Domain(row[0], row[1], row[2])   
        c.close()

    def print_nodes(self):
        c = sqlite3.connect('./db')
        for row in c.execute("select * from nodes"):
            print("%s:%s" % (row[0], row[1])) 
        c.close()

        
    def isP2PMessage(self, msg):
        return "P2P-DNS" in msg

    def handle_data(self, socket, address):
        print("got data")

        while True:
            msg = str( socket.read() )

            print(msg)

            if not self.handle_message(msg, socket, address):
                break
            
        socket.close()

    def handle_message(self, msg, socket, address):
        if self.isP2PMessage(msg):
            print("got p2p message")
            if "REQUEST" in msg:
                print("requesting sth")
                if "CONNECTION" in msg:
                    print("a connection!")
                    socket.write(b"P2P-DNS 0.1\nACCEPT CONNECTION\n")
                    port = int( re.findall(r'PORT (\d+)', msg)[0] )
                    self.nodes[address] = port

                    c = sqlite3.connect('./db')
                    c.execute("insert into nodes values (?, ?)", (address, port))
                    c.commit()
                    c.close()
                    
                    print("have new node: %s:%s" % (address, port))
                    return True
                elif "NODES" in msg:
                    print("all the nodes I know!")
                    msg = "P2P-DNS 0.1\nKNOWN NODES"
                    for (ip, port) in self.nodes.items():
                        msg += "\n%s %s" % (ip, port)
                    socket.write(msg)
                    return False
        return False

    def add_node_to_db(self, host, port):
        if host not in self.nodes:
            self.nodes[host] = port

            c = sqlite3.connect('./db')
            c.execute("insert into nodes values (?, ?)", (host, port))
            c.commit()
            c.close()
                
    def add_node(self, host, port):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ssl_sock = ssl.wrap_socket(s, cert_reqs=ssl.CERT_NONE)
        try:
            ssl_sock.connect((host, port))
        except socket.error:
            print("host %s doesn't accept connection" % host)
            return

        ssl_sock.write("P2P-DNS 0.1\nREQUEST CONNECTION\nPORT %s" % port)

        data = str( ssl_sock.read() )

        if "P2P-DNS" in data:
            if "ACCEPT" in data:
                print("node accepted the connection")

                self.add_node_to_db(host, port)

                ssl_sock.write("P2P-DNS 0.1\nREQUEST NODES")
                data = str( ssl_sock.read() )
                for l in data.split('\n')[2:]:
                    n = l.split(' ')
                    self.nodes_to_ask[n[0]] = int(n[1])
            else:
                print("node refused connection")
        else:
            print("couldn't find p2p-dns server")

        ssl_sock.close()

    def stop(self):
        self._stopped.set()

    def stopped(self):
        return self._stopped.is_set()

    def run(self):
        s = socket.socket()
        s.bind(('', listen_port))
        s.listen(5)
        s.settimeout(1)
        
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
        
        

        
