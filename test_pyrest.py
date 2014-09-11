#!/usr/bin/env python

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
from tornado import websocket

# application imports
from pyrest import Application

# all method returning suite is required by tornado.testing.main()
def all():
   return unittest.TestLoader().loadTestsFromModule(__import__(__name__))

# NOTE: Use individual AyncHTTPClient requests, not self.http_client
#       because each http client contains the response.
#
#         AsyncHTTPClient(self.io_loop).fetch("http://www.tornadoweb.org/", self.stop)
#         response = self.wait()

class RESTfulTest(AsyncHTTPTestCase, LogTrapTestCase):

    # def setUp(self):
    #     super(RESTfulTest, self).setUp()
    #     rtl_app.RTLApp('REDHAWK_DEV').stop_survey()


    def get_app(self):
        return Application(debug=True, _ioloop=self.io_loop)

    def test_domain_get(self):
        AsyncHTTPClient(self.io_loop).fetch(self.get_url('/rh/rest/domains'), self.stop)
        response = self.wait()
        self.assertEquals(200, response.code)
        # get the json reply
        data = json.loads(response.body)

        self.assertEquals(list, type(data['domains']))


    @tornado.testing.gen_test
    def test_status_ws(self):

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
        msg = yield conn1.read_message()
        try:
            data = json.loads(msg)
        except ValueError:
            data = dict(data=msg)

        if data.get('error', None):
            self.fail('Recieved websockt error %s' % data)
        conn1.protocol.close()

if __name__ == '__main__':

    # FIXME: Make command line arugment to replace rtl_app with mock
    #rtl_app = mock_rtl_app
   # logging.basicConfig(level=logging.debug)
    tornado.testing.main()

