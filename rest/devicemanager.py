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
