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
Tornado tests for the /domain/{NAME}/waveforms portion of the REST API
"""
__author__ = 'rpcanno'

from base import JsonTests
from defaults import Default


class WaveformTests(JsonTests):
    def _get_waveforms(self):
        url = '/domains/'+Default.DOMAIN_NAME
        json, resp = self._json_request(url, 200)

        self.assertTrue('waveforms' in json)

        return url, json['waveforms']

    def _launch(self, name):
        json, resp = self._json_request(
            '/domains/'+Default.DOMAIN_NAME+'/waveforms',
            200,
            'POST',
            {'name': name}
        )
        self.assertTrue('launched' in json)
        self.assertTrue('waveforms' in json)
        self.assertTrue(json['launched'] in [x['id'] for x in json['waveforms']])

        return json['launched']

    def _release(self, wf_id):
        json, resp = self._json_request(
            '/domains/'+Default.DOMAIN_NAME+'/waveforms/'+wf_id,
            200,
            'DELETE'
        )

        self.assertAttr(json, 'released', wf_id)

        self.assertTrue('waveforms' in json)
        self.assertFalse(json['released'] in json['waveforms'])

    def test_launch_release(self):
        url, waveforms = self._get_waveforms()
        json, resp = self._json_request(url+'/waveforms', 200)

        self.assertTrue('available' in json)
        self.assertTrue(Default.WAVEFORM in [x['name'] for x in json['available']])

        wf_id = self._launch(Default.WAVEFORM)
        self._release(wf_id)

    def test_list(self):
        url, waveforms = self._get_waveforms()
        json, resp = self._json_request(url+'/waveforms', 200)

        self.assertTrue('available' in json)
        self.assertTrue(isinstance(json['available'], list))
        for app in json['available']:
            self.assertTrue('sad' in app)
            self.assertTrue('name' in app)

        self.assertIdList(json, 'waveforms')
        self.assertEquals(waveforms, json['waveforms'])

    def test_info(self):
        wf_id = self._launch(Default.WAVEFORM)

        url = '/domains/%s/waveforms/%s' % (Default.DOMAIN_NAME, wf_id)
        json, resp = self._json_request(url, 200)

        self.assertList(json, 'ports')
        self.assertList(json, 'components')
        self.assertTrue('name' in json)
        self.assertAttr(json, 'id', wf_id)

        self.assertList(json, 'properties')
        # TODO: self.assertProperties(json['properties'])

    def test_not_found(self):
        url = '/domains/%s/waveforms/adskfhsdhfasdhjfhsd' %Default.DOMAIN_NAME
        json, resp = self._json_request(url, 404)

        self._resource_not_found(json)
