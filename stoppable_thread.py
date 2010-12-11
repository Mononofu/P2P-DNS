#! /usr/bin/env python
# -*- coding: utf-8 -*-

import threading

class StoppableThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self._stopped = threading.Event()
    
    def stop(self):
        self._stopped.set()

    def stopped(self):
        return self._stopped.is_set()
