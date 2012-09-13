#!/usr/bin/python

class NoteryError(Exception):
    id = 'E_NOTERY_ERROR'
    description = 'Unknown error'

class InvalidNotificationError (NoteryError):
    id = 'E_INVALID'
    description = 'Invalid notification'

class UnknownNotificationError (NoteryError):
    id = 'E_UNKNOWN'
    description = 'Unknown notification'

class NoteryProtocolError (NoteryError):
    id = 'E_PROTOCOL'
    description = 'Protocol error'

