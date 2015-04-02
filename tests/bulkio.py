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



if __name__ == '__main__':

    tornado.testing.main()

