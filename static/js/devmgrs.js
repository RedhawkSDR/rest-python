
var DomMgrView = AccordionView.extend({
    show: function() {
        console.log('show domain manager');
    },
    hide: function() {
        console.log('hide show domain manager');
    }
});

var PropsView = AccordionView.extend({
    show: function() {
        console.log('show properties');
        retrieveDomMgr(function(data){
            var domain_resp = JSON.parse(data);
            //addSubstructure(domain_resp.domMgr, "prop", document.getElementById("DomainManagerprops"),"name","value")
            var dommgrprops = $("#DomainManagerprops");
            addSubstructure(domain_resp.domMgr, "prop", $("#DomainManagerprops"),"name","value")
        });
    },
    hide: function() {
        console.log('hide properties');
    }
});

function domMgrAccordion(domMgr_element)
{
    var accordion_props = new PropsView({group_id:"DomainManagerprops", modgroup_id:"DomainManagerprops",level:2,group_type:"props",
        color:"default",classname:"panel-collapseSingleEntity",visible_text:"Properties"});
    domMgr_element.append(accordion_props.render().el);
};

function addToAccordion(json_msg,parent_element,item_id_key,item_name_key,addAccordion_callback)
{
    var item_iter = parent_element.childNodes;
    for (var json_idx in json_msg) {
        var item_id = json_msg[json_idx][item_id_key];
        var item_name = json_msg[json_idx][item_name_key];
        var foundItem = isItemInAccordionDiv(item_id,item_iter);
        if (foundItem == true) {
            continue;
        }
        var item_element = addAccordion_callback(item_id,item_name);
        parent_element.appendChild(item_element);
    }
}

function addSubstructure(object_array, attribute_name, parent_element,attribute_id,attribute_value)
{
    console.log('begin');
    var par_el = parent_element[0];
    var child_iter = par_el.childNodes;
    var foundItem = false;
    for (var child_idx=0; child_idx<child_iter.length; child_idx++) {
        if (child_iter[child_idx].hasAttribute("data-table_id")) {
            if (child_iter[child_idx].getAttribute("data-table_id") == attribute_name) {
                foundItem = true;
                break;
            }
        }
    }
    if (!foundItem) {
        var struct = [];
        for (var idx in object_array) {
            if (typeof(object_array[idx][attribute_name]) == 'undefined') {
                continue;
            }
            if ((attribute_id == "")&&(attribute_value == "undefined")) {
                struct.push({prop_id:object_array[idx][attribute_name],prop_value:''})
            } else {
                struct.push({prop_id:object_array[idx][attribute_name][attribute_id],prop_value:object_array[idx][attribute_name][attribute_value]})
            }
        }
        /*var table = createTable(struct,attribute_name);
        parent_element.appendChild(table);*/
        console.log('the length of the structure is: '+struct.length);
        var table = new PropertiesView({idvalues:struct,table_id:attribute_name,object_url:document.URL});
        parent_element.append(table.render().el);
    } else {
        for (var idx in object_array) {
            if (typeof(object_array[idx][attribute_name]) == 'undefined') {
                continue;
            }
            var contained_data_id = "";
            var contained_data = "";
            if ((attribute_id == "")&&(attribute_value == "undefined")) {
                contained_data_id = object_array[idx][attribute_name];
            } else {
                contained_data_id = object_array[idx][attribute_name][attribute_id];
                contained_data = object_array[idx][attribute_name][attribute_value];
            }
            var sub_iter = child_iter[child_idx].childNodes;
            for (var sub_idx=0;sub_idx<sub_iter.length;sub_idx++) {
                if (sub_iter[sub_idx].hasAttribute("data-contained_data_id")) {
                    if (sub_iter[sub_idx].getAttribute("data-contained_data_id") == contained_data_id) {
                        var value_iter = sub_iter[sub_idx].childNodes;
                        for (var value_idx=0;value_idx<value_iter.length;value_idx++) {
                            if (hasClass(value_iter[value_idx], "val_col")) {
                                value_iter[value_idx].innerHTML = contained_data
                                break;
                            }
                        }
                    }
                }
            }
        }
    }
}

function cleanAccordion(json_msg,parent_element,item_id_key,item_name_key,addAccordion_callback)
{
    var item_iter = parent_element.childNodes;
    for (var iter_idx=0;iter_idx<item_iter.length;iter_idx++) {
        var foundItem = false;
        for (var json_idx=0;json_idx<json_msg.length; json_idx++) {
            var item_id = json_msg[json_idx][item_id_key];
            if (item_iter[iter_idx].hasAttribute("data-group_id")) {
                if (item_iter[iter_idx].getAttribute("data-group_id") == item_id) {
                    foundItem = true;
                    break;
                }
            }
        }
        if (foundItem == false) {
            parent_element.removeChild(item_iter[iter_idx]);
        }
    }
}

