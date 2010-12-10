#! /usr/bin/env python
# -*- coding: utf-8 -*-

from database import *
from config import *
import threading
import zmq

class DNSModule(threading.Thread):
    def __init__(self, db, port = dns_module_listen_port):
        threading.Thread.__init__(self)
        self._stopped = threading.Event()
        self.database = db
        self.port = port
        
    def stop(self):
        self._stopped.set()

    def stopped(self):
        return self._stopped.is_set()

    def run(self):
        context = zmq.Context()
        socket = context.socket(zmq.REP)
        socket.bind("tcp://*:%d" % self.port)
        
        poller = zmq.Poller()
        poller.register(socket, zmq.POLLIN)

        while not self.stopped():
            # timeout so we can free the socket and quit the program
            # if necessary; in ms
            socks = dict(poller.poll(timeout=100))
            
            if socket in socks and socks[socket] == zmq.POLLIN:
                print("got dns question")
                msg = socket.recv()
                if msg in self.database.domains:
                    domain = self.database.domains[msg]
                    socket.send("%s %d" % (domain.ip, domain.ttl))
                else:
                    socket.send("0.0.0.0 %d" % default_ttl)
                    # signal that domain doesn't exist
