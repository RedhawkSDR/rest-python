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
Tornado tests for the /domain portion of the REST API
"""
__author__ = 'rpcanno'

import logging
import json
import socket
import tornado
from tornado.httpclient import AsyncHTTPClient

from base import JsonTests
from defaults import Default
from model import domain


class DomainTests(JsonTests):
    def setUp(self):
        self.redhawk_remote_bug = domain.redhawk_remote_bug
        super(DomainTests, self).setUp()

    def tearDown(self):
        super(DomainTests, self).tearDown()
        domain.redhawk_remote_bug = self.redhawk_remote_bug


    def test_list(self):
        body, resp = self._json_request("/domains", 200)

        self.assertTrue('domains' in body)
        self.assertTrue(isinstance(body['domains'], list))
        if len(body['domains']) == 0:
            self.fail("Invalid test.  Expected at least one REDHAWK Domain returned, received 0")
        for d in body['domains']:
            if ':' in d:
                self.fail("Not expecting location in domain (no ':').  Received '%s'" % d)

    def test_list_location(self):
        hosts = ['localhost', socket.gethostname()]
        for h in hosts:
            body, resp = self._json_request("/domains/%s:" % h, 200)
            self.assertTrue('domains' in body)
            self.assertTrue(isinstance(body['domains'], list))
            if len(body['domains']) == 0:
                self.fail("Invalid test.  Expected at least one REDHAWK Domain returned, received 0")
            for d in body['domains']:
                d = str(d)
                if not d.startswith("%s:" % h):
                    self.fail("Returned domain missing location.  Expected %s:XXX received %s" % (h, d))

    def test_list_bad_location(self):
        body, resp = self._json_request("/domains/localhost_bad:", 404)
        self.assertAttr(body, 'error', 'ResourceNotFound')
        self.assertAttr(body, 'message', "Unable to connect with NameService on host 'localhost_bad'")

    def test_list_bad_redhawk_version(self):
        domain.redhawk_remote_bug = True
        body, resp = self._json_request("/domains/localhost:", 200)
        body, resp = self._json_request("/domains/", 200)
        body, resp = self._json_request("/domains/:", 200)
        body, resp = self._json_request("/domains/localhost_awful:", 500)
        self.assertAttr(body, 'error', 'Exception')
        self.assertAttr(body, 'message', "Remote domain connectivity is unavailable in Redhawk <= 1.10.2")


    def test_bad_redhawk_version(self):
        domain.redhawk_remote_bug = True
        body, resp = self._json_request("/domains/" + Default.DOMAIN_NAME, 200)
        body, resp = self._json_request("/domains/:" + Default.DOMAIN_NAME, 200)
        body, resp = self._json_request("/domains/localhost:" + Default.DOMAIN_NAME, 200)
        body, resp = self._json_request("/domains/foobar:" + Default.DOMAIN_NAME, 500)
        self.assertAttr(body, 'error', 'Exception')
        self.assertAttr(body, 'message', "Remote domain connectivity is unavailable in Redhawk <= 1.10.2")

    def test_info(self):
        body, resp = self._json_request("/domains/" + Default.DOMAIN_NAME, 200)

        self.assertTrue('name' in body)
        self.assertEquals(body['name'], Default.DOMAIN_NAME)

        self.assertTrue('applications' in body)
        self.assertTrue('deviceManagers' in body)
        self.assertTrue('properties' in body)
        self.assertTrue('id' in body)

    def test_location_good(self):
        body, resp = self._json_request("/domains/localhost:" + Default.DOMAIN_NAME, 200)

        self.assertTrue('name' in body)
        self.assertEquals(body['name'], Default.DOMAIN_NAME)

        self.assertTrue('applications' in body)
        self.assertTrue('deviceManagers' in body)
        self.assertTrue('properties' in body)
        self.assertTrue('id' in body)

    def test_location_bad(self):
        domainname = 'localh:%s' % Default.DOMAIN_NAME
        body, resp = self._json_request("/domains/%s" % domainname, 404)
        self.assertAttr(body, 'error', 'ResourceNotFound')
        self.assertAttr(body, 'message', "Unable to find domain '%s'" % domainname)

    def test_domain_not_found(self):
        body, resp = self._json_request("/domains/ldskfadjklfsdjkfasdl", 404)
        print body
        self._resource_not_found(body)

    @tornado.testing.gen_test
    def test_domain_get_instance(self):
        response = yield AsyncHTTPClient(self.io_loop).fetch(
            self.get_url("%s/domains/%s" % (Default.REST_BASE, Default.DOMAIN_NAME)))
        self.assertEquals(200, response.code)
        data = json.loads(response.body)

        for name in ('applications', 'properties', 'deviceManagers', 'id', 'name'):
            self.assertTrue(name in data, "json missing %s" % name)

    def test_domain_get_failure(self):
        # callback must be used to get response to non-200 HTTPResponse
        AsyncHTTPClient(self.io_loop).fetch(self.get_url("%s/domains/%s" % (Default.REST_BASE, 'REDHAWK_DEV_FOO')),
                                            self.stop)
        response = self.wait()

        self.assertEquals(404, response.code)
        pdata = json.loads(response.body)
        logging.debug("Found port data %s", pdata)
        # FIXME: Check error response




