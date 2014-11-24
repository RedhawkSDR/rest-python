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
Tornado tests for the /domain/{NAME}/applications/{ID}/components portion of the REST API
"""

from pyrest import Application
from base import JsonTests
from defaults import Default


class ComponentTests(JsonTests):

    def setUp(self):
        super(ComponentTests, self).setUp()
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
        super(ComponentTests, self).tearDown()

    def _get_comps(self):
        pass

    def test_list(self):
        json, resp = self._json_request(self.base_url + '/components', 200)

        self.assertIdList(json, 'components')
        self.assertEquals(self.components, json['components'])

    def test_info(self):
        comp_id = self.components[0]['id']
        json, resp = self._json_request('%s/components/%s' % (self.base_url, comp_id), 200)

        self.assertList(json, 'ports')

        self.assertAttr(json, 'id', comp_id)
        self.assertAttr(json, 'name', Default.COMPONENT)

        self.assertList(json, 'properties')
        self.assertProperties(json['properties'])

    def test_not_found(self):
        json, resp = self._json_request('%s/components/ggsdfgfdg' % self.base_url, 404)

        self._resource_not_found(json)

    def test_properties(self):
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

        # Configure
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
