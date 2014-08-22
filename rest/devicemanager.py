"""
Rest handlers for Device Managers

Classes:
DeviceManagers -- Get info of all or a specific device manager
"""

from handler import JsonHandler
from model.domain import Domain


class DeviceManagers(JsonHandler):
    def get(self, domain_name, dev_mgr_id=None):
        dom = Domain(str(domain_name))

        if dev_mgr_id:
            info = dom.device_manager_info(dev_mgr_id)
        else:
            info = {'deviceManagers': dom.device_managers()}

        self._render_json(info)
