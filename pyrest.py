#!/usr/bin/env python
import os,sys
cwd = os.getcwd()
print cwd

from model import domain
import tornado.ioloop
import tornado.web
import tornado.websocket
import threading
import json

class OdmEvents(tornado.websocket.WebSocketHandler):
    def open(self):
        self.odmContainer = domain.odmStreamHandler(self)
        self._runThread = threading.Thread(target=self.odmContainer.thread_function)
        self._runThread.setDaemon(True)
        self._runThread.start()

    def on_message(self, message):
        pass

    def on_close(self):
        self.odmContainer.closeOdmStream()

class Main(tornado.web.RequestHandler):
    def get(self):
        self.redirect('/domain')

class Domain(tornado.web.RequestHandler):
    def get(self):
        domains = domain.scan_domains()

        self.set_header("Content-Type", "application/json; charset='utf-8'")
        self.write({'domains': domains})

class SingleDomain(tornado.web.RequestHandler):
    def get(self, domainname):
        domain_ptr = domain.connectToDomain(domainname)
        return self.render('templates/domain.html',name=domainname)

class SingleDomainInfo(tornado.web.RequestHandler):
    def get(self, domainname):
        domain.connectToDomain(domainname)
        resp=domain.retrieveDomMgrInfo(domainname)

        self.set_header("Content-Type", "application/json; charset='utf-8'")
        self.write(resp)

class DomainProps(tornado.web.RequestHandler):
    def get(self, domainname):
        resp=domain.retrieveDomMgrInfo(domainname)
        ret_seq = []
        items=eval(resp)['domMgr']
        for item in items:
            for entry in item:
                if entry == 'prop':
                    ret_seq.append(item[entry])
                    break
        ret_dict = {'props':ret_seq}
        return_value = json.dumps(ret_dict)
        self.write(return_value)

class SingleDomainProp(tornado.web.RequestHandler):
    def get(self, domainname, propname):
        resp=domain.retrieveDomMgrInfo(domainname)
        self.set_header("Content-Type", "application/json; charset='utf-8'")
        self.write(resp)

class DeviceManagers(tornado.web.RequestHandler):
    def get(self, domainname):
        dm=domainname
        json_msg=domain.retrieveDevMgrs(dm)

        self.set_header("Content-Type", "application/json; charset='utf-8'")
        self.write(json_msg)

class Applications(tornado.web.RequestHandler):
    def get(self, domain_name):
        json_msg=domain.retrieveApps(domain_name)

        self.set_header("Content-Type", "application/json; charset='utf-8'")
        self.write(json_msg)

class AvailableApplications(tornado.web.RequestHandler):
    def get(self, domainname):
        json_msg=domain.retrieveAvailableApps(domainname)

        self.set_header("Content-Type", "application/json; charset='utf-8'")
        self.write(json_msg)

class DeviceManager(tornado.web.RequestHandler):
    def get(self, domainname, devmgrname):
        resp=domain.retrieveDevMgrInfo(domainname,devmgrname)

        self.set_header("Content-Type", "application/json; charset='utf-8'")
        self.write(resp)

class Application(tornado.web.RequestHandler):
    def get(self, domainname, appname):
        resp = domain.retrieveAppInfo(domainname, appname)

        self.set_header("Content-Type", "application/json; charset='utf-8'")
        self.write(resp)


class LaunchApplication(tornado.web.RequestHandler):
    def get(self, domainname):
        appname = self.get_argument("waveform")
        resp=domain.launchApp(domainname,appname)

        self.set_header("Content-Type", "application/json; charset='utf-8'")
        self.write(resp)


class ReleaseApplication(tornado.web.RequestHandler):
    def get(self, domainname):
        appid = self.get_argument("waveform")
        resp=domain.releaseApp(domainname,appid)

        self.set_header("Content-Type", "application/json; charset='utf-8'")
        self.write(resp)


class Device(tornado.web.RequestHandler):
    def get(self, domainname, devmgrname, devname):
        resp=domain.retrieveDevInfo(domainname,devmgrname,devname)

        self.set_header("Content-Type", "application/json; charset='utf-8'")
        self.write(resp)

class Service(tornado.web.RequestHandler):
    def get(self, domainname, devmgrname, svcname):
        resp=domain.retrieveSvcInfo(domainname,devmgrname,svcname)

        self.set_header("Content-Type", "application/json; charset='utf-8'")
        self.write(resp)


class DevMgrProp(tornado.web.RequestHandler):
    def get(self, domainname, devmgrname, propname):
        resp=domain.retrieveDevMgrProp(domainname,devmgrname,propname)

        self.set_header("Content-Type", "application/json; charset='utf-8'")
        self.write(resp)


class Devices(tornado.web.RequestHandler):
    def get(self, domainname, devmgrname):
        resp=domain.retrieveDevs(domainname, devmgrname)

        self.set_header("Content-Type", "application/json; charset='utf-8'")
        self.write(resp)

class Services(tornado.web.RequestHandler):
    def get(self, domainname, devmgrname):
        resp=domain.retrieveSvcs(domainname,devmgrname,svcname)
        return_value = json.dumps(resp)
        self.write(return_value)

class DevMgrProps(tornado.web.RequestHandler):
    def get(self, domainname, devmgrname):
        resp=domain.retrieveDevMgrProps(domainname,devmgrname,propname)
        return_value = json.dumps(resp)
        self.write(return_value)

class Component(tornado.web.RequestHandler):
    def get(self, domainname, appname, compname):
        resp=domain.retrieveCompInfo(domainname,appname,compname)
        return_value = json.dumps(resp)
        self.write(return_value)


application = tornado.web.Application([
    (r"/", Main),
    (r"/static/(.*)", tornado.web.StaticFileHandler, {"path": cwd+"/static"}),
    (r"/domain", Domain),
    (r"/domain/", Domain),
    (r"/domain/([^/]+)/?", SingleDomainInfo),
    (r"/domain/([^/]+)/info/?", SingleDomainInfo),
    (r"/domain/([^/]+)/props/?", DomainProps),
    (r"/domain/([^/]+)/props/([^/]+)", SingleDomainProp),
    (r"/domain/([^/]+)/applications/?", Applications),
    (r"/domain/([^/]+)/applications/([^/]+)", Application),
    (r"/domain/([^/]+)/launch_app", LaunchApplication),
    (r"/domain/([^/]+)/release_app", ReleaseApplication),
    (r"/domain/([^/]+)/applications/([^/]+)/([^/]+)", Component),
    (r"/domain/([^/]+)/devicemanagers/?", DeviceManagers),
    (r"/domain/([^/]+)/devicemanagers/([^/]+)", DeviceManager),
    (r"/domain/([^/]+)/devicemanagers/([^/]+)/devs/([^/]+)", Device),
    (r"/domain/([^/]+)/devicemanagers/([^/]+)/devs/?", Devices),
    (r"/domain/([^/]+)/devicemanagers/([^/]+)/svcs/([^/]+)", Service),
    (r"/domain/([^/]+)/devicemanagers/([^/]+)/svcs/?", Services),
    (r"/domain/([^/]+)/devicemanagers/([^/]+)/props/([^/]+)", DevMgrProp),
    (r"/domain/([^/]+)/devicemanagers/([^/]+)/props/?", DevMgrProps),
    (r"/domain/([^/]+)/availableapps/?", AvailableApplications),
    (r"/odmEvents", OdmEvents),
])

domain.initialize(application)

if __name__ == '__main__':
    application.listen(8080)
    tornado.ioloop.IOLoop.instance().start()
    
