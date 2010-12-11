#! /usr/bin/env python
# -*- coding: utf-8 -*-

import threading
import re
from config import *
from database import *
from stoppable_thread import *
import socket, ssl

class MessageSender(StoppableThread):
    def __init__(self, db):
        StoppableThread.__init__(self)
        self.database = db
        self.msg_to_send = []
        self.cv = threading.Condition()
        
    def send_message(self, msg, host, port = None):
        self.cv.acquire()
        self.msg_to_send.append( (msg, host, port) )
        self.cv.notify()
        self.cv.release()

    def run(self):

        while not self.stopped():

            self.cv.acquire()
            while len(self.msg_to_send) < 1:
                self.cv.wait(0.05) # time out after 100 ms
                if self.stopped():
                    return
                
            msg, host, port = self.msg_to_send.pop()
            
            if port == None:
                port = self.database.get_port(host)
                
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

            self.cv.release()

        
class Server(StoppableThread):
    def __init__(self, db):
        StoppableThread.__init__(self)
        self.port = default_port
        self.database = db
        self.sender = MessageSender(db)
        self.sender.start()

    def isP2PMessage(self, msg):
        return "P2P-DNS" in msg

    def handle_data(self, socket, address):
        msg = ""
        while True:
            msg += str( socket.read() )
            if msg[-1] == "\0":
                socket.close()
                break
        return self.handle_message(msg[:-1], socket, address)

    def handle_message(self, msg, socket, address):
        if self.isP2PMessage(msg):
            if "REQUEST" in msg:
                print "requesting", 
                if "CONNECTION" in msg:
                    print("a connection!")
                    self.sender.send_message("ACCEPT CONNECTION\nPORT %d"
                                             % listen_port,
                                             address)
                    port = int( re.findall(r'PORT (\d+)', msg)[0] )

                    self.database.add_node(address, port)                
                    print("have new node: %s:%s" % (address, port))
                    self.sender.send_message("REQUEST NODES", address)
                    self.sender.send_message("REQUEST DOMAINS", address)
                elif "NODES" in msg:
                    print("all the nodes I know!")
                    msg = "DATA NODES"
                    for (ip, port) in self.database.get_nodes().items():
                        msg += "\n%s %s" % (ip, port)
                    self.sender.send_message(msg, address)
                elif "DOMAINS" in msg:
                    print("all the domains I know!")
                    msg = "DATA DOMAINS"
                    for (domain, record) in self.database.get_domains().items():
                        # "domain ip ttl timestamp key"
                        msg += "\n%s %s %d %s %s" % (domain,
                                                record.ip,
                                                record.ttl,
                                                record.timestamp,
                                                record.key)
                    self.sender.send_message(msg, address)
            elif "ACCEPT" in msg:
                if "CONNECTION" in msg:
                    print("node accepted the connection")
                    port = int( re.findall(r'PORT (\d+)', msg)[0] )
                    self.database.add_node(address, port)
                    self.sender.send_message("REQUEST NODES", address)
                    self.sender.send_message("REQUEST DOMAINS", address)
            elif "DATA" in msg:
                print "got",
                if "NODES" in msg:
                    print("nodes")
                    for l in msg.split('\n')[2:]:
                        n = l.split(' ')

                        if (n[0] != address and
                            n[0] != my_address and
                            not self.database.have_node(n[0]) ):
                            self.sender.send_message("REQUEST CONNECTION\nPORT %d"
                                              % listen_port,
                                              n[0],
                                              int(n[1]))
                elif "DOMAINS" in msg:
                    print("domains")
                    for l in msg.split('\n')[2:]:
                        n = l.split(' ')
                        self.database.add_domain(n[0], n[1], n[2], n[3], n[4]) 
        return True
                
    def add_node(self, host, port):
        self.sender.send_message("REQUEST CONNECTION\nPORT %s" % listen_port,
                          host,
                          port)
        # that's the port this server is listening on

    def register_domain(self, domain, ip, key, ttl = default_ttl):
        # put in db
        self.database.add_domain(domain, ip, key, ttl)

        # announce to all known nodes
        for (node_ip, node_port) in self.database.get_nodes().items():
            # "domain ip ttl timestamp key"
            self.sender.send_message("DATA DOMAINS\n%s %s %d %s %s" % (
                    domain,
                    ip,
                    ttl,
                    time.time() + default_record_lifetime,
                    key),
                                     node_ip,
                                     node_port)

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
        self.sender.stop()
        self.sender.join()
        
        

        
