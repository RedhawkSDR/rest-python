#
# This file is protected by Copyright. Please refer to the COPYRIGHT file
# distributed with this source distribution.
#
# This file is part of REDHAWK rest-python.
#
# REDHAWK rest-python is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# REDHAWK rest-python is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see http://www.gnu.org/licenses/.
#
"""
REDHAWK Helper class used by the Server Handlers
"""

import logging
import re
from ossie.utils import redhawk
from ossie.utils.redhawk.channels import ODMListener
from ossie.cf.CF import InvalidObjectReference
from omniORB import CORBA

_logger = logging.getLogger(__name__)

class ResourceNotFound(Exception):
    def __init__(self, resource='resource', name='Unknown', msg=None):
        self.name = name
        self.resource = resource
        self.msg = msg if msg else "Unable to find %s '%s'" % (self.resource, self.name)

    def __str__(self):
        return self.msg


class WaveformLaunchError(Exception):
    def __init__(self, name='Unknown', msg=''):
        self.name = name
        self.msg = msg

    def __str__(self):
        return "Not able to launch waveform '%s'. %s" % (self.name, self.msg)


class ApplicationReleaseError(Exception):
    def __init__(self, name='Unknown', msg=''):
        self.name = name
        self.msg = msg

    def __str__(self):
        return "Not able to release waveform '%s'. %s" % (self.name, self.msg)

def scan_domains(location=None):
    _logger.debug("Scan domains(location=%s). redhawk_remote_bug=%s", location, redhawk_remote_bug)
    if redhawk_remote_bug and location and location != 'localhost':
        raise Exception('Remote domain connectivity is unavailable in Redhawk <= 1.10.2')
    
    try:
        return [ build_domainref(location, d) for d in redhawk.scan(location) ]
    except RuntimeError, e:
        # FIXME: Runtime Error is not very descriptive.  Need to weed out other problems
        if not location:
            location = 'localhost'
        raise ResourceNotFound(msg="Unable to connect with NameService on host '%s'" % location)


def parse_domainref(domainref):
    '''
        Parses a domain reference: location + ':' + DOMAINNAME

        Note that a location can be a hostname or an IP address (ipv4 and ipv6).
        Locations may be omitted by just including the DOMAINNAME, unless the
        DOMAINNAME includes a colon, in which case a blank location can
        be specified by using a leading (e.g. ":DOMAIN:NAME" yields [None, 'DOMAIN:NAME'])

        ipv6 addresses should be surrounded by a '[' and ']' much like
        https://www.ietf.org/rfc/rfc2732.txt

        :param domainref: A formatted domain reference
        :return: [location, domainname] list

       >>> parse_domainref('DOMAINNAME')
       (None, 'DOMAINNAME')
       >>> parse_domainref(':DOMAIN:NAME')
       (None, 'DOMAIN:NAME')
       >>> parse_domainref('DOMAIN:NAME')
       ('DOMAIN', 'NAME')
       >>> parse_domainref('127.2.7.1:NAME')
       ('127.2.7.1', 'NAME')
       >>> parse_domainref('localhost:NAME')
       ('localhost', 'NAME')
       >>> parse_domainref('[::1]:NAME')
       ('::1', 'NAME')
       >>> parse_domainref('[::1]:DOMAIN:NAME')
       ('::1', 'DOMAIN:NAME')
       >>> parse_domainref('[::1]:]DOMAIN:NAME')
       ('::1', ']DOMAIN:NAME')
       >>> parse_domainref('[::1:DOMAIN:NAME')
       ('[', ':1:DOMAIN:NAME')
       >>> parse_domainref('localhost:')
       ('localhost', None)
       >>> parse_domainref('')
       Traceback (most recent call last):
       ...
       ValueError: invalid domain reference ''
       >>> parse_domainref(':localhost:')
       (None, 'localhost:')
       >>> parse_domainref('[DOMAINNAME]XXX')
       (None, '[DOMAINNAME]XXX')
       >>> parse_domainref(u'foo:DOMAINNAME')
       ('foo', 'DOMAINNAME')
    '''
    if not domainref:
        raise ValueError("invalid domain reference '%s'" % domainref)
    if domainref[0] == ':':
        return (None, domainref[1:])
    if domainref[0] == '[' and ']' in domainref:
        addr, domain = domainref.split(']', 1)
        if domain and domain[0] == ':':
            return (addr[1:], parse_domainref(domain)[1])

        return None, domainref
    rtn = str(domainref).split(':', 1)
    if len(rtn) == 1:
        return (None, rtn[0])
    if not rtn[1]:
        return (rtn[0], None)
    return (rtn[0], rtn[1])

def build_domainref(location, domain):
    '''
        Generates a safe domainref using a location and a domain.  Escapes things as necessary
        
        >>> build_domainref(None, 'Domainname')
        'Domainname'
        >>> build_domainref('Hostname', 'Domainname')
        'Hostname:Domainname'
        >>> build_domainref('Hostname', None)
        'Hostname:'
        >>> build_domainref('Hostname', '')
        'Hostname:'
        >>> build_domainref('', 'DOMAIN')
        'DOMAIN'
        >>> build_domainref('', 'Domainname')
        'Domainname'
        >>> build_domainref('', ':Domainname')
        '::Domainname'
        >>> build_domainref('', 'Domainname:')
        ':Domainname:'
        >>> build_domainref('127.2.7.1', 'NAME')
        '127.2.7.1:NAME'
        >>> build_domainref('::1', 'NAME')
        '[::1]:NAME'
        >>> build_domainref(None, '[DOMAINNAME]XXX')
        '[DOMAINNAME]XXX'
        >>> build_domainref('[', ':1:DOMAIN:NAME')
        '[::1:DOMAIN:NAME'
    '''
    if not domain:
        domain = ''
    domain = str(domain)
    if not location:
        if ':' in domain:
            return ":%s" % domain
        else:
            return domain
    location = str(location)
    if ":" in location:
        location = "[%s]" % location
    return "%s:%s" % (location, domain)

