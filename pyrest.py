#!/usr/bin/env python
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
import os

from rest.domain import DomainInfo, DomainProperties
from rest.application import Applications
from rest.component import Component, ComponentProperties
from rest.devicemanager import DeviceManagers
from rest.device import Devices, DeviceProperties
from rest.port import PortHandler
from rest.bulkio_handler import BulkIOWebsocketHandler
from rest.sysinfo import SysInfoHandler

import tornado.httpserver
import tornado.web
import tornado.websocket
from tornado import ioloop

from model.redhawk import Redhawk

# setup command line options
from tornado.options import define, options

define('port', default=8080, type=int, help="server port")
define("debug", default=False, type=bool, help="Enable Tornado debug mode.  Reloads code")
define('staticpath', default=None, type=str, help='Path to the static content')

_ID = r'/([^/]+)'
_LIST = r'/?'
_REST_PATH = r'/redhawk/rest'
_DOMAIN_PATH = _REST_PATH + '/domains'
_APPLICATION_PATH = _DOMAIN_PATH + _ID + r'/applications'
_COMPONENT_PATH = _APPLICATION_PATH + _ID + r'/components'
_DEVICE_MGR_PATH = _DOMAIN_PATH + _ID + r'/deviceManagers'
_DEVICE_PATH = _DEVICE_MGR_PATH + _ID + r'/devices'
_PROPERTIES_PATH = r'/properties'
_PORT_PATH = r'/ports'
_BULKIO_PATH = _PORT_PATH + _ID + r'/bulkio'


class Application(tornado.web.Application):
    def __init__(self, *args, **kwargs):
        # explicit _ioloop for unit testing
        _ioloop = kwargs.get('_ioloop', None)
        cwd = os.path.abspath(os.path.dirname(__import__(__name__).__file__))
        static_path = kwargs.get('static_path', None)

        # REDHAWK Service
        redhawk = Redhawk()


        handlers = [
            (_REST_PATH + r'/sysinfo', SysInfoHandler, dict(redhawk=redhawk)),

            # Domains
            (_DOMAIN_PATH + _LIST, DomainInfo, dict(redhawk=redhawk)),
            (_DOMAIN_PATH + _ID, DomainInfo, dict(redhawk=redhawk)),
            (_DOMAIN_PATH + _ID + _PROPERTIES_PATH + _LIST, DomainProperties,   
                dict(redhawk=redhawk)),
            (_DOMAIN_PATH + _ID + _PROPERTIES_PATH + _ID, DomainProperties, 
                dict(redhawk=redhawk)),

            # Applications
            (_APPLICATION_PATH + _LIST, Applications, dict(redhawk=redhawk)),
            (_APPLICATION_PATH + _ID, Applications, dict(redhawk=redhawk)),
            (_APPLICATION_PATH + _ID + _PORT_PATH + _LIST, PortHandler, 
                dict(redhawk=redhawk, kind='application')),
            (_APPLICATION_PATH + _ID + _PORT_PATH + _ID, PortHandler, 
                dict(redhawk=redhawk, kind='application')),
            (_APPLICATION_PATH + _ID + _BULKIO_PATH, BulkIOWebsocketHandler, 
                dict(redhawk=redhawk, kind='application', _ioloop=_ioloop)),

            # Components
            (_COMPONENT_PATH + _LIST, Component, dict(redhawk=redhawk)),
            (_COMPONENT_PATH + _ID, Component, dict(redhawk=redhawk)),
            (_COMPONENT_PATH + _ID + _PROPERTIES_PATH + _LIST, ComponentProperties,
                dict(redhawk=redhawk)),
            (_COMPONENT_PATH + _ID + _PROPERTIES_PATH + _ID, ComponentProperties,
                dict(redhawk=redhawk)),
            (_COMPONENT_PATH + _ID + _PORT_PATH + _LIST, PortHandler,
                dict(redhawk=redhawk, kind='component')),
            (_COMPONENT_PATH + _ID + _PORT_PATH + _ID, PortHandler,
                dict(redhawk=redhawk, kind='component')),
            (_COMPONENT_PATH + _ID + _BULKIO_PATH, BulkIOWebsocketHandler,
                dict(redhawk=redhawk, kind='component', _ioloop=_ioloop)),

            # Device Managers
            (_DEVICE_MGR_PATH + _LIST, DeviceManagers, dict(redhawk=redhawk)),
            (_DEVICE_MGR_PATH + _ID, DeviceManagers, dict(redhawk=redhawk)),

            # Devices
            (_DEVICE_PATH + _LIST, Devices, dict(redhawk=redhawk)),
            (_DEVICE_PATH + _ID, Devices, dict(redhawk=redhawk)),
            (_DEVICE_PATH + _ID + _PROPERTIES_PATH + _LIST, DeviceProperties,
                dict(redhawk=redhawk)),
            (_DEVICE_PATH + _ID + _PROPERTIES_PATH + _ID, DeviceProperties,
                dict(redhawk=redhawk)),
            (_DEVICE_PATH + _ID + _PORT_PATH + _LIST, PortHandler,
                dict(redhawk=redhawk, kind='device')),
            (_DEVICE_PATH + _ID + _PORT_PATH + _ID, PortHandler,
                dict(redhawk=redhawk, kind='device')),
            (_DEVICE_PATH + _ID + _BULKIO_PATH, BulkIOWebsocketHandler,
                dict(redhawk=redhawk, kind='device', _ioloop=_ioloop)),
        ]

        if static_path:
	    filehandles = [
                (r"/$", IndexHandler, {"basepath": static_path}),
                (r"/(.*)/$", IndexHandler, {"basepath": static_path}),
                (r"/(.*)", tornado.web.StaticFileHandler, {"path": static_path})
            ]
            handlers.extend(filehandles)

        tornado.web.Application.__init__(self, handlers, *args, **kwargs)


class IndexHandler(tornado.web.RequestHandler):
    
    def initialize(self, basepath):
        self._basepath = basepath
        
    def get(self, path=""):
        filepath = os.path.join(self._basepath, path, "index.html")
        print "Rendering %s" % filepath
        self.render(filepath)


def main():
    tornado.options.parse_command_line()
    application = Application(debug=options.debug, static_path=options['staticpath'])
    application.listen(options.port)
    ioloop.IOLoop.instance().start()

if __name__ == '__main__':
    main()
