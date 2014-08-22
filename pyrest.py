#!/usr/bin/env python
import os

from rest.domain import DomainInfo, DomainProperties
from rest.waveform import Waveforms
from rest.component import Component, ComponentProperties
from rest.devicemanager import DeviceManagers
from rest.device import Devices

import tornado.ioloop
import tornado.web
import tornado.websocket

cwd = os.getcwd()

application = tornado.web.Application([
    (r"/static/(.*)", tornado.web.StaticFileHandler, {"path": cwd+"/static"}),

    (r"/rh/rest/domains/?", DomainInfo),
    (r"/rh/rest/domains/([^/]+)/?", DomainInfo),

    (r"/rh/rest/domains/([^/]+)/properties/?", DomainProperties),
    (r"/rh/rest/domains/([^/]+)/properties/([^/]+)", DomainProperties),

    (r"/rh/rest/domains/([^/]+)/waveforms/?", Waveforms),
    (r"/rh/rest/domains/([^/]+)/waveforms/([^/]+)", Waveforms),

    (r"/rh/rest/domains/([^/]+)/waveforms/([^/]+)/components/?", Component),
    (r"/rh/rest/domains/([^/]+)/waveforms/([^/]+)/components/([^/]+)", Component),
    (r"/rh/rest/domains/([^/]+)/waveforms/([^/]+)/components/([^/]+)/properties", ComponentProperties),

    (r"/rh/rest/domains/([^/]+)/deviceManagers/?", DeviceManagers),
    (r"/rh/rest/domains/([^/]+)/deviceManagers/([^/]+)", DeviceManagers),

    (r"/rh/rest/domains/([^/]+)/deviceManagers/([^/]+)/devices/?", Devices),
    (r"/rh/rest/domains/([^/]+)/deviceManagers/([^/]+)/devices/([^/]+)", Devices)
])

if __name__ == '__main__':
    application.listen(8080)
    tornado.ioloop.IOLoop.instance().start()

