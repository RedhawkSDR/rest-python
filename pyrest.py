#!/usr/bin/env python
import json
import os,sys
cwd = os.getcwd()

from model.domain import Domain
from model.domain import scan_domains
import tornado.ioloop
import tornado.web
import tornado.websocket


class JsonHandler(tornado.web.RequestHandler):
    def _render_json(self, resp):
        if resp:
            self.set_header("Content-Type", "application/json; charset='utf-8'")
            self.write(resp)
        else:
            self._render_error("Unable to find requested resource", 404)

    def _render_error(self, msg, status=500):
        self.set_status(status)
        self.finish({"error": msg})


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
        info = dom.info()

        if prop_name:
            value = None
            for item in info['domMgr']:
                if 'prop' in item and item['prop']['name'] == prop_name:
                    value = item['prop']

            if value:
                self._render_json(value)
            else:
                self._render_json({'error': "Could not find prop"})
        else:
            ret_seq = []
            items = info['domMgr']
            for item in items:
                for entry in item:
                    if entry == 'prop':
                        ret_seq.append(item[entry])
                        break

            self._render_json({'props': ret_seq})


class DeviceManagers(JsonHandler):
    def get(self, domain_name, dev_mgr_name=None):
        dom = Domain(str(domain_name))

        if dev_mgr_name:
            info = dom.device_manager_info(dev_mgr_name)
        else:
            info = dom.device_managers()

        self._render_json(info)


class Waveforms(JsonHandler):
    def get(self, domain_name, app_id=None):
        dom = Domain(str(domain_name))

        if app_id:
            info = dom.app_info(app_id)
        else:
            info = dom.apps()

        self._render_json(info)

    def post(self, domain_name):
        data = json.loads(self.request.body)
        if 'name' in data:
            app_name = data['name']

            dom = Domain(str(domain_name))
            info = dom.launch(app_name)

            self._render_json(info)
        else:
            self._render_error("Request is missing 'name' value", 500)

    def delete(self, domain_name, app_id):
        dom = Domain(str(domain_name))
        info = dom.release(app_id)

        self._render_json(info)


class WaveformsAvailable(JsonHandler):
    def get(self, domain_name):
        dom = Domain(str(domain_name))
        apps = dom.available_apps()

        self._render_json(apps)


class Devices(JsonHandler):
    def get(self, domain_name, dev_mgr_name, dev_id=None):
        dom = Domain(str(domain_name))

        if dev_id:
            info = dom.device_info(dev_mgr_name, dev_id)
        else:
            info = dom.devices(dev_mgr_name)

        self._render_json(info)


class Component(JsonHandler):
    def get(self, domain_name, app_id, comp_id):
        dom = Domain(str(domain_name))
        info = dom.comp_info(app_id, comp_id)

        self._render_json(info)


application = tornado.web.Application([
    (r"/static/(.*)", tornado.web.StaticFileHandler, {"path": cwd+"/static"}),

    (r"/domains/?", DomainInfo),
    (r"/domains/([^/]+)/?", DomainInfo),

    (r"/domains/([^/]+)/properties/?", DomainProps),
    (r"/domains/([^/]+)/properties/([^/]+)", DomainProps),

    (r"/domains/([^/]+)/waveforms/?", Waveforms),
    (r"/domains/([^/]+)/waveforms/available/?", WaveformsAvailable),

    (r"/domains/([^/]+)/waveforms/([^/]+)", Waveforms),

    (r"/domains/([^/]+)/waveforms/([^/]+)/components/([^/]+)", Component),

    (r"/domains/([^/]+)/devicemanagers/?", DeviceManagers),
    (r"/domains/([^/]+)/devicemanagers/([^/]+)", DeviceManagers),

    (r"/domains/([^/]+)/devicemanagers/([^/]+)/devices/?", Devices),
    (r"/domains/([^/]+)/devicemanagers/([^/]+)/devices/([^/]+)", Devices)
])

if __name__ == '__main__':
    application.listen(8080)
    tornado.ioloop.IOLoop.instance().start()

