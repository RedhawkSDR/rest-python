"""
Tornado tests for the /domain/{NAME}/deviceManagers portion of the REST API
"""
__author__ = 'rpcanno'

from base import JsonTests

from defaults import Default


class DeviceManagerTests(JsonTests):
    def _get_dev_mgr_list(self):
        """
        Get a list of device managers from one level up (ie the control)
        """
        body, resp = self._json_request("/domains/"+Default.DOMAIN_NAME, 200)

        self.assertTrue('deviceManagers' in body)
        self.assertTrue(isinstance(body['deviceManagers'], list))

        return body['deviceManagers']

    def test_list(self):
        dev_managers = self._get_dev_mgr_list()

        body, resp = self._json_request("/domains/"+Default.DOMAIN_NAME+"/deviceManagers", 200)

        self.assertTrue('deviceManagers' in body)
        self.assertTrue(isinstance(body['deviceManagers'], list))

        for mgr in body['deviceManagers']:
            self.assertTrue('id' in mgr)
            self.assertTrue('name' in mgr)
            
        self.assertEquals(dev_managers, body['deviceManagers'])

    def test_info(self):
        dev_managers = self._get_dev_mgr_list()

        self.assertTrue(len(dev_managers) > 0)

        mgr = dev_managers[0]
        self.assertTrue('id' in mgr)

        body, resp = self._json_request("/domains/"+Default.DOMAIN_NAME+"/deviceManagers/"+mgr['id'], 200)

        self.assertTrue('name' in body)
        self.assertEquals(body['name'], mgr['name'])
        self.assertTrue('id' in body)
        self.assertEquals(body['id'], mgr['id'])

        self.assertTrue('services' in body)
        self.assertTrue('properties' in body)
        self.assertTrue('devices' in body)

    def test_info_not_found(self):
        global DOMAIN_NAME
        body, resp = self._json_request("/domains/"+Default.DOMAIN_NAME+"/deviceManagers/sdkafsdfhklasdfhkajl", 404)

        self._resource_not_found(body)