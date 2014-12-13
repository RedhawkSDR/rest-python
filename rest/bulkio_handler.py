#
# This file is protected by Copyright. Please refer to the COPYRIGHT file
# distributed with this source distribution.
#
# This file is part of REDHAWK rest-python.
#
# REDHAWK rest-python is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# REDHAWK rest-python is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see http://www.gnu.org/licenses/.
#
# system imports
import logging

from bulkio.bulkioInterfaces import BULKIO__POA

# third party imports
from tornado import ioloop, gen
from tornado import websocket

import numpy

from model.domain import Domain, ResourceNotFound
from asyncport import AsyncPort


def _floats2bin(flist):
    """
        Converts a list of python floating point values
        to a packed array of IEEE 754 32 bit floating point
    """
    return numpy.array(flist).astype('float32').tostring()


def _doubles2bin(flist):
    """
        Converts a list of python floating point values
        to a packed array of IEEE 754 64 bit floating point
    """
    return numpy.array(flist).astype('float64').tostring()


def _pass_through(flist):
    return flist


class BulkIOWebsocketHandler(websocket.WebSocketHandler):

    data_conversion_map = {
        'dataFloat':  _floats2bin,
        'dataDouble': _doubles2bin,
        'dataOctet': _pass_through,
        'dataShort': _pass_through
    }

    def initialize(self, kind, redhawk=None, _ioloop=None):
        self.kind = kind
        self.redhawk = redhawk
        if not _ioloop:
            _ioloop = ioloop.IOLoop.current()
        self._ioloop = _ioloop

    @gen.coroutine
    def open(self, *args):
        try:
            logging.debug("BulkIOWebsocketHandler open kind=%s, path=%s", self.kind, args)
            obj, path = yield self.redhawk.get_object_by_path(args, path_type=self.kind)
            logging.debug("Found object %s", dir(obj))

            for p in obj.ports:
                if p.name == path[0]:
                    if p._direction == 'Uses':
                        data_type = p._using.name
                        namespace = p._using.nameSpace

                        if namespace == 'BULKIO':
                            self.port = obj.getPort(str(path[0]))
                            logging.debug("Found port %s", self.port)

                            self.converter = self.data_conversion_map[data_type]

                            bulkio_poa = getattr(BULKIO__POA, data_type)
                            logging.debug(bulkio_poa)

                            self.async_port = AsyncPort(bulkio_poa, self._pushSRI, self._pushPacket)
                            self._portname = 'myport%s' % id(self)
                            self.port.connectPort(self.async_port.getPort(), self._portname)

                            break
                        else:
                            raise ValueError("Port '%s' is not a BULKIO port" % path[0])
                    else:
                        raise ValueError("Port '%s' is not a uses" % path[0])
            else:
                raise ValueError("Could not find port of name '%s'" % path[0])

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
        try:
            self.port.disconnectPort(self._portname)
        except Exception, e:
            logging.exception('Error disconnecting port %s' % self._portname)

    def _pushSRI(self, SRI):
        self._ioloop.add_callback(self.write_message, 
            dict(hversion=SRI.hversion,
                xstart=SRI.xstart,
                xdelta=SRI.xdelta,
                xunits=SRI.xunits,
                subsize=SRI.subsize,
                ystart=SRI.ystart,
                ydelta=SRI.ydelta,
                yunits=SRI.yunits,
                mode=SRI.mode,
                streamID=SRI.streamID,
                blocking=SRI.blocking,
                keywords=dict(((kw.id, kw.value.value()) for kw in SRI.keywords))))

    def _pushPacket(self, data, ts, EOS, stream_id):

        # FIXME: need to write ts, EOS and stream id
        self._ioloop.add_callback(self.write_message, self.converter(data), binary=True)

    def write_message(self, *args, **ioargs):
        # hide WebSocketClosedError because it's very likely
        try:
            super(BulkIOWebsocketHandler, self).write_message(*args, **ioargs)
        except websocket.WebSocketClosedError:
            logging.debug('Received WebSocketClosedError. Ignoring')
