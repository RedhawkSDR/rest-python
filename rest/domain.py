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
Rest handlers for Domains

Classes:
DomainInfo -- Get info of all or a specific domain
DomainProperties -- Manipulate the properties of a domain
"""

from tornado import gen

from handler import JsonHandler
from helper import PropertyHelper


class DomainInfo(JsonHandler, PropertyHelper):
    @gen.coroutine
    def get(self, domain_name=None):
        if domain_name:
            dom_info = yield self.redhawk.get_domain_info(domain_name)
            properties = yield self.redhawk.get_domain_properties(domain_name)
            apps = yield self.redhawk.get_application_list(domain_name)
            device_managers = yield self.redhawk.get_device_manager_list(domain_name)

            info = {
                'id': dom_info._get_identifier(),
                'name': dom_info.name,
                'properties': self.format_properties(properties),
                'applications': apps,
                'deviceManagers': device_managers
            }

        else:
            domains = yield self.redhawk.get_domain_list()
            info = {'domains': domains}
        self._render_json(info)


class DomainProperties(JsonHandler, PropertyHelper):
    @gen.coroutine
    def get(self, domain_name, prop_name=None):
        properties = yield self.redhawk.get_domain_properties(domain_name)
        info = self.format_properties(properties)

        if prop_name:
            value = None
            for item in info:
                if item['name'] == prop_name:
                    value = item

            if value:
                self._render_json(value)
            else:
                self._render_json({'error': "Could not find property"})
        else:
            self._render_json({'properties': info})
