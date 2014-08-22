from ossie.utils import redhawk
from ossie.utils.redhawk.channels import ODMListener
from rest.helper import PropertyHelper, PortHelper

__author__ = 'rpcanno'


def scan_domains():
    return redhawk.scan()


def _my_dir(obj):
    return [m for m in dir(obj) if not m.startswith('__')]


class ResourceNotFound(Exception):
    def __init__(self, resource='resource', name='Unknown'):
        self.name = name
        self.resource = resource

    def __str__(self):
        return "Unable to find %s '%s'" % (self.resource, self.name)


class InvalidWaveform(Exception):
    def __init__(self, name='Unknown'):
        self.name = name

    def __str__(self):
        return "'%s' is not a valid waveform" % self.name


class WaveformLaunchError(Exception):
    def __init__(self, name='Unknown', msg=''):
        self.name = name
        self.msg = msg

    def __str__(self):
        return "Not able to launch waveform '%s'. %s" % (self.name, self.msg)


class WaveformReleaseError(Exception):
    def __init__(self, name='Unknown', msg=''):
        self.name = name
        self.msg = msg

    def __str__(self):
        return "Not able to release waveform '%s'. %s" % (self.name, self.msg)


class Domain(PropertyHelper, PortHelper):
    domMgr_ptr = None
    odmListener = None
    eventHandlers = []
    name = None

    def __init__(self, domainname):
        self.name = domainname
        try:
            self._establish_domain()
        except StandardError:
            raise ResourceNotFound("domain", domainname)

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

    def properties(self):
        props = self.format_properties(self.domMgr_ptr.query([]))  # TODO: self._propSet(self.domMgr_ptr._properties)
        return props

    def _domain(self):
        if self.domMgr_ptr:
            return self.domMgr_ptr
        raise ResourceNotFound('domain', self.name)

    def find_app(self, app_id=None):
        _dom = self._domain()
        apps = _dom.apps

        if not app_id:
            return apps

        for app in apps:
            if app._get_identifier() == app_id:
                return app
        raise ResourceNotFound('waveform', app_id)

    def find_component(self, app_id, comp_id=None):
        app = self.find_app(app_id)

        if not comp_id:
            return app.comps

        for comp in app.comps:
            if comp._id == comp_id:
                return comp
        raise ResourceNotFound('component', comp_id)

    def apps(self):
        apps_dict = []
        apps = self.find_app()
        for app in apps:
            apps_dict.append({'name': app.name, 'id': app._get_identifier()})
        return apps_dict

    def components(self, app_id):
        comps_dict = []
        comps = self.find_component(app_id)
        for comp in comps:
            comps_dict.append({'name': comp.name, 'id': comp._get_identifier()})
        return comps_dict

    def launch(self, app_name):
        _dom = self._domain()
        try:
            app = _dom.createApplication(app_name)
            return app._get_identifier()
        except Exception, e:
            raise WaveformLaunchError(app_name, str(e))

    def release(self, app_id):
        app = self.find_app(app_id)
        try:
            app.releaseObject()
            return app_id
        except Exception, e:
            raise WaveformReleaseError(app_id, str(e))

    def available_apps(self):
        _dom = self._domain()
        sads_full_path = _dom.catalogSads()
        sads = _dom._sads
        sad_ret = []
        for idx in range(len(sads)):
            sad_ret.append({'name': sads[idx], 'sad': sads_full_path[idx]})
        return sad_ret

    def device_managers(self):
        if self.domMgr_ptr is None:
            raise ResourceNotFound('domain', self.name)
        dev_mgrs = self.domMgr_ptr.devMgrs
        dev_mgrs_dict = []
        for dev_mgr in dev_mgrs:
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

                prop_dict = self.format_properties(devMgr.query([]))  # TODO: self._propSet(devMgr._properties)
                return {
                    'name': devMgr.name,
                    'id': devMgr.id,
                    'properties': prop_dict,
                    'devices': dev_dict,
                    'services': svc_dict
                }
        raise ResourceNotFound('device manager', dev_mgr_id)

    def devices(self, dev_mgr_id):
        for devMgr in self.domMgr_ptr.devMgrs:
            if devMgr.id == dev_mgr_id:
                ret_dict = []
                for dev in devMgr.devs:
                    ret_dict.append({'name': dev.name, 'id': dev._id})
                    return ret_dict
        raise ResourceNotFound('device manager', dev_mgr_id)

    def device_info(self, dev_mgr_id, dev_id):
        for devMgr in self.domMgr_ptr.devMgrs:
            if devMgr.id == dev_mgr_id:
                for dev in devMgr.devs:
                    if dev._id == dev_id:
                        prop_dict = self.format_properties(dev._properties)

                        return {
                            'name': dev.name,
                            'id': dev._id,
                            'started': dev._get_started(),
                            'ports': self.format_ports(dev.ports),
                            # 'properties': self.format_properties(dev.query([])),
                            'properties': prop_dict
                        }
                raise ResourceNotFound('device', dev_id)
        raise ResourceNotFound('device manager', dev_mgr_id)