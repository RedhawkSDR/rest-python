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
Rest handlers for Components

Classes:
Component -- Get info about a specific component
ComponentProperties -- Manipulate properties of a specific component
"""

from handler import JsonHandler
from helper import PropertyHelper, PortHelper
from model.domain import Domain

import json


class Component(JsonHandler, PropertyHelper, PortHelper):
    def get(self, domain_name, app_id, comp_id=None):
        dom = Domain(str(domain_name))

        if comp_id:
            comp = dom.find_component(app_id, comp_id)

            info = {
                'name': comp.name,
                'id': comp._id,
                'started': comp._get_started(),
                'ports': self.format_ports(comp.ports),
                'properties': self.format_properties(comp._properties)
            }
        else:
            info = {'components': dom.components(app_id)}

        self._render_json(info)


class ComponentProperties(JsonHandler, PropertyHelper):
    def get(self, domain, waveform, component):
        dom = Domain(str(domain))
        comp = dom.find_component(waveform, component)

        self._render_json({
            'properties': self.format_properties(comp._properties)
        })

    def put(self, domain, waveform, component):
        data = json.loads(self.request.body)

        dom = Domain(str(domain))
        comp = dom.find_component(waveform, component)

        changes = {}
        for p in data['properties']:
            changes[p['id']] = p['value']

        configure_changes = {}
        for prop in comp._properties:
            if prop.id in changes:
                if changes[prop.id] != prop.queryValue():
                    print "New Value", changes[prop.id], '->', prop.queryValue()
                    configure_changes[prop.id] = (type(prop.queryValue()))(changes[prop.id])

        print configure_changes
        comp.configure(configure_changes)
