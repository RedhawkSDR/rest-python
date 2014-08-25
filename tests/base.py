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

        return json.loads(response.body), response

    def _resource_not_found(self, body):
        self.assertTrue('error' in body)
        self.assertEquals(body['error'], Default.RESOURCE_NOT_FOUND_ERR)
        self.assertTrue('message' in body)
        self.assertTrue(Default.RESOURCE_NOT_FOUND_MSG_REGEX.match(body['message']))