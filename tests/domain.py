"""
Tornado tests for the /domain portion of the REST API
"""
__author__ = 'rpcanno'

from base import JsonTests
from defaults import Default


class DomainTests(JsonTests):

    def test_list(self):
        body, resp = self._json_request("/domains", 200)

        self.assertTrue('domains' in body)
        self.assertTrue(isinstance(body['domains'], list))

    def test_info(self):
        body, resp = self._json_request("/domains/"+Default.DOMAIN_NAME, 200)

        self.assertTrue('name' in body)
        self.assertEquals(body['name'], Default.DOMAIN_NAME)

        self.assertTrue('waveforms' in body)
        self.assertTrue('deviceManagers' in body)
        self.assertTrue('properties' in body)
        self.assertTrue('id' in body)

    def test_info_not_found(self):
        body, resp = self._json_request("/domains/ldskfadjklfsdjkfasdl", 404)
        print body
        self._resource_not_found(body)