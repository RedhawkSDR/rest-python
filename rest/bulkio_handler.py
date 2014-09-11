# system imports
import logging

from bulkio.bulkioInterfaces import BULKIO, BULKIO__POA

# third party imports
import tornado
from tornado import ioloop
from tornado.httpclient import AsyncHTTPClient
from tornado import web
from tornado import websocket
from tornado import gen

import numpy

from model.domain import Domain, ResourceNotFound
from asyncport import AsyncPort


def _floats2bin(flist):
    """
        Converts a list of python floating point values
        to a packed array of IEEE 754 32 bit floating point
    """
    return numpy.array(flist).astype('float32').tostring()

class BulkIOWebsocketHandler(websocket.WebSocketHandler):

    def initialize(self, kind, _ioloop=None):
        self.kind = kind
        if not _ioloop:
            _ioloop = ioloop.IOLoop.current()
        self._ioloop = _ioloop


    def _pushSRI(self, SRI):
        self._ioloop.add_callback(self.write_message, 
            dict(hversion=SRI.hrversion,
                xstart=SRI.xstart,
                xdelta=SRI.xdelta,
                xunits=SRI.xunits,
                subsize=SRI.subsize,
                ystart=SRI.ystart,
                ydelta=SRI.ydelta,
                yunits=SRI.yunits,
                mode=SRI.mode,
                streamID=SRI.streamID,
                blocking=SRI.blocking))

    def _pushPacket(self, data, ts, EOS, stream_id):
        # FIXME: need to write ts, EOS and stream id
        self._ioloop.add_callback(self.write_message, _floats2bin(data), binary=True)

    def open(self, *args):
        try:
            logging.debug("BulkIOWebsocketHandler open kind=%s, args=%s", self.kind, args)
            obj, path = Domain.locate(args, path_type=self.kind)
            logging.debug("Found object %s", dir(obj))
            self.port = obj.getPort(path[0])
            logging.debug("Found port %s", self.port)

            self.async_port = AsyncPort(BULKIO__POA.dataFloat, self._pushSRI, self._pushPacket)
            self.port.connectPort(self.async_port.getPort(), 'myport')
        except ResourceNotFound, e:
            self.write_message(dict(error='ResourceNotFound', message=str(e)))
            self.close()
        except Exception, e:
            logging.exception('Error with request %s' % self.request.full_url())
            self.write_message(dict(error='SystemError', message=str(e)))
            self.close()


    def on_message(self, message):
        logging.debug('stream message[%d]: %s', len(message), message)

    def on_close(self):
        logging.debug('Stream CLOSE')