function removeFromAccordion(parent_element,attr_name)
{
    var sub_elements = parent_element.childNodes;
    for (i=0; i<sub_elements.length; i++) {
        if (sub_elements[i] instanceof HTMLDivElement) {
            if (sub_elements[i].hasAttribute("data-group_id")) {
                if (sub_elements[i].getAttribute("data-group_id") == attr_name) {
                    parent_element.removeChild(sub_elements[i]);
                    break;
                }
            }
        }
    }
}

function releaseApplication(e)
{
    releaseApp(e.target.getAttribute("data-application_id"),function(data){
        return false;
        }
    );
}

function appAccordion(group_id, child)
{
    var modgroup_id = group_id.replace(/\./g,"_");
    var accordion = accordionElement(group_id, modgroup_id,3,"App","default","panel-collapseSingleEntity");
    accordion.find("#group_anchor_"+modgroup_id).html(child);
    
    var releaseButton = $('<button class="btn btn-sm btn-default" data-application_id="'+group_id+'"/>');
    releaseButton.onclick = releaseApplication;
    releaseButton.innerHTML = "Release application";
    accordion.find("#"+modgroup_id).append(releaseButton);
    var sub_accordion_comps = accordionElement(group_id+"comps",modgroup_id+"comps",2,"comps","default","panel-collapseSingleEntity");
    sub_accordion_comps.find("#group_anchor_"+modgroup_id+"comps").html("Components");
    accordion.find("#"+modgroup_id).append(sub_accordion_comps);
    var sub_accordion_ports = accordionElement(group_id+"ports",modgroup_id+"ports",2,"ports","default","panel-collapseSingleEntity");
    sub_accordion_ports.find("#group_anchor_"+modgroup_id+"ports").html("Ports");
    accordion.find("#"+modgroup_id).append(sub_accordion_ports);
    var sub_accordion_props = accordionElement(group_id+"props",modgroup_id+"props",2,"props","default","panel-collapseSingleEntity");
    sub_accordion_props.find("#group_anchor_"+modgroup_id+"props").html("Properties");
    accordion.find("#"+modgroup_id).append(sub_accordion_props);
    return accordion;
};

function devMgrAccordion(group_id, child)
{
    var modgroup_id = group_id.replace(/\./g,"_");
    var accordion = accordionElement(group_id, modgroup_id,3,"devMgr","default","panel-collapseSingleEntity");
    accordion.find("#group_anchor_"+modgroup_id).html(child);
    
    var sub_accordion_devs = accordionElement(group_id+"devs",modgroup_id+"devs",2,"devs","default","panel-collapseSingleEntity");
    sub_accordion_devs.find("#group_anchor_"+modgroup_id+"devs").html("Devices");
    accordion.find("#"+modgroup_id).appendChild(sub_accordion_devs);
    var sub_accordion_svcs = accordionElement(group_id+"svcs",modgroup_id+"svcs",2,"svcs","default","panel-collapseSingleEntity");
    sub_accordion_svcs.find("#group_anchor_"+modgroup_id+"svcs").html("Services");
    accordion.find("#"+modgroup_id).appendChild(sub_accordion_svcs);
    var sub_accordion_props = accordionElement(group_id+"props",modgroup_id+"props",2,"props","default","panel-collapseSingleEntity");
    sub_accordion_props.find("#group_anchor_"+modgroup_id+"props").html("Properties");
    accordion.find("#"+modgroup_id).appendChild(sub_accordion_props);
    return accordion;
};

function domMgrRightClick(domMgr_element,menu_id)
{
    var div_1 = document.createElement("div");
    div_1.id = menu_id;
    div_1.className = "hide";
    var ul_1 = document.createElement("ul");
    var li_1 = document.createElement("li");
    var li_2 = document.createElement("li");
    a_1 = document.createElement("a");
    a_1.setAttribute("href", "www.google.com");
    a_1.innerHTML = "link 1";
    li_1.appendChild(a_1);
    a_2 = document.createElement("a");
    a_2.setAttribute("href", "www.google.com");
    a_2.innerHTML = "link 2";
    li_2.appendChild(a_2);
    ul_1.appendChild(li_1);
    ul_1.appendChild(li_2);
    div_1.appendChild(ul_1);
    domMgr_element.appendChild(div_1);
}

function hasClass(element, cls) {
    return (' ' + element.className + ' ').indexOf(' ' + cls + ' ') > -1;
}

function itemAccordion(group_id, child, item_type)
{
    var modgroup_id = group_id.replace(/[\.:]/g,"_");
    var accordion = accordionElement(group_id, modgroup_id,2,item_type,"default","panel-collapseSingleEntity");
    accordion.find("#group_anchor_"+modgroup_id).html(child);
    
    var sub_accordion_props = accordionElement(group_id+"props",modgroup_id+"props",2,"props","default","panel-collapseSingleEntity");
    sub_accordion_props.find("#group_anchor_"+modgroup_id+"props").html("Properties");
    accordion.find("#"+modgroup_id).appendChild(sub_accordion_props);
    var sub_accordion_ports = accordionElement(group_id+"ports",modgroup_id+"ports",2,"ports","default","panel-collapseSingleEntity");
    sub_accordion_ports.find("#group_anchor_"+modgroup_id+"ports").html("Ports");
    accordion.find("#"+modgroup_id).appendChild(sub_accordion_ports);
    return accordion;
}

