from ossie.utils import redhawk
from ossie.utils.redhawk.channels import IDMListener, ODMListener
import Queue
from ossie.cf import StandardEvent
import json

print 'importing domain.py'

global domMgr_ptr
global odmListener
global _app
global eventHandlers

def initialize(app):
    global domMgr_ptr
    global odmListener
    global _app
    global eventHandlers
    domMgr_ptr = None
    odmListener = None
    _app = app
    eventHandlers = []

def scan_domains():
    return redhawk.scan()

def json_to_eventsource(jsonmsg):
    content = jsonmsg.splitlines()
    msgout = ''
    for line in content:
        msgout += 'data: '+line+'\n'
    msgout += '\n'
    return msgout

def json_to_websocket(jsonmsg):
    return jsonmsg

def json_to_string(jsonmsg):
    content = jsonmsg
    return content

def createJsonMsg(msg):
    jsonmsg = json.dumps(msg)
    return jsonmsg

def getCategory(sourceCategory):
    category = ''
    if sourceCategory == StandardEvent.DEVICE_MANAGER:
        category = 'DeviceManager'
    elif sourceCategory == StandardEvent.DEVICE:
        category = 'Device'
    elif sourceCategory == StandardEvent.APPLICATION:
        category = 'Application'
    elif sourceCategory == StandardEvent.APPLICATION_FACTORY:
        category = 'ApplicationFactory'
    return category

def odmResponse(event):
    global eventHandlers
    for eventH in eventHandlers:
        eventH.event_queue.put(event)
    
class odmStreamHandler:
    def __init__(self, socket_handler):
        global eventHandlers
        self.socket_handler = socket_handler
        self.event_queue = Queue.Queue()
        self.exitCondition = False
        eventHandlers.append(self)
    
    def thread_function(self):
        global _app
        while(not self.exitCondition):
            try:
                data = self.event_queue.get(timeout=1)
                if isinstance(data, StandardEvent.DomainManagementObjectAddedEventType):
                    category = getCategory(data.sourceCategory)
                    jsonmsg = createJsonMsg({'eventType':'DomainManagementObjectAddedEventType','domain':domMgr_ptr.name,'sourceCategory':category,'sourceName':data.sourceName,'sourceId':data.sourceId})
                    msg = json_to_websocket(jsonmsg)
                elif isinstance(data, StandardEvent.DomainManagementObjectRemovedEventType):
                    category = getCategory(data.sourceCategory)
                    jsonmsg = createJsonMsg({'eventType':'DomainManagementObjectRemovedEventType','domain':domMgr_ptr.name,'sourceCategory':category,'sourceName':data.sourceName,'sourceId':data.sourceId})
                    msg = json_to_websocket(jsonmsg)
                else:
                    jsonmsg = createJsonMsg({})
                    msg = json_to_websocket(jsonmsg)
            except Exception, e:
                jsonmsg = createJsonMsg({})
                msg = json_to_websocket(jsonmsg)
            if not self.exitCondition:
                self.socket_handler.write_message(msg)
                
    def closeOdmStream(self):
        global eventHandlers
        for idx in range(len(eventHandlers)):
            if eventHandlers[idx]==self:
                eventHandlers.pop(idx)
                break
        self.exitCondition = True
        
def connectODM_listener():
    global odmListener
    odmListener = ODMListener()
    odmListener.connect(domMgr_ptr)
    odmListener.deviceManagerAdded.addListener(odmResponse)
    odmListener.deviceManagerRemoved.addListener(odmResponse)
    odmListener.applicationAdded.addListener(odmResponse)
    odmListener.applicationRemoved.addListener(odmResponse)

def establishDomain(name):
    global domMgr_ptr
    redhawk.setTrackApps(False)
    domMgr_ptr = redhawk.attach(name)
    connectODM_listener()

def retrieveDevMgrInfo(domainname, devMgrName):
    global domMgr_ptr
    for devMgr in domMgr_ptr.devMgrs:
        if devMgr.name == devMgrName:
            ret_dict=[{'devMgrName':devMgrName}]
            for dev in devMgr.devs:
                ret_dict.append({'dev':{"name":dev.name,"id":dev._id}})
            for svc in devMgr.services:
                ret_dict.append({'svc':{"name":svc.name,"id":svc._id}})
            msg_json = createJsonMsg({'devMgr':ret_dict})
            return msg_json
    return '{}'

def retrieveAppInfo(domainname, appName):
    global domMgr_ptr
    for app in domMgr_ptr.apps:
        if app.name == appName:
            ret_dict=[{'appName':appName}]
            for comp in app.comps:
                ret_dict.append({'comp':{"name":comp.name,"id":comp._id}})
            for prop in app._properties:
                ret_dict.append({'prop':{"name":prop.clean_name,"value":str(prop.queryValue())}})
            for port in app.ports:
                ret_dict.append({'port':port.name})
            msg_json = createJsonMsg({'app':ret_dict})
            return msg_json
    return '{}'

