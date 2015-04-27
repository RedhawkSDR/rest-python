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

# tornado imports
import tornado
import tornado.testing
from tornado.testing import AsyncHTTPTestCase, LogTrapTestCase
from tornado.httpclient import AsyncHTTPClient, HTTPRequest

from base import JsonAssertions, RedhawkTests
# application imports
from pyrest import Application
from defaults import Default

# all method returning suite is required by tornado.testing.main()
def all():
   return unittest.TestLoader().loadTestsFromModule(__import__(__name__))


class PortTests(RedhawkTests, AsyncHTTPTestCase, LogTrapTestCase, JsonAssertions):

    # def setUp(self):
    #     super(RESTfulTest, self).setUp()
    #     rtl_app.RTLApp('REDHAWK_DEV').stop_survey()


    def get_app(self):
        return Application(debug=True, _ioloop=self.io_loop)

    @tornado.testing.gen_test
    def test_domain_get_instance(self):        
        response = yield AsyncHTTPClient(self.io_loop).fetch(self.get_url("%s/domains/%s" % (Default.REST_BASE, Default.DOMAIN_NAME)))
        self.assertEquals(200, response.code)
        data = json.loads(response.body)

        for name in ('applications', 'properties', 'deviceManagers', 'id', 'name'):
            self.assertTrue(name in data, "json missing %s" % name)


    def test_domain_get_failure(self):
        # callback must be used to get response to non-200 HTTPResponse
        AsyncHTTPClient(self.io_loop).fetch(self.get_url("%s/domains/%s" % (Default.REST_BASE, 'REDHAWK_DEV_FOO')), self.stop)
        response = self.wait()

        self.assertEquals(404, response.code)
        pdata = json.loads(response.body)
        logging.debug("Found port data %s", pdata)
        # FIXME: Check error response


    @tornado.testing.gen_test
    def test_application_port_get(self):
        self._async_clean_applications()
        # get a list of waveforms
        id = yield self._launch('SigTest')
        self._async_sleep(1)
        portr = yield AsyncHTTPClient(self.io_loop).fetch(self.get_url("%s/domains/%s/applications/%s/ports" % (Default.REST_BASE, Default.DOMAIN_NAME, id)))
        self.assertEquals(200, portr.code)
        pdata = json.loads(portr.body)
        # imp
        # orting here so that only this test case fails if it doesn't exist
        self.validate_json(pdata, "ports.schema.json")

        # FIXME: Test against a applications with ports
        # logging.debug("Found port data %s", pdata)
        # self.fail("BAD")
