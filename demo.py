#!/usr/bin/python

import os
import sys
import argparse
import json
import time

import zmq
from zmq.eventloop.ioloop import PeriodicCallback

from notery.base import ZMQProcess, MessageHandler

class DemoHandler (MessageHandler):

    def handle_ping (self, msg):
        print 'PING', msg

class DemoApp(ZMQProcess):
    def __init__ (self):
        super(DemoApp, self).__init__()

    def setup(self):
        super(DemoApp, self).setup()

        self.pub, self.pub_addr = self.stream(zmq.PUB, 'tcp://*:%(port)s', True)
        self.sub, sub_addr = self.stream(zmq.SUB, self.pub_addr, False)
        self.heartbeat = PeriodicCallback(self.ping, 1000, self.loop)

        self.sub.on_recv(DemoHandler())

    def ping(self):
        print 'SEND PING'
        self.pub.send(json.dumps(['ping', time.time()]))

    def run(self):
        print 'RUN'
        self.setup()

        print 'START HEARTBEAT'
        self.heartbeat.start()

        print 'START LOOP'
        self.loop.start()

        print 'STARTED'
        print self.loop
        print self.heartbeat

    def stop(self):
        self.heartbeat.stop()
        self.loop.stop()

def parse_args():
    p = argparse.ArgumentParser()
    return p.parse_args()

def echo(msg):
    print 'ECHO:', msg

def main():
    opts = parse_args()

    app = DemoApp()
    app.start()
    app.join()

if __name__ == '__main__':
    main()

