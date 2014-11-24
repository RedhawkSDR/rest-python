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
Tornado tests for the /domain/{NAME}/applications portion of the REST API
"""

from base import JsonTests
from defaults import Default


class ApplicationTests(JsonTests):
    def _get_applications(self):
        url = '/domains/'+Default.DOMAIN_NAME
        json, resp = self._json_request(url, 200)

        self.assertTrue('applications' in json)

        return url, json['applications']

    def _launch(self, name):
        json, resp = self._json_request(
            '/domains/'+Default.DOMAIN_NAME+'/applications',
            200,
            'POST',
            {'name': name}
        )
        self.assertTrue('launched' in json)
        self.assertTrue('applications' in json)
        self.assertTrue(json['launched'] in [x['id'] for x in json['applications']])

        return json['launched']

    def _release(self, wf_id):
        json, resp = self._json_request(
            '/domains/'+Default.DOMAIN_NAME+'/applications/'+wf_id,
            200,
            'DELETE'
        )

        self.assertAttr(json, 'released', wf_id)

        self.assertTrue('applications' in json)
        self.assertFalse(json['released'] in json['applications'])

    def test_launch_release(self):
        url, applications = self._get_applications()
        json, resp = self._json_request(url+'/applications', 200)

        self.assertTrue('waveforms' in json)
        self.assertTrue(Default.WAVEFORM in [x['name'] for x in json['waveforms']])

        wf_id = self._launch(Default.WAVEFORM)
        self._release(wf_id)

    def test_list(self):
        url, applications = self._get_applications()
        json, resp = self._json_request(url+'/applications', 200)

        self.assertTrue('waveforms' in json)
        self.assertTrue(isinstance(json['waveforms'], list))
        for app in json['waveforms']:
            self.assertTrue('sad' in app)
            self.assertTrue('name' in app)

        self.assertIdList(json, 'applications')
        self.assertEquals(applications, json['applications'])

    def test_info(self):
        wf_id = self._launch(Default.WAVEFORM)

        url = '/domains/%s/applications/%s' % (Default.DOMAIN_NAME, wf_id)
        json, resp = self._json_request(url, 200)

        self.assertList(json, 'ports')
        self.assertList(json, 'components')
        self.assertTrue('name' in json)
        self.assertAttr(json, 'id', wf_id)

        self.assertList(json, 'properties')
        # TODO: self.assertProperties(json['properties'])

    def test_not_found(self):
        url = '/domains/%s/applications/adskfhsdhfasdhjfhsd' %Default.DOMAIN_NAME
        json, resp = self._json_request(url, 404)

        self._resource_not_found(json)
