#!/usr/bin/env python
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
import unittest
import json
import logging
import time
import struct
import threading
from functools import partial

# tornado imports
import tornado
import tornado.testing
from tornado.testing import AsyncHTTPTestCase, LogTrapTestCase
from tornado.httpclient import AsyncHTTPClient, HTTPRequest
from tornado import websocket, gen

# application imports
from pyrest import Application
from base import JsonTests
from defaults import Default
from rest.bulkio_handler import DATA_CONVERSION_MAP

# all method returning suite is required by tornado.testing.main()
#def all():
#   return unittest.TestLoader().loadTestsFromModule(__import__(__name__))


class BulkIOTests(JsonTests, AsyncHTTPTestCase, LogTrapTestCase):

    # def setUp(self):
    #     super(RESTfulTest, self).setUp()
    #     rtl_app.RTLApp('REDHAWK_DEV').stop_survey()

    def setUp(self):
        super(JsonTests, self).setUp()
        json, resp = self._json_request(
            '/domains/%s/applications' % Default.DOMAIN_NAME,
            200,
            'POST',
            {'name': Default.WAVEFORM,
             'started': True }
        )
        self.assertTrue('launched' in json)
        self.base_url = '/domains/%s/applications/%s' % (Default.DOMAIN_NAME, json['launched'])

        json, resp = self._json_request(self.base_url, 200)
        self.assertList(json, 'components')
        self.assertTrue(json['components'])

        self.components = json['components']

    def tearDown(self):
        self._json_request(
            self.base_url,
            200,
            'DELETE'
        )
        super(BulkIOTests, self).tearDown()



    def get_app(self):
        return Application(debug=True, _ioloop=self.io_loop)

    @tornado.testing.gen_test
    def test_bulkio_ws(self):

        # NOTE: A timeout means the website took too long to respond
        # it could mean that bulkio port is not sending data
        cid = next((cp['id'] for cp in self.components if cp['name'] == 'SigGen'), None)
        if not cid:
            self.fail('Unable to find SigGen component')

        url = self.get_url("%s/components/%s/ports/dataFloat_out/bulkio"%(Default.REST_BASE+self.base_url,cid)).replace('http','ws')
        conn1 = yield websocket.websocket_connect(url,
                                                  io_loop=self.io_loop) 

        foundSRI = False
        for x in xrange(10):
            msg = yield conn1.read_message()
            try:
                data = json.loads(msg)
                logging.debug("Got SRI %s", data)
                foundSRI = True
                props = set(('hversion', 'xstart', 'xdelta', 'xunits',
                            'subsize', 'ystart', 'ydelta', 'yunits', 'mode',
                            'streamID', 'blocking', 'keywords'))
                missing = props.difference(data.keys())
                if missing:
                   self.fail("Missing SRI properties %s" % missing)
            except ValueError:
                data = dict(data=msg)

        if data.get('error', None):
            self.fail('Recieved websocket error %s' % data)
        #conn1.protocol.close()
        conn1.close()

        # wait a little bit to force close to take place in ioloop
        # (if we return without waiting, ioloop closes before websocket closes)
        x = yield gen.Task(self.io_loop.add_timeout, time.time() + .5)

        if not foundSRI:
            self.fail('Did not receive SRI')


class TestDataConverters(unittest.TestCase):

    def _testDataConverter(self, dtype, bpa, input, expected):
        """
          Test data converter output
        :param dtype: the BULKIO data type
        :param bpa: bytes per atom
        :param input: list of atoms
        :param expected: string array expected
        """
        # do sanity check on input
        if bpa * len(input) != len(expected):
            self.fail("Bad expected value for %s type.  Expected %d bytes, got %d bytes" %
                      (dtype, bpa * len(input), len(expected)))
        converter = DATA_CONVERSION_MAP[dtype]
        self.assertEquals(expected, converter(input))

    def testDataConverterDouble(self):
        dmax = 1.7e308
        dmin = 1.7e-308
        data = [dmax, dmin, -dmax, -dmin, 0.0]
        self._testDataConverter('dataDouble', 8, data, struct.pack('=ddddd', *data), )

    def testDataConverterFloat(self):
        fmax = 3.4e38
        fmin = 3.4e-38
        data = [fmax, fmin, -fmax, -fmin, 0.0]
        self._testDataConverter('dataFloat', 4, data, struct.pack('=fffff', *data))

    def testDataConverterShort(self):
        smax = (1<<15)-1
        smin = -(1<<15)
        data = [smax, smin, 15, -15, 0]
        self._testDataConverter('dataShort', 2, data, struct.pack('=hhhhh', *data))

    def testDataConverterLong(self):
        lmax = (1<<31)-1
        lmin = -(1<<31)
        data = [lmax, lmin, 15, -15, 0]
        self._testDataConverter('dataLong', 4, data, struct.pack('=lllll', *data))

    def testDataConverterLongLong(self):
        lmax = (1<<63)-1
        lmin = -(1<<63)
        data = [lmax, lmin, 15, -15, 0]
        self._testDataConverter('dataLongLong', 8, data, struct.pack('=qqqqq', *data))

    def testDataConverterOctet(self):
        omax = (1<<8)-1
        omin = 0
        data = [omax, omin, 15, 0]
        self._testDataConverter('dataOctet', 1, data, struct.pack('=BBBB', *data))

    def testDataConverterULong(self):
        lmax = (1<<32)-1
        lmin = 0
        data = [lmax, lmin, 15, 0]
        self._testDataConverter('dataUlong', 4, data, struct.pack('=LLLL', *data))

    def testDataConverterULongLong(self):
        lmax = (1<<64)-1
        lmin = 0
        data = [lmax, lmin, 15, 0]
        self._testDataConverter('dataUlongLong', 8, data, struct.pack('=QQQQ', *data))

    def testDataConverterUShort(self):
        lmax = (1<<16)-1
        lmin = 0
        data = [lmax, lmin, 15, 0]
        self._testDataConverter('dataUshort', 2, data, struct.pack('=HHHH', *data))

    def testDataConverterChar(self):
        lmax = (1<<7)-1
        lmin = -(1<<7)
        data = [lmax, lmin, 15, -15, 0]
        self._testDataConverter('dataChar', 1, data, struct.pack('=bbbbb', *data))




if __name__ == '__main__':

    tornado.testing.main()

