"""
Rest handlers for Domains

Classes:
DomainInfo -- Get info of all or a specific domain
DomainProperties -- Manipulate the properties of a domain
"""

from handler import JsonHandler
from model.domain import Domain, scan_domains

class DomainInfo(JsonHandler):
    def get(self, domain_name=None):
        if domain_name:
            dom = Domain(str(domain_name))
            info = dom.info()
        else:
            info = {'domains': scan_domains()}
        self._render_json(info)


class DomainProperties(JsonHandler):
    def get(self, domain_name, prop_name=None):
        dom = Domain(str(domain_name))
        info = dom.properties()

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
