#!/usr/bin/env python
import json
import os,sys
cwd = os.getcwd()

from model.domain import Domain, ResourceNotFound
from model.domain import scan_domains
import tornado.ioloop
import tornado.web
import tornado.websocket


class JsonHandler(tornado.web.RequestHandler):
    def _handle_request_exception(self, e):
        print 'Exception::', e
        status = 500
        resp = {'message': str(e), 'error': type(e).__name__}

        if type(e) == ResourceNotFound:
            status = 404
        elif type(e) == KeyError:
            resp = {'error': 'JsonParsing', 'message': "Expecting value "+str(e)}
        elif type(e) == ValueError:
            resp = {'error': 'JsonParsing', 'message': str(e)}

        self._render_error(resp, status)

    def _render_json(self, resp):
        if resp and not 'error' in resp:
            self.set_header("Content-Type", "application/json; charset='utf-8'")
            self.write(resp)
        else:
            self._render_error("Unable to find requested resource", 404)

    def _render_error(self, msg, status=500):
        self.set_status(status)
        self.finish(msg)


class DomainInfo(JsonHandler):
    def get(self, domain_name=None):
        if domain_name:
            dom = Domain(str(domain_name))
            info = dom.info()
        else:
            info = {'domains': scan_domains()}
        self._render_json(info)


class DomainProps(JsonHandler):
    def get(self, domain_name, prop_name=None):
        dom = Domain(str(domain_name))
        info = dom.properties()

        if prop_name:
            value = None
            for item in info:
                if item['name'] == prop_name:
                    value = item

            if value:
                self._render_json(value)
            else:
                self._render_json({'error': "Could not find property"})
        else:
            self._render_json({'properties': info})


class DeviceManagers(JsonHandler):
    def get(self, domain_name, dev_mgr_id=None):
        dom = Domain(str(domain_name))

        if dev_mgr_id:
            info = dom.device_manager_info(dev_mgr_id)
        else:
            info = {'deviceManagers': dom.device_managers()}

        self._render_json(info)


class Waveforms(JsonHandler):
    def get(self, domain_name, app_id=None):
        dom = Domain(str(domain_name))

        if app_id:
            info = dom.app_info(app_id)
        else:
            info = {'waveforms': dom.apps(), 'available': dom.available_apps()}

        self._render_json(info)

    def post(self, domain_name):
        data = json.loads(self.request.body)

        app_name = data['name']

        dom = Domain(str(domain_name))
        app_id = dom.launch(app_name)

        self._render_json({'launched': app_id, 'waveforms': dom.apps()})

    def delete(self, domain_name, app_id):
        dom = Domain(str(domain_name))
        dom.release(app_id)

        self._render_json({'released': app_id, 'waveforms': dom.apps()})


class Devices(JsonHandler):
    def get(self, domain_name, dev_mgr_name, dev_id=None):
        dom = Domain(str(domain_name))

        if dev_id:
            info = dom.device_info(dev_mgr_name, dev_id)
        else:
            info = {'devices': dom.devices(dev_mgr_name)}

        self._render_json(info)


class Component(JsonHandler):
    def get(self, domain_name, app_id, comp_id):
        dom = Domain(str(domain_name))
        info = dom.comp_info(app_id, comp_id)

        self._render_json(info)


application = tornado.web.Application([
    (r"/static/(.*)", tornado.web.StaticFileHandler, {"path": cwd+"/static"}),

    (r"/rh/rest/domains/?", DomainInfo),
    (r"/rh/rest/domains/([^/]+)/?", DomainInfo),

    (r"/rh/rest/domains/([^/]+)/properties/?", DomainProps),
    (r"/rh/rest/domains/([^/]+)/properties/([^/]+)", DomainProps),

    (r"/rh/rest/domains/([^/]+)/waveforms/?", Waveforms),
    (r"/rh/rest/domains/([^/]+)/waveforms/([^/]+)", Waveforms),

    (r"/rh/rest/domains/([^/]+)/waveforms/([^/]+)/components/([^/]+)", Component),

    (r"/rh/rest/domains/([^/]+)/deviceManagers/?", DeviceManagers),
    (r"/rh/rest/domains/([^/]+)/deviceManagers/([^/]+)", DeviceManagers),

    (r"/rh/rest/domains/([^/]+)/deviceManagers/([^/]+)/devices/?", Devices),
    (r"/rh/rest/domains/([^/]+)/deviceManagers/([^/]+)/devices/([^/]+)", Devices)
])

if __name__ == '__main__':
    application.listen(8080)
    tornado.ioloop.IOLoop.instance().start()

