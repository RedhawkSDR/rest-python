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
    def get(self, domain_name, app_id, comp_id):
        dom = Domain(str(domain_name))

        comp = dom.find_component(app_id, comp_id)
        prop_dict = self.format_properties(comp._properties)  # self._props(comp.query([]))

        info = {
            'name': comp.name,
            'id': comp._id,
            'ports': self.format_ports(comp.ports),
            'properties': prop_dict
        }

        self._render_json(info)


class ComponentProperties(JsonHandler):
    def put(self, domain=None, waveform=None, component=None):
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