def launchApp(domainname, appName):
    global domMgr_ptr
    ret_dict=[]
    try:
        app = domMgr_ptr.createApplication(str(appName))
        ret_dict.append({'appName':app.name})
    except Exception, e:
        ret_dict.append({'error':e})
    ret_dict_full = {'app':ret_dict}
    msg_json = createJsonMsg(ret_dict_full)
    return msg_json

def releaseApp(domainname, appId):
    global domMgr_ptr
    ret_dict=[{}]
    try:
        apps = domMgr_ptr.apps
        for app in apps:
            if app.name == appId:
                app.releaseObject()
                break
    except Exception, e:
        ret_dict.append({'error':e})
    ret_dict_full = {'app':ret_dict}
    msg_json = createJsonMsg(ret_dict_full)
    return msg_json

def retrieveDevInfo(domainname, devMgrName, devId):
    global domMgr_ptr
    for devMgr in domMgr_ptr.devMgrs:
        if devMgr.name == devMgrName:
            for dev in devMgr.devs:
                if dev._id == devId:
                    ret_dict=[{'devName':dev.name}]
                    ret_dict=[{'devId':dev._id}]
                    for prop in dev._properties:
                        ret_dict.append({'prop':{"name":prop.clean_name,"value":str(prop.queryValue())}})
                    for port in dev.ports:
                        ret_dict.append({'port':port.name})
                    msg_json = createJsonMsg({'dev':ret_dict})
                    return msg_json
    return '{}'

def retrieveDevs(domainname, devMgrName):
    global domMgr_ptr
    for devMgr in domMgr_ptr.devMgrs:
        if devMgr.name == devMgrName:
            for dev in devMgr.devs:
                ret_dict=[{'devName':dev.name}]
                ret_dict.append({'devId':dev._id})
                msg_json = createJsonMsg({'dev':ret_dict})
                return msg_json
    return '{}'

def retrieveCompInfo(domainname, appName, compId):
    global domMgr_ptr
    for app in domMgr_ptr.apps:
        if app.name == appName:
            for comp in app.comps:
                if comp._id == compId:
                    ret_dict=[{'compName':comp.name}]
                    ret_dict=[{'compId':comp._id}]
                    for prop in comp._properties:
                        ret_dict.append({'prop':{"name":prop.clean_name,"value":str(prop.queryValue())}})
                    for port in comp.ports:
                        ret_dict.append({'port':port.name})
                    msg_json = createJsonMsg({'comp':ret_dict})
                    return msg_json
    return '{}'

def retrieveDevMgrs(domainname):
    global domMgr_ptr
    if domMgr_ptr == None:
        return '{}'
    if domMgr_ptr.name != domainname:
        return '{}'
    devmgrs=domMgr_ptr.devMgrs
    devmgrs_dict = []
    for devmgr in devmgrs:
        devmgrs_dict.append({'devMgrName':devmgr.name})
    msg_json = createJsonMsg({'deviceManagers':devmgrs_dict})
    return msg_json

def retrieveApps(domainname):
    global domMgr_ptr
    if domMgr_ptr == None:
        return '{}'
    if domMgr_ptr.name != domainname:
        return '{}'
    apps=domMgr_ptr.apps
    apps_dict = []
    for app in apps:
        apps_dict.append({'name':app.name})
    msg_json = createJsonMsg({'applications':apps_dict})
    return msg_json

def retrieveAvailableApps(domainname):
    global domMgr_ptr
    if domMgr_ptr == None:
        return '{}'
    if domMgr_ptr.name != domainname:
        return '{}'
    sadsfullpath = domMgr_ptr.catalogSads()
    sads = domMgr_ptr._sads
    sad_ret = []
    for idx in range(len(sads)):
        sad_ret.append({'name':sads[idx],'sad':sadsfullpath[idx]})
    msg_json = createJsonMsg({'availableApps':sad_ret})
    return msg_json

def retrieveDomMgrInfo(domainname):
    global domMgr_ptr
    domain_name = str(domainname)
    connectToDomain(domainname)
    if domain_name == domMgr_ptr.ref._get_name():
        ret_dict=[{'domMgrName':domain_name}]
        props = domMgr_ptr.query([])
        for prop in props:
            ret_dict.append({'prop':{"name":prop.id,"value":str(prop.value._v)}})
        msg_json = createJsonMsg({'domMgr':ret_dict})
        return msg_json
    return '{}'

def connectToDomain(domainname):
    global domMgr_ptr
    domain_name = str(domainname)
    if domMgr_ptr == None:
        establishDomain(domain_name)
        return domMgr_ptr
    try:
        if domain_name == domMgr_ptr.ref._get_name():
            return domMgr_ptr
    except:
        pass
    establishDomain(domain_name)
    return domMgr_ptr
