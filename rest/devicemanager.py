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
Rest handlers for Device Managers

Classes:
DeviceManagers -- Get info of all or a specific device manager
"""

from handler import JsonHandler
from helper import PropertyHelper, PortHelper
from model.domain import Domain


class DeviceManagers(JsonHandler, PropertyHelper, PortHelper):
    def get(self, domain_name, dev_mgr_id=None):
        dom = Domain(str(domain_name))

        if dev_mgr_id:
            dev_mgr = dom.find_device_manager(dev_mgr_id)

            prop_dict = self.format_properties(dev_mgr.query([]))  # TODO: self._propSet(devMgr._properties)
            info = {
                'name': dev_mgr.name,
                'id': dev_mgr.id,
                'properties': prop_dict,
                'devices': dom.devices(dev_mgr_id),
                'services': dom.services(dev_mgr_id)
            }
        else:
            info = {'deviceManagers': dom.device_managers()}

        self._render_json(info)
