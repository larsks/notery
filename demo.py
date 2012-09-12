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

    def handle_ping (self, data):
        print 'RECEIVE PING', data

class DemoApp(ZMQProcess):
    def __init__ (self):
        super(DemoApp, self).__init__()

    def setup(self):
        super(DemoApp, self).setup()

        self.pub, self.pub_addr = self.stream(zmq.PUB, 'tcp://*:%(port)s', True)
        self.sub, sub_addr = self.stream(zmq.SUB, self.pub_addr, False,
                callback=DemoHandler())
        self.heartbeat = PeriodicCallback(self.ping, 1000, self.loop)

    def ping(self):
        print 'SEND PING'
        self.pub.send_multipart(['ping', json.dumps(['ping', time.time()])])

    def local_run(self):
        print 'START HEARTBEAT'
        self.heartbeat.start()

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

