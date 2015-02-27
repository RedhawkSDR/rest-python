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
Tornado tests for the /domain portion of the REST API
"""
__author__ = 'depew'

from base import JsonTests
from defaults import Default
import types


class SysinfoTests(JsonTests):

    def test_sysinfo(self):
        body, resp = self._json_request("/sysinfo", 200)
        self.assertHasAttr(body, 'supportsRemoteLocations')
        self.assertHasAttr(body, 'redhawk.version')
        self.assertHasAttr(body, 'rhweb.version')
        if not isinstance(body['supportsRemoteLocations'], types.BooleanType):
            self.fail("Expected properties.remoteLocations to be a boolean, got %s" % type(p['remoteLocations']))

