"""
Tornado tests for the /domain/{NAME}/waveforms/{ID}/components portion of the REST API
"""
__author__ = 'rpcanno'

from base import JsonTests
from defaults import Default


class ComponentTests(JsonTests):
    def _setUp(self):
        json, resp = self._json_request(
            '/domains/%s/waveforms' % Default.DOMAIN_NAME,
            200,
            'POST',
            {'name': Default.WAVEFORM}
        )
        self.assertTrue('launched' in json)
        self.base_url = '/domains/%s/waveforms/%s' % (Default.DOMAIN_NAME, json['launched'])

        json, resp = self._json_request(self.base_url, 200)
        self.assertList(json, 'components')
        self.assertTrue(json['components'])

        self.components = json['components']

    def _tearDown(self):
        self._json_request(
            self.base_url,
            200,
            'DELETE'
        )

    def _get_comps(self):
        pass

    def test_list(self):
        self._setUp()

        json, resp = self._json_request(self.base_url + '/components', 200)

        self.assertIdList(json, 'components')
        self.assertEquals(self.components, json['components'])

        self._tearDown()

    def test_info(self):
        self._setUp()

        comp_id = self.components[0]['id']
        json, resp = self._json_request('%s/components/%s' % (self.base_url, comp_id), 200)

        self.assertList(json, 'ports')

        self.assertAttr(json, 'id', comp_id)
        self.assertAttr(json, 'name', Default.COMPONENT)

        self.assertList(json, 'properties')
        self.assertProperties(json['properties'])

        self._tearDown()

    def test_not_found(self):
        self._setUp()

        json, resp = self._json_request('%s/components/ggsdfgfdg' % self.base_url, 404)

        self._resource_not_found(json)

        self._tearDown()

    def test_properties(self):
        self._setUp()

        comp_id = self.components[0]['id']
        json, resp = self._json_request('%s/components/%s' % (self.base_url, comp_id), 200)
        properties = json['properties']

        json, resp = self._json_request("%s/components/%s/properties" % (self.base_url, comp_id), 200)

        self.assertList(json, 'properties')
        self.assertEquals(properties, json['properties'])

        prop = None
        for p in json['properties']:
            if p['id'] == Default.COMPONENT_PROPERTY:
                prop = p
        self.assertEquals(prop['value'], Default.COMPONENT_PROPERTY_VALUE)

        # TODO: Configure
        new_props = {'properties': [
            {'id': Default.COMPONENT_PROPERTY, 'value': Default.COMPONENT_PROPERTY_CHANGE}
        ]}
        json, resp = self._json_request(
            "%s/components/%s/properties" % (self.base_url, comp_id),
            200,
            'PUT',
            {'properties': [
                {'id': Default.COMPONENT_PROPERTY, 'value': Default.COMPONENT_PROPERTY_CHANGE}
            ]}
        )

        json, resp = self._json_request("%s/components/%s/properties" % (self.base_url, comp_id), 200)
        prop = None
        for p in json['properties']:
            if p['id'] == Default.COMPONENT_PROPERTY:
                prop = p
        self.assertEquals(prop['value'], Default.COMPONENT_PROPERTY_CHANGE)

        self._tearDown()