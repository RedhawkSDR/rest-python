from omniORB import CORBA
from ossie.utils import redhawk
from ossie.utils.redhawk.channels import ODMListener
__author__ = 'rpcanno'


def scan_domains():
    return redhawk.scan()


def _my_dir(obj):
    return [m for m in dir(obj) if not m.startswith('__')]

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

    def _any_simple(self, any):
        return {'scaType': 'simple', 'value': any._v}

    def _any_struct(self, any):
        ret = {'scaType': 'struct'}
        value = {}
        for a in any._v:
            #ret['value'].append(self._prop(a))
            value[a.id] = a.value._v
        ret['value'] = value
        return ret

    def _any_seq(self, any):
        ret = {'scaType': 'seq', 'value': []}
        for a in any._v:
            ret['value'].append(self._any(a))
        return ret

    def _any(self, any):
        typeName = str(any._t)

        if 'CORBA.TypeCode("IDL:CF/Properties:1.0")' == typeName:
            return self._any_struct(any)
        elif 'CORBA.TypeCode("IDL:omg.org/CORBA/AnySeq:1.0")' == typeName:
            return self._any_seq(any)
        else:
            return self._any_simple(any)

    def _prop(self, property):
        ret = self._any(property.value)
        ret['id'] = property.id
        return ret

    def _props(self, properties):
        prop_dict = []
        for prop in properties:
            prop_dict.append(self._prop(prop))

        return prop_dict

    def _propSet(self, properties):
        prop_dict = []
        for prop in properties:
            if prop.type != 'struct' and prop.type != 'structSeq':
                if isinstance(prop.queryValue(), list):
                    prop_type = "simpleSeq"
                else:
                    prop_type = 'simple'
            else:
                prop_type = prop.type

            prop_json = {
                'id': prop.id,
                'name': prop.clean_name,
                'value': prop.queryValue(),
                'scaType': prop_type,
                'mode': prop.mode,
                'kinds': prop.kinds
            }

            if prop_type == 'simple':
                prop_json['type'] = type(prop.queryValue()).__name__
                if prop_json['type'] == 'str':
                    prop_json['type'] = 'string'
                elif prop_json['type'] == 'bool':
                    prop_json['type'] = 'boolean'

            if '_enums' in dir(prop) and prop._enums:
                prop_json['enumerations'] = prop._enums

            prop_dict.append(prop_json)
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
        props = self._props(self.domMgr_ptr.query([]))  # TODO: self._propSet(self.domMgr_ptr._properties)
        return props

    def info(self):
        if self.domMgr_ptr:
            return {
                'id': self.domMgr_ptr._get_identifier(),
                'name': self.name,
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
            apps_dict.append({'name': app.name, 'id': app._get_identifier()})
        return apps_dict

    def app_info(self, app_id):
        for app in self.domMgr_ptr.apps:
            if app._get_identifier() == app_id:
                comp_dict = []
                for comp in app.comps:
                    comp_dict.append({"name": comp.name, "id": comp._id})
                prop_dict = self._propSet(app._properties)  # self._props(app.query([]))
                return {
                    'id': app._get_identifier(),
                    'name': app.name,
                    'components': comp_dict,
                    'ports': self._ports(app.ports),
                    'properties': prop_dict
                }
        return None

    def comp_info(self, app_id, comp_id):
        for app in self.domMgr_ptr.apps:
            if app._get_identifier() == app_id:
                for comp in app.comps:
                    if comp._id == comp_id:
                        prop_dict = self._propSet(comp._properties)  # self._props(comp.query([]))

                        return {
                            'name': comp.name,
                            'id': comp._id,
                            'ports': self._ports(comp.ports),
                            'properties': prop_dict
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
                if app._get_identifier() == app_id:
                    app.releaseObject()
                    ret_dict['released'] = app.name
                    break
        except Exception, e:
            ret_dict['error'] = e

        if not 'released' in ret_dict:
            ret_dict['error'] = 'Waveform id ('+app_id+') not found.'

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

                prop_dict = self._props(devMgr.query([]))  # TODO: self._propSet(devMgr._properties)
                return {
                    'name': devMgr.name,
                    'id': devMgr.id,
                    'properties': prop_dict,
                    'devices': dev_dict,
                    'services': svc_dict
                }
        return None

    def devices(self, dev_mgr_id):
        for devMgr in self.domMgr_ptr.devMgrs:
            if devMgr.id == dev_mgr_id:
                ret_dict = []
                for dev in devMgr.devs:
                    ret_dict.append({'name': dev.name, 'id': dev._id})
                    return ret_dict
        return None

    def device_info(self, dev_mgr_id, dev_id):
        for devMgr in self.domMgr_ptr.devMgrs:
            if devMgr.id == dev_mgr_id:
                for dev in devMgr.devs:
                    if dev._id == dev_id:
                        prop_dict = self._propSet(dev._properties)

                        return {
                            'name': dev.name,
                            'id': dev._id,
                            'started': dev._get_started(),
                            'ports': self._ports(dev.ports),
                            # 'properties': self._props(dev.query([])),
                            'properties': prop_dict
                        }
        return None