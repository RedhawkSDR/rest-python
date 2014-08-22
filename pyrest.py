#!/usr/bin/env python
import os
from optparse import OptionParser

from rest.domain import DomainInfo, DomainProperties
from rest.waveform import Waveforms
from rest.component import Component, ComponentProperties
from rest.devicemanager import DeviceManagers
from rest.device import Devices

import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.websocket


class Application(tornado.web.Application):
    def __init__(self):
        cwd = os.getcwd()

        handlers = [
            (r"/apps/(.*)/$", IndexHandler),
            (r"/apps/(.*)", tornado.web.StaticFileHandler, {"path": cwd+"/apps"}),

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
        ]
        settings = {}
        tornado.web.Application.__init__(self, handlers, **settings)


class IndexHandler(tornado.web.RequestHandler):
    def get(self, path):
        self.render("apps/"+path+"/index.html")


def main():
    parser = OptionParser()
    parser.add_option("-p", "--port", dest='port', default=8080, type='int', help="server port")
    (options, args) = parser.parse_args()

    port = options.port
    print "Starting server on port %s" % port

    application = Application()
    http_server = tornado.httpserver.HTTPServer(application)

    http_server.listen(port)

    tornado.ioloop.IOLoop.instance().start()

if __name__ == '__main__':
    main()

