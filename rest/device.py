"""
Rest handlers for Devices

Classes:
Device -- Get info of a specific device
"""

from handler import JsonHandler
from helper import PropertyHelper, PortHelper
from model.domain import Domain
from tornado import web


class Devices(JsonHandler, PropertyHelper, PortHelper):
    def get(self, domain_name, dev_mgr_id, dev_id=None):
        dom = Domain(str(domain_name))

        if dev_id:
            dev = dom.find_device(dev_mgr_id, dev_id)

            info = {
                'name': dev.name,
                'id': dev._id,
                'started': dev._get_started(),
                'ports': self.format_ports(dev.ports),
                # 'properties': self.format_properties(dev.query([])),
                'properties': self.format_properties(dev._properties)
            }
        else:
            info = {'devices': dom.devices(dev_mgr_id)}

        self._render_json(info)


class DeviceProperties(web.RequestHandler):

    def get(self, *args):
        self.set_status(500)
        self.write(dict(status='Device Properties handler not implemented'))