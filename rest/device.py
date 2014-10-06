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
Rest handlers for Devices

Classes:
Device -- Get info of a specific device
"""

from tornado import gen

from handler import JsonHandler
from helper import PropertyHelper, PortHelper
from tornado import web


class Devices(JsonHandler, PropertyHelper, PortHelper):
    @gen.coroutine
    def get(self, domain_name, dev_mgr_id, dev_id=None):
        if dev_id:
            dev = yield self.redhawk.get_device(domain_name, dev_mgr_id, dev_id)

            info = {
                'name': dev.name,
                'id': dev._id,
                'started': dev._get_started(),
                'ports': self.format_ports(dev.ports),
                'properties': self.format_properties(dev._properties)
            }
        else:
            devices = yield self.redhawk.get_device_list(domain_name, dev_mgr_id)
            info = {'devices': devices}

        self._render_json(info)


class DeviceProperties(web.RequestHandler):

    def get(self, *args):
        self.set_status(500)
        self.write(dict(status='Device Properties handler not implemented'))
