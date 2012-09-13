#!/usr/bin/python

import os
import sys
import argparse
import json
import logging
import weakref

import zmq

from base import ZMQProcess, MessageHandler
from errors import *

DEFAULT_SOCKET_URL = 'tcp://*:2138'

class Note(dict):
    def __init__(self, id, tag, **kwargs):
        super(Note, self).__init__(**kwargs)

        self['id'] = id
        self['tag'] = tag

class RepStreamHandler (MessageHandler):
    def __init__(self, parent):
        super(RepStreamHandler, self).__init__()
        self.parent = parent

        self.setup_logging()

    def setup_logging(self):
        self.log = logging.getLogger('notery.RepStreamHandler')

    def __call__ (self, *args, **kwargs):
        try:
            msgtype, data = super(RepStreamHandler, self).__call__(*args, **kwargs)
            self.log.debug('received: %s' % msgtype)
            self.reply(msgtype, data)
        except NoteryError, detail:
            self.reply('error', {'message': str(detail)})
        except AttributeError:
            self.reply('error', {
                'message': 'Unknown message type',
                })
        except:
            self.reply('error', {
                'message': 'Unexpected application error',
                })
            raise

    def reply(self, msgtype, data):
        self.parent.s_rep.send_multipart(
                [ msgtype, json.dumps(data) ])

    def handle_ping(self, data):
        return ('pong', data)

    def handle_publish(self, data):
        return ('publish', self.parent.publish(data))

    def handle_retract(self, data):
        return ('retract', self.parent.retract(**data))

    def handle_list(self, data):
        return ('list', self.parent.list())

class Notary (ZMQProcess):
    def __init__ (self, socket=DEFAULT_SOCKET_URL):
        super(Notary, self).__init__()
        self.sock_url = socket

    def setup(self):
        super(Notary, self).setup()

        self.setup_logging()
        self.setup_sockets()
        self.setup_notes()

    def setup_logging(self):
        self.log = logging.getLogger('notery')
        self.log.info('Initialized logging.')

    def setup_notes(self):
        self.notes_by_lid = {}
        self.notes_by_rid = weakref.WeakValueDictionary()
        self.notid = 0

    def setup_sockets(self):
        self.s_rep, self.s_rep_addr = self.stream(
                zmq.REP,
                self.sock_url,
                True,
                callback = RepStreamHandler(self))

    def stop(self):
        self.loop.stop()

    def publish(self, note):
        note = Note(note)

        if not 'tag' in note or not 'id' in note:
            raise InvalidNotificationError(
                    'Notifications must have both tag and id.')

        if 'lid' in note:
            lid = note['lid']
            self.log.debug('updating notification lid = %s' % lid)
        else:
            lid = self.notid
            self.notid += 1
            note['lid'] = lid
            self.log.debug('allocated new lid = %s' % lid)

        self.notes_by_lid[lid] = note
        self.notes_by_rid[(note['id'], note['tag'])] = note

        return lid

    def list(self):
        return self.notes_by_lid.values()

    def retract(self, id=None, lid=None, tag=None):
        try:
            self.log.debug('retract, id=%s, lid=%s, tag=%s' % (
                id, lid, tag))
            if lid is not None:
                note = self.notes_by_lid[lid]
                del self.notes_by_lid[lid]
            elif id is not None and tag is not None:
                note = self.notes_by_rid[(id, tag)]
                lid = note['lid']
                del self.notes_by_lid[lid]
            else:
                raise KeyError()
        except KeyError:
            raise UnknownNotificationError('Unable to find a matching notification.')

        return lid

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('--socket', '-s', default='tcp://*:2138')
    p.add_argument('--debug', action='store_true')
    return p.parse_args()

def main():
    opts = parse_args()

    if opts.debug:
        loglevel = logging.DEBUG
    else:
        loglevel = logging.INFO

    logging.basicConfig(
            level=loglevel)

    n = Notary(socket=opts.socket)
    n.start()

if __name__ == '__main__':
    main()

