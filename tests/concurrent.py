"""
Tornado tests for the /domain/{NAME}/applications/{ID}/components portion of the REST API

"""
# tornado imports
import random
import time

import tornado
import tornado.testing
from tornado.testing import AsyncHTTPTestCase, LogTrapTestCase
from tornado.httpclient import AsyncHTTPClient, HTTPRequest
from tornado import websocket

from pyrest import Application
from base import JsonTests
from defaults import Default
import pprint


class ConcurrencyTests(JsonTests):

    def setUp(self):
        super(ConcurrencyTests, self).setUp()
        json, resp = self._json_request(
            '/domains/%s/applications' % Default.DOMAIN_NAME,
            200,
            'POST',
            {'name': Default.WAVEFORM}
        )
        self.assertTrue('launched' in json)
        self.base_url = '/domains/%s/applications/%s' % (Default.DOMAIN_NAME, json['launched'])

        json, resp = self._json_request(self.base_url, 200)
        self.assertList(json, 'components')
        self.assertTrue(json['components'])

        self.components = json['components']

    def tearDown(self):
        self._json_request(
            self.base_url,
            200,
            'DELETE'
        )
        super(ConcurrencyTests, self).tearDown()

    def _get_comps(self):
        pass

    @tornado.testing.gen_test(timeout=600)
    def test_list(self):
        http_client = AsyncHTTPClient()
        url = self.get_url(Default.REST_BASE + self.base_url + '/components')
        
        # Do five tests, get the average time
        times = []
        avgs = {}
        
        for x in xrange(5):
            result1 = yield http_client.fetch(url)
            self.assertEquals(200, result1.code)        
            times.append(result1.request_time)
            print result1.request_time
        
        avg = sum(times) / len(times)
        avgs[1] = avg
        print "AVG: %f" % avg
        
        clients = 10
        results = yield [ http_client.fetch(url) for x in xrange(clients) ]
        avg1 = sum((r.request_time for r in results)) / len(results)
        avgs[clients] = avg1
        print avg1
        
        clients = 100
        results = yield [ http_client.fetch(url) for x in xrange(clients) ]
        avg2 = sum((r.request_time for r in results)) / len(results)        
        avgs[clients] = avg2
        print avg2

        clients = 200
        results = yield [ http_client.fetch(url) for x in xrange(clients) ]
        avg3 = sum((r.request_time for r in results)) / len(results)
        avgs[clients] = avg3
        
        print avg3
        
        print "Averages ", avgs
        
        

    @tornado.gen.coroutine
    def set_properties2(self):
        '''
            Updates the frequency to frequency + 10.  Returns the cumulative time it took
        '''
        yield tornado.gen.Task(self.io_loop.add_timeout, time.time() + random.random())
        
        comp_id = self.components[0]['id']
        properties, resp1 = yield self._async_get_properties(comp_id)
        print properties
        resp2 = yield self._async_set_property(comp_id, frequency=properties['frequency'] + 10)
        properties, resp3 = yield self._async_get_properties(comp_id)
        print properties
        
#         pprint.pprint(dict(resp1=resp1, resp2=resp2, resp3=resp3))
        raise tornado.gen.Return(resp1.request_time + resp2.request_time + resp3.request_time)
        
        
    @tornado.testing.gen_test(timeout=600)
    def test_set_properties(self):
        
        values = yield [ self.set_properties2() for x in xrange(1) ]
        print values
        print "Average: %f" % (sum(values) / len(values))

        values = yield [ self.set_properties2() for x in xrange(100) ]
        print values
        print "Average: %f" % (sum(values) / len(values))
#         comp_id = self.components[0]['id']
#         json, resp = yield self._async_json_request('%s/components/%s' % (self.base_url, comp_id), 200)
#         properties = json['properties']
# 
#         json, resp = yield self._async_json_request("%s/components/%s/properties" % (self.base_url, comp_id), 200)
#         self.assertList(json, 'properties')
#         self.assertEquals(properties, json['properties'])
# 
#         prop = None
#         for p in json['properties']:
#             if p['id'] == Default.COMPONENT_PROPERTY:
#                 prop = p
#         self.assertEquals(prop['value'], Default.COMPONENT_PROPERTY_VALUE)
# 
#         # Configure
#         json, resp = yield self._async_json_request(
#             "%s/components/%s/properties" % (self.base_url, comp_id),
#             200,
#             'PUT',
#             {'properties': [
#                 {'id': Default.COMPONENT_PROPERTY, 'value': Default.COMPONENT_PROPERTY_CHANGE}
#             ]}
#         )
# 
#         json, resp = yield self._async_json_request("%s/components/%s/properties" % (self.base_url, comp_id), 200)
#         prop = None
#         for p in json['properties']:
#             if p['id'] == Default.COMPONENT_PROPERTY:
#                 prop = p
#         self.assertEquals(prop['value'], Default.COMPONENT_PROPERTY_CHANGE)
#         http_client = AsyncHTTPClient()
#         url = self.get_url(Default.REST_BASE + self.base_url + '/components')