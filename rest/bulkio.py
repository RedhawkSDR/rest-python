# system imports
import json
import os,sys
import logging
import time
import functools

# third party imports
import tornado
from tornado import ioloop
from tornado.httpclient import AsyncHTTPClient
from tornado import web
from tornado import websocket
from tornado import gen
import gevent
import threading


class BulkIOWebsocketHandler(websocket.WebSocketHandler):

    def initialize(self, kind):
        self.kind = kind

    def open(self, *args):
        logging.debug('Event handler open kind=%s, args=%s', self.kind, args)
        print args

    def on_message(self, message):
        logging.debug('stream message[%d]: %s', len(message), message)

    def on_close(self):
        logging.debug('Stream CLOSE')    