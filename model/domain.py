from ossie.utils import redhawk
from ossie.utils.redhawk.channels import ODMListener

__author__ = 'rpcanno'


def scan_domains():
    return redhawk.scan()


class Domain:
    domMgr_ptr = None
    odmListener = None
    eventHandlers = []
    name = None

    def __init__(self, domainname):
        self.name = domainname
        self._establish_domain()

    def _odm_response(self, event):
        for eventH in self.eventHandlers:
            eventH.event_queue.put(event)

    def _connect_odm_listener(self):
        self.odmListener = ODMListener()
        self.odmListener.connect(self.domMgr_ptr)
        self.odmListener.deviceManagerAdded.addListener(self._odm_response)
        self.odmListener.deviceManagerRemoved.addListener(self._odm_response)
        self.odmListener.applicationAdded.addListener(self._odm_response)
        self.odmListener.applicationRemoved.addListener(self._odm_response)

    def _establish_domain(self):
        redhawk.setTrackApps(False)
        self.domMgr_ptr = redhawk.attach(self.name)
        self._connect_odm_listener()

    def _props(self, properties):
        prop_dict = []
        for prop in properties:
            prop_dict.append({'id': prop.id, "value": prop.value.value()})
        return prop_dict

    def _ports(self, ports):
        port_dict = []
        for port in ports:
            port_value = {'name': port.name, 'direction': port._direction}
            if port._direction == 'Uses':
                port_value['type'] = port._using.name
                port_value['namespace'] = port._using.nameSpace
            port_dict.append(port_value)
        return port_dict

    def properties(self):
        props = self.domMgr_ptr.query([])
        return self._props(props)

    def info(self):
        if self.domMgr_ptr:
            return {
                'id': self.name,
                'properties': self.properties(),
                'waveforms': self.apps(),
                'deviceManagers': self.device_managers()
            }
        return None

    def apps(self):
        if self.domMgr_ptr is None:
            return {}
        apps = self.domMgr_ptr.apps
        apps_dict = []
        for app in apps:
            apps_dict.append(app.name)
        return apps_dict

    def app_info(self, app_name):
        for app in self.domMgr_ptr.apps:
            if app.name == app_name:
                comp_dict = []
                for comp in app.comps:
                    comp_dict.append({"name": comp.name, "id": comp._id})
                return {
                    'id': app_name,
                    'components': comp_dict,
                    'ports': self._ports(app.ports),
                    'properties': self._props(app.query([]))
                }
        return None

    def comp_info(self, app_name, comp_id):
        for app in self.domMgr_ptr.apps:
            if app.name == app_name:
                for comp in app.comps:
                    if comp._id == comp_id:
                        prop_dict = []
                        for prop in comp._properties:
                            prop_dict.append({"name": prop.clean_name, "value": str(prop.queryValue())})

                        return {
                            'name': comp.name,
                            'id': comp._id,
                            'ports': self._ports(comp.ports),
                            'properties': self._props(comp.query([]))
                        }
        return None

    def launch(self, app_name):
        ret_dict = {}
        try:
            app = self.domMgr_ptr.createApplication(str(app_name))
            ret_dict['launched'] = app.name
        except Exception, e:
            ret_dict['error'] = e
        return ret_dict

    def release(self, app_id):
        ret_dict = {}
        try:
            apps = self.domMgr_ptr.apps
            for app in apps:
                if app.name == app_id:
                    app.releaseObject()
                    ret_dict['released'] = app.name
                    break
        except Exception, e:
            ret_dict['error'] = e
        return ret_dict

    def available_apps(self):
        if self.domMgr_ptr is None:
            return {}
        sads_full_path = self.domMgr_ptr.catalogSads()
        sads = self.domMgr_ptr._sads
        sad_ret = []
        for idx in range(len(sads)):
            sad_ret.append({'name': sads[idx], 'sad': sads_full_path[idx]})
        return sad_ret

    def device_managers(self):
        if self.domMgr_ptr is None:
            return {}
        dev_mgrs = self.domMgr_ptr.devMgrs
        dev_mgrs_dict = []
        for dev_mgr in dev_mgrs:
            print dir(dev_mgr)
            dev_mgrs_dict.append({'name': dev_mgr.name, 'id': dev_mgr.id})

        return dev_mgrs_dict

    def device_manager_info(self, dev_mgr_id):
        for devMgr in self.domMgr_ptr.devMgrs:
            if devMgr.id == dev_mgr_id:
                dev_dict = []
                for dev in devMgr.devs:
                    dev_dict.append({"name": dev.name, "id": dev._id})

                svc_dict = []
                for svc in devMgr.services:
                    svc_dict.append({"name": svc.name, "id": svc._id})
                return {
                    'name': devMgr.name,
                    'id': devMgr.id,
                    'properties': self._props(devMgr.query([])),
                    'devices': dev_dict,
                    'services': svc_dict
                }
        return None

    def devices(self, dev_mgr_name):
        for devMgr in self.domMgr_ptr.devMgrs:
            if devMgr.name == dev_mgr_name:
                ret_dict = []
                for dev in devMgr.devs:
                    ret_dict.append({'name': dev.name, 'id': dev._id})
                    return ret_dict
        return None

    def device_info(self, dev_mgr_name, dev_id):
        for devMgr in self.domMgr_ptr.devMgrs:
            if devMgr.name == dev_mgr_name:
                for dev in devMgr.devs:
                    if dev._id == dev_id:
                        prop_dict = []
                        for prop in dev._properties:
                            prop_dict.append({"name": prop.clean_name, "value": prop.queryValue()})

                        return {'name': dev.name, 'id': dev._id, 'ports': self._ports(dev.ports), 'properties': prop_dict}
        return None