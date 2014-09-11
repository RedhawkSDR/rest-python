#!/usr/bin/env python
import os
from optparse import OptionParser

from rest.domain import DomainInfo, DomainProperties
from rest.waveform import Waveforms
from rest.component import Component, ComponentProperties
from rest.devicemanager import DeviceManagers
from rest.device import Devices, DeviceProperties
from rest.port import PortHandler
from rest.bulkio import BulkIOWebsocketHandler

import tornado.httpserver
import tornado.web
import tornado.websocket
from tornado import ioloop

# setup command line options
from tornado.options import define, options

define('port', default=8080, type='int', help="server port")
define("debug", default=False, type=bool, help="Enable Tornado debug mode.  Reloads code")

_ID = r'/([^/]+)'
_LIST = r'/?'
_DOMAIN_PATH = r'/rh/rest/domains'
_WAVEFORM_PATH = _DOMAIN_PATH + _ID + r'/waveforms'
_COMPONENT_PATH = _WAVEFORM_PATH + _ID + r'/components'
_DEVICE_MGR_PATH = _DOMAIN_PATH + _ID + r'/deviceManagers'
_DEVICE_PATH = _DEVICE_MGR_PATH + _ID + r'/device'
_PROPERTIES_PATH = r'/properties'
_PORT_PATH = r'/ports'
_BULKIO_PATH = _PORT_PATH + _ID + r'/bulkio'

class Application(tornado.web.Application):
    def __init__(self, *args, **kwargs):
        cwd = os.getcwd()

        handlers = [
            (r"/apps/(.*)/$", IndexHandler),
            (r"/apps/(.*)", tornado.web.StaticFileHandler, {"path": cwd+"/apps"}),

            # Domains
            (_DOMAIN_PATH + _LIST, DomainInfo),
            (_DOMAIN_PATH + _ID, DomainInfo),
            (_DOMAIN_PATH + _ID + _PROPERTIES_PATH + _LIST, DomainProperties),
            (_DOMAIN_PATH + _ID + _PROPERTIES_PATH + _ID, DomainProperties),

            # Waveforms
            (_WAVEFORM_PATH + _LIST, Waveforms),
            (_WAVEFORM_PATH + _ID, Waveforms),
            (_WAVEFORM_PATH + _ID + _PORT_PATH + _LIST, PortHandler, dict(kind='waveform')),
            (_WAVEFORM_PATH + _ID + _PORT_PATH + _ID, PortHandler, dict(kind='waveform')),
            (_WAVEFORM_PATH + _ID + _BULKIO_PATH, BulkIOWebsocketHandler, dict(kind='waveform')),

            # Components
            (_COMPONENT_PATH + _LIST, Component),
            (_COMPONENT_PATH + _ID, Component),
            (_COMPONENT_PATH + _ID + _PROPERTIES_PATH + _LIST, ComponentProperties),
            (_COMPONENT_PATH + _ID + _PROPERTIES_PATH + _ID, ComponentProperties),
            (_COMPONENT_PATH + _ID + _PORT_PATH + _LIST, PortHandler, dict(kind='component')),
            (_COMPONENT_PATH + _ID + _PORT_PATH + _ID, PortHandler, dict(kind='component')),
            (_COMPONENT_PATH + _ID + _BULKIO_PATH, BulkIOWebsocketHandler, dict(kind='component')),

            # Device Managers
            (_DEVICE_MGR_PATH + _LIST, DeviceManagers),
            (_DEVICE_MGR_PATH + _ID, DeviceManagers),

            # Devices
            (_DEVICE_PATH + _LIST, Devices),
            (_DEVICE_PATH + _ID, Devices),
            (_DEVICE_PATH + _ID + _PROPERTIES_PATH + _LIST, DeviceProperties),
            (_DEVICE_PATH + _ID + _PROPERTIES_PATH + _ID, DeviceProperties),
            (_DEVICE_PATH + _ID + _PORT_PATH + _LIST, PortHandler, dict(kind='device')),
            (_DEVICE_PATH + _ID + _PORT_PATH + _ID, PortHandler, dict(kind='device')),
            (_DEVICE_PATH + _ID + _BULKIO_PATH, BulkIOWebsocketHandler, dict(kind='device')),
        ]
        tornado.web.Application.__init__(self, handlers, *args, **kwargs)


class IndexHandler(tornado.web.RequestHandler):
    def get(self, path):
        self.render("apps/"+path+"/index.html")


def main():
    tornado.options.parse_command_line()
    application = Application(debug=options.debug)
    application.listen(options.port)
    ioloop.IOLoop.instance().start()

if __name__ == '__main__':
    main()

