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

import pprint
import tornado

from base import RedhawkTests
from defaults import Default
from model.redhawk import Redhawk


class ApplicationTests(RedhawkTests):
    
    def setUp(self):
        super(ApplicationTests, self).setUp();
        self.redhawk = Redhawk()

    def tearDown(self):
        # kill SigTest waveforms
        self._clean_applications(['SigTest'])
        super(ApplicationTests, self).tearDown();
    

    @tornado.testing.gen_test
    def test_launch_release(self):
        url, applications = yield self._get_applications()
        json, resp = yield self._async_json_request(url+'/applications', 200)

        self.assertTrue('waveforms' in json)
        self.assertTrue(Default.WAVEFORM in [x['name'] for x in json['waveforms']])

        wf_id = yield self._launch(Default.WAVEFORM)
        yield self._release(wf_id)

    @tornado.testing.gen_test
    def test_list(self):
        url, applications = yield self._get_applications()
        json, resp = yield self._async_json_request(url+'/applications', 200)

        self.assertTrue('waveforms' in json)
        self.assertTrue(isinstance(json['waveforms'], list))
        for app in json['waveforms']:
            self.assertTrue('sad' in app)
            self.assertTrue('name' in app)

        self.assertIdList(json, 'applications')
        self.assertEquals(applications, json['applications'])

    @tornado.testing.gen_test
    def test_info(self):
        wf_id = yield self._launch(Default.WAVEFORM)

        url = '/domains/%s/applications/%s' % (Default.DOMAIN_NAME, wf_id)
        json, resp = yield self._async_json_request(url, 200)

        self.assertList(json, 'ports')
        self.assertList(json, 'components')
        self.assertTrue('name' in json)
        self.assertAttr(json, 'id', wf_id)

        self.assertList(json, 'properties')
        # TODO: self.assertProperties(json['properties'])
        
    @tornado.testing.gen_test
    def test_detect_new_applications(self):
        yield [ self.detect_new_applications() for x in xrange(10) ]        
        
    @tornado.gen.coroutine
    def detect_new_applications(self):
        'Test when an application started'
        url, apps = yield self._get_applications()        
        
        # start a new app
        id = yield self.redhawk.launch_application(Default.DOMAIN_NAME, Default.WAVEFORM)
        
#         yield self._async_sleep(.5)
        
        # ensure it exists in the application
        url, apps2 = yield self._get_applications()
        if id not in (a['id'] for a in apps2):
            self.fail("Expecting %s in domain %s" % (id, Default.DOMAIN_NAME))
#         if (len(apps)+1 != len(apps2)):
#             self.fail("Expecting one additional app %s %s" % (apps, apps2))
            
        # now release it
        yield self.redhawk.release_application(Default.DOMAIN_NAME, id)

        # ensure it is missing in the application list
        url, apps3 = yield self._get_applications()
        if id in (a['id'] for a in apps3):
            self.fail("Not Expecting %s in domain %s" % (id, Default.DOMAIN_NAME))
#         if (len(apps) != len(apps3)):
#             self.fail("Expecting same number of apps %s %s" % (apps, apps3))
        
        
    @tornado.testing.gen_test
    def test_not_found(self):
        url = '/domains/%s/applications/adskfhsdhfasdhjfhsd' %Default.DOMAIN_NAME
        json, resp = yield self._async_json_request(url, 404)

        self._resource_not_found(json)
    
