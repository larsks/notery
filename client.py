#!/usr/bin/python

import os
import sys
import argparse
import json

import zmq

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('--socket', '-s',
            default='tcp://localhost:2138')
    return p.parse_args()

def send(s, method, **kwargs):
    s.send_multipart([method, json.dumps(kwargs)])
    msg = s.recv_multipart()
    print 'got:', msg

def main():
    opts = parse_args()

    ctx = zmq.Context()
    s = ctx.socket(zmq.REQ)
    s.connect(opts.socket)

    return s

if __name__ == '__main__':
    s = main()


