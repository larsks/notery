#!/usr/bin/python

import multiprocessing
import random
import json

import zmq
from zmq.eventloop.ioloop import IOLoop, PeriodicCallback
from zmq.eventloop.zmqstream import ZMQStream

class ZMQProcess (multiprocessing.Process):

    ctx  = None
    loop = None

    def __init__(self):
        super(ZMQProcess, self).__init__()

    def setup(self):
        self.ctx = zmq.Context()
        self.loop = IOLoop.instance()

    def stream(self, sock_type, sock_addr, sock_bind, 
            callback=None, subscribe=''):

        assert self.ctx is not None

        sock_addr = sock_addr % {
                'port': random.randint(1024,65535),
                }

        s = ZMQStream(
                self.ctx.socket(sock_type))

        if sock_type == zmq.SUB:
            s.setsockopt(zmq.SUBSCRIBE, subscribe)

        if sock_bind:
            s.bind(sock_addr)
        else:
            s.connect(sock_addr)

        if callback:
            s.on_recv(callback)

        return (s, sock_addr)

class MessageHandler (object):

    def deserialize(self, msg):
        return json.loads(msg[0])

    def __call__ (self, msg):
        method, data = self.deserialize(msg)
        getattr(self, 'handle_%s' % method)(data)

