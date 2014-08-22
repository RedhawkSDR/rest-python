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

    def find_device_manager(self, device_manager_id=None):
        _dom = self._domain()

        if not device_manager_id:
            return _dom.devMgrs

        for dev_mgr in _dom.devMgrs:
            if dev_mgr.id == device_manager_id:
                return dev_mgr
        raise ResourceNotFound('device manager', device_manager_id)

    def find_device(self, device_manager_id, device_id=None):
        dev_mgr = self.find_device_manager(device_manager_id)

        if not device_id:
            return dev_mgr.devs

        for dev in dev_mgr.devs:
            if dev._id == device_id:
                return dev
        raise ResourceNotFound('device', device_id)

    def find_service(self, device_manager_id, service_id=None):
        dev_mgr = self.find_device_manager(device_manager_id)

        if not service_id:
            return dev_mgr.services

        for svc in dev_mgr.services:
            if svc.id == service_id:
                return svc
        raise ResourceNotFound('service', service_id)

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

    def devices(self, dev_mgr_id):
        devs = self.find_device(dev_mgr_id)
        ret_dict = []
        for dev in devs:
            ret_dict.append({'name': dev.name, 'id': dev._id})
            return ret_dict

    def services(self, dev_mgr_id):
        svcs = self.find_service(dev_mgr_id)
        ret_dict = []
        for svc in svcs:
            ret_dict.append({'name': svc.name, 'id': svc._id})
            return ret_dict