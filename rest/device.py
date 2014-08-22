"""
Rest handlers for Devices

Classes:
Device -- Get info of a specific device
"""

from handler import JsonHandler
from model.domain import Domain


class Devices(JsonHandler):
    def get(self, domain_name, dev_mgr_name, dev_id=None):
        dom = Domain(str(domain_name))

        if dev_id:
            info = dom.device_info(dev_mgr_name, dev_id)
        else:
            info = {'devices': dom.devices(dev_mgr_name)}

        self._render_json(info)