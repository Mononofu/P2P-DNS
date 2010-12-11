#! /usr/bin/env python3
# -*- coding: utf-8 -*-

from config import *
import time
import sqlite3

class Domain(object):
    def __init__(self, domain, ip, key, ttl = default_ttl, timestamp = time.time() + default_record_lifetime):
        self.domain = str(domain)
        self.ip = str(ip)
        self.key = str(key)
        self.ttl = int(ttl)
        self.timestamp = timestamp

class Database(object):
    def __init__(self):
        self.domains = {}
        self.nodes = {}

        c = sqlite3.connect('./db')

        c.execute("create table if not exists nodes (ip text, port text)")
        c.execute("create table if not exists domains (domain text, ip text, key text, ttl text, timestamp text)")
        c.commit()
        for row in c.execute("select * from nodes"):
            self.nodes[row[0]] = int(row[1])      
        for row in c.execute("select * from domains"):
            self.domains[row[0]] = Domain(row[0], row[1], row[2], row[3], row[4])   
        c.close()

    def print_nodes(self):
        c = sqlite3.connect('./db')
        for row in c.execute("select * from nodes"):
            print("%s:%s" % (row[0], row[1])) 
        c.close()

    def print_domains(self):
        c = sqlite3.connect('./db')
        for row in c.execute("select * from domains"):
            print("%s: %s, TTL: %s" % (row[0], row[1], row[3])) 
        c.close()

    def add_node(self, host, port):
        if host not in self.nodes:
            self.nodes[host] = int(port)

            c = sqlite3.connect('./db')
            c.execute("insert into nodes values (?, ?)", (host, port))
            c.commit()
            c.close()

    def add_domain(self, domain, ip, key, ttl = 120, timestamp = time.time() ):
        if domain not in self.domains:
            self.domains[domain] = Domain(domain, ip, key, ttl, timestamp)

            c = sqlite3.connect('./db')
            c.execute("insert into domains values (?, ?, ?, ?, ?)", (domain,
                                                                     ip,
                                                                     key,
                                                                     ttl,
                                                                     timestamp))
            c.commit()
            c.close()
