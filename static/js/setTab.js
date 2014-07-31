
function setDomain(el, domain_name){
    $(el).append('<div id="tab_container" class="container"/>');
    $('#tab_container',el).append('<div id="tab_content">');
    $('#tab_content',el).append('<ul id="tabs" class="nav nav-tabs" data-tabs="tabs"/>');
    $('#tabs',el).append('<li class="active"><a id="DomainName" href="#red" data-toggle="tab">'+domain_name+'</a></li>');
    $('#tab_content',el).append('<div id="domainTab" class="tab-content">');
    var domainmanager_accordion = new DomMgrView({group_id:"domainManager_acc", modgroup_id:"domainManager_acc",level:1,group_type:"domainmanager",
        color:"primary",classname:"panel-collapse_domainMgr",visible_text:"Domain Manager"});
    $('#domainTab',el).append(domainmanager_accordion.render().el);
    domMgrAccordion(domainmanager_accordion.widget.find("#domainManager_acc"));
    var devicemanager_accordion = new DevMgrsView({group_id:"deviceManagers_acc", modgroup_id:"deviceManagers_acc",level:1,group_type:"devicemanagers",
        color:"primary",classname:"panel-collapse_devMgrs",visible_text:"Device Managers"});
    $('#domainTab',el).append(devicemanager_accordion.render().el);
    var applications_accordion = new AccordionView({group_id:"applications_acc", modgroup_id:"applications_acc",level:1,group_type:"applications",
        color:"primary",classname:"panel-collapse_applications",visible_text:"Applications"});
    $('#domainTab',el).append(applications_accordion.render().el);
};

/*      <div class="btn-group" id="dropdown-applications">
        <button type="button" data-toggle="dropdown" class="btn btn-primary dropdown-toggle">Launch Application <span class="caret"></span></button>
        <ul class="dropdown-menu" id="dropdown-applications_list">
        </ul>
      </div>
*/
