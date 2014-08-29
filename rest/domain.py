"""
Rest handlers for Domains

Classes:
DomainInfo -- Get info of all or a specific domain
DomainProperties -- Manipulate the properties of a domain
"""

from handler import JsonHandler
from helper import PropertyHelper
from model.domain import Domain, scan_domains


class DomainInfo(JsonHandler, PropertyHelper):
    def get(self, domain_name=None):
        if domain_name:
            dom = Domain(str(domain_name))
            dom_info = dom._domain()

            info = {
                'id': dom_info._get_identifier(),
                'name': dom_info.name,
                'properties': self.format_properties(dom.properties()),
                'waveforms': dom.apps(),
                'deviceManagers': dom.device_managers()
            }

        else:
            info = {'domains': scan_domains()}
        self._render_json(info)


class DomainProperties(JsonHandler, PropertyHelper):
    def get(self, domain_name, prop_name=None):
        dom = Domain(str(domain_name))
        info = self.format_properties(dom.properties())

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