def _parse_dist_version(distver, element=None):
    '''
    :param distver: distribution version from pkg_resources
    :return: a three element tuple of only the integers
        >>> _parse_dist_version(('00000001', '00000010', '00000002', '*final'))
        (1, 10, 2)
        >>> _parse_dist_version(('00000002', '00000012', '00000002', '*final'))
        (2, 12, 2)
        >>> _parse_dist_version(('00000002', '00000012', '0000002b', '*final'))
        (2, 12, 2)
        >>> _parse_dist_version(('00000002', '00000012', '000000b', '*final'))
        (2, 12, 0)
        >>> _parse_dist_version(('00000002', '00000012', 'b', '*final'))
        (2, 12, 0)
    '''
    if element is None:
        return (_parse_dist_version(distver, 0),
                _parse_dist_version(distver, 1),
                _parse_dist_version(distver, 2))
    try:
        return int(re.findall('\d+', distver[element])[0])
    except (ValueError, IndexError):
        return 0

def _identify_buggy_redhawk_location(v):
    '''
    Identifies the python code that is unable to connect to more
    than a single remote location. The bug means that only the first
    location is used.  And subsequent calls with different locations
    will connect only use the first location.  Bug is fixed
    in Redhawk 1.10.3 (core framework v 1.10.2) 
    
    :param v: tuple representing version major, minor, patch
    :return: boolean
       >>> _identify_buggy_redhawk_location((1, 10, 1))
       True
       >>> _identify_buggy_redhawk_location((1, 10, 2))
       False
       >>> _identify_buggy_redhawk_location((1, 11, 1))
       False
       >>> _identify_buggy_redhawk_location((2, 1, 1))
       False
       >>> _identify_buggy_redhawk_location((1, 9, 2))
       True
    '''
    return v[0] == 1 and ((v[1] == 10 and v[2] < 2) or v[1] < 10)

def get_redhawk_version():
    '''
        Attempt to find redhawk version.
        :return: the version
    '''
    try:
        import pkg_resources
        dist = pkg_resources.get_distribution('ossiepy')
        return _parse_dist_version(dist.parsed_version)
    except Exception, e:
        _logger.exception("Unable to determine redhawk_version")
        raise

def has_remote_location_bug():
    try:
        return _identify_buggy_redhawk_location(get_redhawk_version())
    except Exception, e:
        _logger.exception("Unable to determine redhawk_version so turning off remote locations")
        return True
    
redhawk_remote_bug = has_remote_location_bug()

class Domain:
    domMgr_ptr = None
    odmListener = None
    eventHandlers = []
    name = None

    def __init__(self, domainref):
        location, domainname = parse_domainref(domainref)
        if redhawk_remote_bug and location and location != 'localhost':
            raise Exception('Remote domain connectivity is unavailable in Redhawk <= 1.10.2')

        _logger.debug("Establishing domain %s at location %s", domainname, location,  exc_info=True)
        
        self._domainref = domainref
        self.name = domainname
        self.location = location

        try:
            self._establish_domain()
        except StandardError, e:
            _logger.warn("Unable to find domain %s", e, exc_info=1)
            raise ResourceNotFound("domain", domainref)

    def _odm_response(self, event):
        for eventH in self.eventHandlers:
            eventH.event_queue.put(event)

    def _connect_odm_listener(self):
        
        listener = ODMListener()
        listener.connect(self.domMgr_ptr)
        listener.deviceManagerAdded.addListener(self._odm_response)
        listener.deviceManagerRemoved.addListener(self._odm_response)
        listener.applicationAdded.addListener(self._odm_response)
        listener.applicationRemoved.addListener(self._odm_response)
        self.odmListener = listener

    def _establish_domain(self):
        redhawk.setTrackApps(False)
        try:
            self.domMgr_ptr = redhawk.attach(self.name, self.location)
        except CORBA.TRANSIENT:
            raise ResourceNotFound('domain', self._domainref)
        
        self.domMgr_ptr.__odmListener = None
        try:
            self._connect_odm_listener()
        except InvalidObjectReference:
            _logger.warn("%s: Unable to connect with EventChannel", self._domainref,
                         exc_info=True)

    def properties(self):
        props = self.domMgr_ptr.query([])  # TODO: self.domMgr_ptr._properties
        return props

    def get_domain_info(self):
        if self.domMgr_ptr:
            return self.domMgr_ptr
        raise ResourceNotFound('domain', self.name)

    def find_app(self, app_id=None):
        _dom = self.get_domain_info()
        apps = _dom.apps

        if not app_id:
            return apps

        for app in apps:
            if app._get_identifier() == app_id:
                return app
        raise ResourceNotFound('application', app_id)

    def find_component(self, app_id, comp_id=None):
        app = self.find_app(app_id)

        if not comp_id:
            return app.comps

        for comp in app.comps:
            if comp._id == comp_id:
                return comp
        raise ResourceNotFound('component', comp_id)

    def find_device_manager(self, device_manager_id=None):
        _dom = self.get_domain_info()

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
        _dom = self.get_domain_info()
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
            raise ApplicationReleaseError(app_id, str(e))

    def available_apps(self):
        _dom = self.get_domain_info()
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
            ret_dict.append({'name': svc._instanceName, 'id': svc._refid})
            return ret_dict


if __name__ == '__main__':
    import doctest
    doctest.testmod()
