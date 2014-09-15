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
from tornado import websocket, gen

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


# Moment is taken from tornado.gen.moment part of Tornado 4.0
# Yielding a moment will have the ioloop process other things
_moment = tornado.concurrent.Future()
_moment.set_result(None)

class RESTfulTest(AsyncHTTPTestCase, LogTrapTestCase):

    # def setUp(self):
    #     super(RESTfulTest, self).setUp()
    #     rtl_app.RTLApp('REDHAWK_DEV').stop_survey()


    def get_app(self):
        return Application(debug=True, _ioloop=self.io_loop)

    @tornado.testing.gen_test
    def test_domain_get_list(self):
        for url in ('/rh/rest/domains', '/rh/rest/domains/'):
            response = yield AsyncHTTPClient(self.io_loop).fetch(self.get_url(url))
            self.assertEquals(200, response.code)
            data = json.loads(response.body)
            self.assertEquals(list, type(data['domains']))


    @tornado.testing.gen_test
    def test_domain_get_instance(self):        
        response = yield AsyncHTTPClient(self.io_loop).fetch(self.get_url('/rh/rest/domains/REDHAWK_DEV'))
        self.assertEquals(200, response.code)
        data = json.loads(response.body)

        for name in ('waveforms', 'properties', 'deviceManagers', 'id', 'name'):
            self.assertTrue(name in data, "json missing %s" % name)


    def test_domain_get_failure(self):
        # callback must be used to get response to non-200 HTTPResponse
        AsyncHTTPClient(self.io_loop).fetch(self.get_url('/rh/rest/domains/REDHAWK_DEV_FOO'), self.stop)
        response = self.wait()

        self.assertEquals(404, response.code)
        pdata = json.loads(response.body)
        logging.debug("Found port data %s", pdata)
        # FIXME: Check error response



    @tornado.testing.gen_test
    def test_waveform_port_get(self):
        # get a list of waveforms
        response = yield AsyncHTTPClient(self.io_loop).fetch(self.get_url('/rh/rest/domains/REDHAWK_DEV/waveforms'))
        self.assertEquals(200, response.code)
        data = json.loads(response.body)
        for wf in data['waveforms']:
            portr = yield AsyncHTTPClient(self.io_loop).fetch(self.get_url('/rh/rest/domains/REDHAWK_DEV/waveforms/%s/ports' % wf['id']))
            self.assertEquals(200, portr.code)
            pdata = json.loads(portr.body)
            # FIXME: Test against a waveform with ports
            logging.debug("Found port data %s", pdata)
            break
        else:
            self.fail('Unable to find any waveforms')


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
            self.fail('Recieved websockt error %s' % data)
        #conn1.protocol.close()
        conn1.close()

        # wait a little bit to force close to take place in ioloop
        # (if we return without waiting, ioloop closes before websocket closes)
        x = yield gen.Task(self.io_loop.add_timeout, time.time() + .5)

        if not foundSRI:
            self.fail('Did not receive SRI')



if __name__ == '__main__':

    # FIXME: Make command line arugment to replace rtl_app with mock
    #rtl_app = mock_rtl_app
   # logging.basicConfig(level=logging.debug)
    tornado.testing.main()

