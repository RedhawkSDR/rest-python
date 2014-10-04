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
"""
Base TestCase class with convenience functions
"""
__author__ = 'rpcanno'

from tornado.testing import AsyncHTTPTestCase
from tornado.httpclient import AsyncHTTPClient, HTTPRequest
from pyrest import Application

import json

from defaults import Default

class JsonAssertions(object):

    RESPONSE_CODES_2XX = (200, 201, 202, 203, 204, 205, 206)
    RESPONSE_CODES_3XX = (300, 301, 302, 303, 304, 305, 306, 307)
    RESPONSE_CODES_4XX = (400, 401, 402, 403, 404, 405, 406, 407, 408, 409, 410, 411, 412, 413, 414, 415, 416, 417)
    RESPONSE_CODES_5XX = (500, 501, 502, 503, 504, 505)

    def assertResponse(self, response, codes=RESPONSE_CODES_2XX):
        '''
            Asserts a valid response

            Codes can be a set of codes (e.g. 2XX) or a single code
        '''
        try:
            if response.code not in codes:
                self.fail("Response code %d not one of %s", response.code, codes)
        except TypeError:
            if response.code != codes:
                self.fail("Response code %d is not %s", response.code, codes)
        

    def assertJson(self, response):
        try:
            return json.loads(response.body)
        except ValueError:
            self.fail("Unable to parse json input '%s'" % response.body)
        
    def assertJsonResponse(self, response, codes=RESPONSE_CODES_2XX):
        data = assertJson(response)
        assertResponse(response, codes)
        return data

    def assertAttr(self, data, name, value):
        self.assertTrue(name in data)
        self.assertEquals(data[name], value)

    def assertList(self, data, name):
        self.assertTrue(name in data)
        self.assertTrue(isinstance(data[name], list))

    def assertIdList(self, data, name):
        self.assertList(data, name)
        for item in data[name]:
            self.assertTrue('id' in item)
            self.assertTrue('name' in item)

    def assertProperties(self, data):
        self.assertTrue(isinstance(data, list))
        for prop in data:
            self.assertList(prop, 'kinds')
            self.assertTrue('name' in prop)
            self.assertTrue('value' in prop)
            self.assertTrue('scaType' in prop)
            self.assertTrue('mode' in prop)
            self.assertTrue('type' in prop)
            self.assertTrue('id' in prop)



class JsonTests(AsyncHTTPTestCase, JsonAssertions):
    def get_app(self):
        return Application()

    def _json_request(self, url, code, method='GET', json_data=None):
        body = None
        if json_data:
            body = json.dumps(json_data)

        AsyncHTTPClient(self.io_loop).fetch(self.get_url(Default.REST_BASE+url), self.stop, method=method, body=body)
        response = self.wait()

        self.assertEquals(code, response.code)

        data = {}
        if response.body:
            data = json.loads(response.body)

        return data, response

    def _resource_not_found(self, body):
        self.assertTrue('error' in body)
        self.assertEquals(body['error'], Default.RESOURCE_NOT_FOUND_ERR)
        self.assertTrue('message' in body)
        self.assertTrue(Default.RESOURCE_NOT_FOUND_MSG_REGEX.match(body['message']))
