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

from base import JsonTests
from defaults import Default
import socket


class DomainTests(JsonTests):

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
        hosts = [ 'localhost', socket.gethostname() ]
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


    def test_info(self):
        body, resp = self._json_request("/domains/"+Default.DOMAIN_NAME, 200)

        self.assertTrue('name' in body)
        self.assertEquals(body['name'], Default.DOMAIN_NAME)

        self.assertTrue('applications' in body)
        self.assertTrue('deviceManagers' in body)
        self.assertTrue('properties' in body)
        self.assertTrue('id' in body)

    def test_location_good(self):
        body, resp = self._json_request("/domains/localhost:"+Default.DOMAIN_NAME, 200)

        self.assertTrue('name' in body)
        self.assertEquals(body['name'], Default.DOMAIN_NAME)

        self.assertTrue('applications' in body)
        self.assertTrue('deviceManagers' in body)
        self.assertTrue('properties' in body)
        self.assertTrue('id' in body)

    def test_location_bad(self):
        domainname='localh:%s' % Default.DOMAIN_NAME
        body, resp = self._json_request("/domains/%s" % domainname, 404)
        self.assertAttr(body, 'error', 'ResourceNotFound')
        self.assertAttr(body, 'message', "Unable to find domain '%s'" % domainname)

    def test_domain_not_found(self):
        body, resp = self._json_request("/domains/ldskfadjklfsdjkfasdl", 404)
        print body
        self._resource_not_found(body)


