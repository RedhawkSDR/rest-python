"""
Tornado tests for the /domain/{NAME}/deviceManagers/{ID}/devices portion of the REST API
"""

__author__ = 'rpcanno'

from base import JsonTests

from defaults import Default


class DeviceTests(JsonTests):
    def _get_dev_list(self):
        """
        Get a list of devices from one level up (ie the control)
        """
        json, resp = self._json_request("/domains/"+Default.DOMAIN_NAME, 200)

        self.assertTrue('deviceManagers' in json)
        self.assertTrue(isinstance(json['deviceManagers'], list))
        self.assertTrue(len(json['deviceManagers']) > 0)

        mgr = json['deviceManagers'][0]
        self.assertTrue('id' in mgr)

        url = "/domains/"+Default.DOMAIN_NAME+"/deviceManagers/"+mgr['id']
        json, resp = self._json_request(url, 200)

        self.assertTrue('devices' in json)
        self.assertTrue(isinstance(json['devices'], list))

        return url, json['devices']

    def test_list(self):
        base_url, devices = self._get_dev_list()

        json, resp = self._json_request(base_url+'/devices', 200)

        self.assertTrue('devices' in json)
        self.assertTrue(isinstance(json['devices'], list))

        for dev in json['devices']:
            self.assertTrue('id' in dev)
            self.assertTrue('name' in dev)

        self.assertEquals(devices, json['devices'])

    def test_info(self):
        url, devices = self._get_dev_list()

        self.assertTrue(len(devices) > 0)

        dev = devices[0]
        self.assertTrue('id' in dev)

        json, resp = self._json_request(url+"/devices/"+dev['id'], 200)

        self.assertTrue('name' in json)
        self.assertEquals(json['name'], dev['name'])
        self.assertTrue('id' in json)
        self.assertEquals(json['id'], dev['id'])

        self.assertTrue('started' in json)
        self.assertTrue('properties' in json)
        self.assertTrue('ports' in json)

    def test_info_not_found(self):
        url, devices = self._get_dev_list()
        json, resp = self._json_request(url+"/devices/sdkafsdfhklasdfhkajl", 404)

        self._resource_not_found(json)