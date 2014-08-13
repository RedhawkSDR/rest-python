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
        self.establish_domain()

    def odm_response(self, event):
        for eventH in self.eventHandlers:
            eventH.event_queue.put(event)

    def connect_odm_listener(self):
        self.odmListener = ODMListener()
        self.odmListener.connect(self.domMgr_ptr)
        self.odmListener.deviceManagerAdded.addListener(self.odm_response)
        self.odmListener.deviceManagerRemoved.addListener(self.odm_response)
        self.odmListener.applicationAdded.addListener(self.odm_response)
        self.odmListener.applicationRemoved.addListener(self.odm_response)

    def establish_domain(self):
        redhawk.setTrackApps(False)
        self.domMgr_ptr = redhawk.attach(self.name)
        self.connect_odm_listener()

    def info(self):
        if self.domMgr_ptr:
            ret_dict = [{'domMgrName': self.name}]
            props = self.domMgr_ptr.query([])
            for prop in props:
                ret_dict.append({'prop': {"name": prop.id, "value": str(prop.value._v)}})
            return {'domMgr': ret_dict}
        return None

    def apps(self):
        if self.domMgr_ptr is None:
            return {}
        apps = self.domMgr_ptr.apps
        apps_dict = []
        for app in apps:
            apps_dict.append(app.name)
        return {'waveforms': apps_dict}

    def app_info(self, app_name):
        for app in self.domMgr_ptr.apps:
            if app.name == app_name:
                ret_dict = [{'appName': app_name}]
                for comp in app.comps:
                    ret_dict.append({'comp': {"name": comp.name, "id": comp._id}})
                for prop in app._properties:
                    ret_dict.append({'prop': {"name": prop.clean_name, "value": str(prop.queryValue())}})
                for port in app.ports:
                    ret_dict.append({'port': port.name})
                return {'app': ret_dict}
        return None

    def comp_info(self, app_name, comp_id):
        for app in self.domMgr_ptr.apps:
            if app.name == app_name:
                for comp in app.comps:
                    if comp._id == comp_id:
                        ret_dict= [{'compName': comp.name}, {'compId': comp._id}]
                        for prop in comp._properties:
                            ret_dict.append({'prop':{"name": prop.clean_name, "value": str(prop.queryValue())}})
                        for port in comp.ports:
                            ret_dict.append({'port': port.name})
                        return {'comp': ret_dict}
        return None

    def launch(self, app_name):
        ret_dict = {}
        try:
            app = self.domMgr_ptr.createApplication(str(app_name))
            ret_dict['launched'] = app.name
        except Exception, e:
            ret_dict['error'] = e
        ret_dict.update(self.apps())
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
        ret_dict.update(self.apps())
        return ret_dict

    def available_apps(self):
        if self.domMgr_ptr is None:
            return {}
        sads_full_path = self.domMgr_ptr.catalogSads()
        sads = self.domMgr_ptr._sads
        sad_ret = []
        for idx in range(len(sads)):
            sad_ret.append({'name': sads[idx], 'sad': sads_full_path[idx]})
        return {'availableApps': sad_ret}

    def device_managers(self):
        if self.domMgr_ptr is None:
            return {}
        dev_mgrs = self.domMgr_ptr.devMgrs
        dev_mgrs_dict = []
        for dev_mgr in dev_mgrs:
            dev_mgrs_dict.append({'devMgrName': dev_mgr.name})

        return {'deviceManagers': dev_mgrs_dict}

    def device_manager_info(self, dev_mgr_name):
        for devMgr in self.domMgr_ptr.devMgrs:
            if devMgr.name == dev_mgr_name:
                ret_dict = [{'devMgrName': dev_mgr_name}]
                for dev in devMgr.devs:
                    ret_dict.append({'dev': {"name": dev.name, "id": dev._id}})
                for svc in devMgr.services:
                    ret_dict.append({'svc': {"name": svc.name, "id": svc._id}})
                return {'devMgr': ret_dict}
        return None

    def devices(self, dev_mgr_name):
        for devMgr in self.domMgr_ptr.devMgrs:
            if devMgr.name == dev_mgr_name:
                for dev in devMgr.devs:
                    ret_dict = [
                        {'devName': dev.name},
                        {'devId': dev._id}
                    ]
                    return {'dev': ret_dict}
        return None

    def device_info(self, dev_mgr_name, dev_id):
        for devMgr in self.domMgr_ptr.devMgrs:
            if devMgr.name == dev_mgr_name:
                for dev in devMgr.devs:
                    if dev._id == dev_id:
                        ret_dict= [{'devName': dev.name}, {'devId': dev._id}]
                        for prop in dev._properties:
                            ret_dict.append({'prop': {"name": prop.clean_name, "value": str(prop.queryValue())}})
                        for port in dev.ports:
                            ret_dict.append({'port': port.name})
                        return {'dev': ret_dict}
        return None