function isItemInAccordionDiv(item, div_iter) {
    var foundItem = false;
    for (var j=0; j<div_iter.length; j++) {
        if (div_iter[j] instanceof HTMLDivElement) {
            if (div_iter[j].hasAttribute("data-group_id")) {
                if (item == div_iter[j].getAttribute("data-group_id")) {
                    foundItem = true;
                    break;
                }
            }
        }
    }
    return foundItem;
};

function getGroupingFromAccordion(Mgr_id, Mgr_iter)
{
    var Mgr_to_retrieve = '';
    if ((document.getElementById(Mgr_id).getAttribute("data-group_type") != 'devMgr')&&(document.getElementById(Mgr_id).getAttribute("data-group_type") != 'App')) {
        return ['undefined',Mgr_to_retrieve,'undefined','undefined','undefined'];
    }
    for (var i=0; i<Mgr_iter.length; i++) {
        if (typeof(Mgr_iter[i].id) != 'undefined') {
            var Mgr_iter_level_2 = document.getElementById(Mgr_iter[i].id).childNodes;
            var Mgr_iter_level_3 = Mgr_iter_level_2[0].childNodes;
            for (var j=0; j<Mgr_iter_level_3.length; j++) {
                if (typeof(Mgr_iter_level_3[j].id) != 'undefined') {
                    var test_id = Mgr_iter_level_3[j].id;
                    if (Mgr_id == test_id) {
                        Mgr_to_retrieve = Mgr_iter_level_3[j].getAttribute("data-redhawk_id");
                        break;
                    }
                }
            }
            if (Mgr_to_retrieve == '') {
                continue;
            }
            var dev=0;
            var svcs=0;
            var props=0;
            var Mgr_iter_level_4 = Mgr_iter_level_3[j].childNodes;
            for (iter=0; iter<Mgr_iter_level_4.length; iter++) {
                if ((Mgr_iter_level_4[iter].getAttribute("data-group_type")=="devs")||(Mgr_iter_level_4[iter].getAttribute("data-group_type")=="comps")) {
                    dev=iter;
                } else if ((Mgr_iter_level_4[iter].getAttribute("data-group_type")=="svcs")||(Mgr_iter_level_4[iter].getAttribute("data-group_type")=="ports")) {
                    svcs=iter;
                } else if (Mgr_iter_level_4[iter].getAttribute("data-group_type")=="props") {
                    props=iter;
                }
            }
            break;
        }
    }
    if (Mgr_to_retrieve == '') {
        return ['undefined',Mgr_to_retrieve,'undefined','undefined','undefined'];
    }
    return [Mgr_iter_level_3[j],Mgr_to_retrieve,Mgr_iter_level_4[dev],Mgr_iter_level_4[svcs],Mgr_iter_level_4[props]];
};

function getGroupItemsFromAccordion(devmgr_dev_id, devMgr_iter)
{
    var devs = document.getElementById(devmgr_dev_id).childNodes;
    return devs;
}

function getItemFromAccordion(dev_id, devMgr_iter)
{
    if (document.getElementById(dev_id)==null) {
        return ['undefined',attr,'undefined','undefined','undefined','undefined'];
    }
    if (!document.getElementById(dev_id).hasAttribute("data-group_type")) {
        return ['undefined',attr,'undefined','undefined','undefined','undefined'];
    }
    var attr = '';
    var devmgr_id = '';
    var devmgr_modid = '';
    var modgroup_id = dev_id.replace(/\./g,"_");
    var dev_element = document.getElementById(modgroup_id)
    if (dev_element == 'undefined') {
        return ['undefined',attr,'undefined','undefined','undefined','undefined'];
    }
    var attr = dev_element.getAttribute("data-redhawk_id");
    if (attr == '') {
        return ['undefined',attr,'undefined','undefined','undefined','undefined'];
    }
    var props=0;
    var ports=0;
    var dev_element_sub = dev_element.childNodes;
    for (var iter=0; iter<dev_element_sub.length; iter++) {
        if (dev_element_sub[iter].getAttribute("data-group_type")=="props") {
            props=iter;
        } else if (dev_element_sub[iter].getAttribute("data-group_type")=="ports") {
            ports=iter;
        }
    }
    devmgr_id = getNodeElementFromChildElement(dev_element).getAttribute("data-group_id");
    devmgr_modid = getNodeElementFromChildElement(dev_element).getAttribute("data-modgroup_id");
    return [dev_element, attr, devmgr_id, devmgr_modid, dev_element_sub[props], dev_element_sub[ports]];
};

function getNodeElementFromChildElement(child)
{
    return child.parentElement.parentElement.parentElement.parentElement.parentElement.parentElement.parentElement.parentElement
};

function retrieveFunctionName(callee)
{
    return callee.substr('function '.length).substr(0,callee.substr('function '.length).indexOf('('))
};
