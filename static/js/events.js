//function EventMgr(object, element)
function EventMgr(object)
{
    this.message = function(data) {
        if (data !== "{}") {
            var resp = JSON.parse(data);
            if (resp.eventType == 'DomainManagementObjectAddedEventType') {
                if (resp.sourceCategory == 'DeviceManager') {
                    var event = new CustomEvent(
                            "DeviceManagerAdded",
                            {
                            detail: {
                                domainName: resp.domain,
                                devMgrName: resp.sourceName
                            },
                            bubbles: true,
                            cancelable: true
                            }
                        );
                } else if (resp.sourceCategory == 'Application') {
                    var event = new CustomEvent(
                            "ApplicationAdded",
                            {
                            detail: {
                                domainName: resp.domain,
                                appName: resp.sourceName
                            },
                            bubbles: true,
                            cancelable: true
                            }
                        );
                }
            }
            if (resp.eventType == 'DomainManagementObjectRemovedEventType') {
                if (resp.sourceCategory == 'DeviceManager') {
                    var event = new CustomEvent(
                            "DeviceManagerRemoved",
                            {
                            detail: {
                                domainName: resp.domain,
                                devMgrName: resp.sourceName
                            },
                            bubbles: true,
                            cancelable: true
                            }
                        );
                } else if (resp.sourceCategory == 'Application') {
                    var event = new CustomEvent(
                            "ApplicationRemoved",
                            {
                            detail: {
                                domainName: resp.domain,
                                appName: resp.sourceName
                            },
                            bubbles: true,
                            cancelable: true
                            }
                        );
                }
            }
            object.dispatchEvent(event);
        }
    };
};

function retrieveApps(callback)
{
    var apps_url = document.URL+"/applications/";
    $.getJSON(apps_url, callback)
}

function retrieveDevMgrs(callback)
{
    var devmgrs_url = document.URL+"/devicemanagers/";
    $.getJSON(devmgrs_url, callback)
}

function retrieveDevMgr(devmgr_id, callback)
{
    var devmgr_url = document.URL+"/devicemanagers/"+devmgr_id;
    $.getJSON(devmgr_url, callback)
}

function retrieveApp(app_id, callback)
{
    var app_url = document.URL+"/applications/"+app_id;
    $.getJSON(app_url, callback)
}

function launchApp(app_name, callback)
{
    var app_url = document.URL+"/launch_app?waveform="+app_name;
    $.getJSON(app_url, callback)
}

function retrieveDomMgr(callback)
{
    var dommgrinfo_url = document.URL+"/info/";
    $.getJSON(dommgrinfo_url, callback)
}

function retrieveAvailableApps(callback)
{
    var availableapps_url = document.URL+"/availableapps/";
    $.getJSON(availableapps_url, callback)
}

function retrieveDev(dev, devmgr_id, callback)
{
    var devmgrs_url = document.URL+"/devicemanagers/"+devmgr_id+"/"+dev;
    $.getJSON(devmgrs_url, callback)
}

function retrieveComp(comp, app_id, callback)
{
    var app_url = document.URL+"/applications/"+app_id+"/"+comp;
    $.getJSON(app_url, callback)
}

function cycleSource()
{
};

function DevMgrChange(object)
{
    var eMgr = new EventMgr(object);
    var ws = new WebSocket("ws://" + document.domain + ":5000/odmEvents");
    ws.onmessage = function(msg) {
        if (!msg)
            ws.close();
        else
            eMgr.message(msg.data);
    }
    window.onbeforeunload = function() {
        ws.close();
    }
};

function DevMgrChangeWS(html_tag_id)
{
    var eMgr = new EventMgr(html_tag_id);
    var source = new WebSocket("ws://"+document.domain+":5000/odmEvents");
    source.onmessage = function(event) {
        eMgr.message(event.data);
    };
};
