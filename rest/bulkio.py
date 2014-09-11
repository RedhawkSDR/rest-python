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
from model.domain import Domain




class BulkIOWebsocketHandler(websocket.WebSocketHandler):

    def initialize(self, kind):
        self.kind = kind

    def open(self, *args):
        logging.debug("BulkIOWebsocketHandler open kind=%s, args=%s", self.kind, args)
        obj, path = Domain.locate(args, path_type=self.kind)
        logging.debug("Found object %s", dir(obj))
        self.port = obj.getPort(path[0])
        logging.debug("Found port %s", self.port)

    def on_message(self, message):
        logging.debug('stream message[%d]: %s', len(message), message)

    def on_close(self):
        logging.debug('Stream CLOSE')