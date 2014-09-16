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

from base import JsonAssertions
# application imports
from pyrest import Application

# all method returning suite is required by tornado.testing.main()
def all():
   return unittest.TestLoader().loadTestsFromModule(__import__(__name__))


class PortTests(AsyncHTTPTestCase, LogTrapTestCase, JsonAssertions):

    # def setUp(self):
    #     super(RESTfulTest, self).setUp()
    #     rtl_app.RTLApp('REDHAWK_DEV').stop_survey()


    def get_app(self):
        return Application(debug=True, _ioloop=self.io_loop)


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
