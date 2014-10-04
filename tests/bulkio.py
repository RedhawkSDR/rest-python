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

# all method returning suite is required by tornado.testing.main()
#def all():
#   return unittest.TestLoader().loadTestsFromModule(__import__(__name__))


class BulkIOTests(AsyncHTTPTestCase, LogTrapTestCase):

    # def setUp(self):
    #     super(RESTfulTest, self).setUp()
    #     rtl_app.RTLApp('REDHAWK_DEV').stop_survey()


    def get_app(self):
        return Application(debug=True, _ioloop=self.io_loop)

    @tornado.testing.gen_test
    def test_bulkio_ws(self):

        # NOTE: A timeout means the website took too long to respond
        # it could mean that bulkio port is not sending data

        response = yield AsyncHTTPClient(self.io_loop).fetch(self.get_url('/rh/rest/domains/REDHAWK_DEV/waveforms'))
        self.assertEquals(200, response.code)
        data = json.loads(response.body)
        wid = next((wf['id'] for wf in data['waveforms'] if wf['name'].startswith('Rtl_FM')), None)
        if not wid:
            self.fail('Unable to find RTL Waveform')            

        response = yield AsyncHTTPClient(self.io_loop).fetch(self.get_url("/rh/rest/domains/REDHAWK_DEV/waveforms/%s/components/"%wid))
        self.assertEquals(200, response.code)
        data = json.loads(response.body)

        cid = next((cp['id'] for cp in data['components'] if cp['name'] == 'NOOP'), None)
        if not cid:
            self.fail('Unable to find NOOP component')

        url = self.get_url("/rh/rest/domains/REDHAWK_DEV/waveforms/%s/components/%s/ports/dataFloat_out/bulkio"%(wid,cid)).replace('http','ws')
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

