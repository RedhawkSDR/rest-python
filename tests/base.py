"""
Base TestCase class with convenience functions
"""
__author__ = 'rpcanno'

from tornado.testing import AsyncHTTPTestCase
from pyrest import Application

import json

from defaults import Default


class JsonTests(AsyncHTTPTestCase):
    def get_app(self):
        return Application()

    def _json_request(self, url, code, method='GET', json_data=None):
        body = None
        if json_data:
            body = json.dumps(json_data)

        self.http_client.fetch(self.get_url(Default.REST_BASE+url), self.stop, method=method, body=body)
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