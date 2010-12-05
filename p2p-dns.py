#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import readline
import sys
from optparse import OptionParser
import socket, ssl
import threading
import os
import re

class Server(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self._stopped = threading.Event()
        self.domains = {}
        self.nodes = {}
        self.port = 8001

    def handle_data(self, stream, source):
        print("got data")
        data = stream.read()

        while data:
            if "P2P-DNS" in data:
                if "REQUEST" in data:
                    if "CONNECTION" in data:
                        stream.write("P2P-DNS 0.1\nACCEPT CONNECTION\n")
                        stream.close()
                        port = int( re.findall(r'PORT (\d+)', data)[0] )
                        self.nodes[source]
                        return
            print(data)
            data = stream.read()

        stream.close()
                
    def add_node(self, host, port):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ssl_sock = ssl.wrap_socket(s, cert_reqs=ssl.CERT_NONE)
        ssl_sock.connect((host, port))

        ssl_sock.write("P2P-DNS 0.1\nREQUEST CONNECTION\nPORT {:}".format(port))

        data = ssl_sock.read()

        if "P2P-DNS" in data:
            if "ACCEPT" in data:
                print("node accepted the connection")
                self.nodes[host] = port
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
        print("started server")
        bindsocket = socket.socket()
        bindsocket.bind(('', self.port))
        bindsocket.listen(5)
        bindsocket.settimeout(1)

        while True:
            if self.stopped():
                print("killed server")
                return

            try:
                newsocket, fromaddr = bindsocket.accept()
                connstream = ssl.wrap_socket(newsocket,
                                         server_side=True,
                                         certfile="server.pem",
                                         keyfile="server.pem",
                                         ssl_version=ssl.PROTOCOL_SSLv3)
                
                self.handle_data(connstream, fromaddr)
            except:
                pass
            

class App(object):
    def __init__(self):
        self.parser = OptionParser(version="%prog 0.1")

    def parse_commandline(self):

        self.parser.add_option("-d",
                          "--daemon",
                          action="store_true",
                          dest="daemon_mode",
                          default=False,
                          help="Starts this server in daemon mode" )

        (options, args) = self.parser.parse_args()

        if options.daemon_mode:
            print("in daemon mode")
            os.spawnl(os.P_NOWAIT, "touch", "touch", "./daemon")
            return True
        return False

    def print_help(self):
        commands = {
            "help":     "print this help",
            "daemon":   "detaches the server and exits this process",
            "connect":  "connect to another node",
            "register": "register a domain with all known nodes",
            "quit":     "exit this process"
            }
        self.parser.print_help()
        print("\n\tCLI commands:")
        for (command, explanaiton) in sorted( commands.items() ):
            print( "{:<10}{:}".format(command, explanaiton) )

    def start_daemon(self):
        proc_id = os.spawnl(os.P_NOWAIT, sys.executable + " " + sys.argv[0], "-d")
        print("process id: {:}".format(proc_id))
        self.quit()

    def start_server(self):
        self.srv = Server()
        self.srv.start()

    def stop(self):
        self.srv.stop()
        self.srv.join()
        sys.exit()

    def run(self):
        daemon_mode = self.parse_commandline()
        self.start_server()
        if not daemon_mode:
            print( """Welcome to this p2p-dns client.
    To run in daemon mode, use '-d' to start or type 'daemon'.
    To find out what other commands exist, type 'help'""" )

            while True:
                try:
                    io = input("~> ")
                    if io == "help":
                        self.print_help()
                    elif io == "daemon":
                        self.start_daemon()
                    elif io == "connect":
                        server = input("server:")
                        port = input("port:")
                        self.srv.add_node(server, port)
                    elif io == "quit":
                        self.stop()
                    else:
                        print("Didn't recognize command. Please retry or type 'help'")
                except EOFError:
                    self.stop()
            
if __name__ == "__main__":
    app = App()
    app.run()
