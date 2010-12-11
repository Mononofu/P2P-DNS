#! /usr/bin/env python
# -*- coding: utf-8 -*-
import socket

default_port = 8001 # default port for adding a new server
listen_port = 8001 # port for the server to listen on
my_address = [ip for ip in socket.gethostbyname_ex(socket.gethostname())[2]
              if not ip.startswith("127.")][0]
dns_module_listen_port = 8002
default_ttl = 60   # in seconds
default_record_lifetime = 3600 * 24 * 30 # one month, duh
