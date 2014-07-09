function devMgrAccordionHtml(group_id,item_id)
{
    document.write('\
      <div class="panel-group" id="'+group_id+'">    \
        <div class="panel panel-default">           \
          <div class="panel-heading">               \
            <h4 class="panel-title">                \
              <a data-toggle="collapse" data-parent="#accordion" href="#'+item_id+'">item</a> \
            </h4>   \
          </div>    \
          <div id="'+item_id+'" class="panel-collapse collapse">    \
            <li><a href="#">bar</a></li>  \
            <li><a href="#">Another action</a></li> \
            <li><a href="#">Separated link</a></li> \
          </div>    \
        </div>  \
      </div>    \
    ');
};

function makeid()
{
    var text = "";
    var possible = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz";

    for( var i=0; i < 10; i++ )
        text += possible.charAt(Math.floor(Math.random() * possible.length));

    return text;
};

function accordionElement(group_id, modgroup_id, level, group_type, color, classname)
{
    var rnd_id = makeid();
    var div_1 = document.createElement("div");
    div_1.id = rnd_id;
    div_1.className = "panel-group";
    div_1.setAttribute("data-group_id",group_id);
    div_1.setAttribute("data-modgroup_id",modgroup_id);
    div_1.setAttribute("data-group_type",group_type);
    var div_2 = document.createElement("div");
    div_2.className = "panel panel-"+color+" offset-x1";
    div_1.appendChild(div_2);
    var div_3 = document.createElement("div");
    div_3.className = "panel-heading";
    div_2.appendChild(div_3);
    var h_1 = document.createElement("h"+level);
    h_1.className = "panel-title";
    div_3.appendChild(h_1);
    var a_1 = document.createElement("a");
    a_1.setAttribute("data-toggle", "collapse");
    a_1.setAttribute("data-parent", "#accordion");
    a_1.setAttribute("href", "#"+modgroup_id);
    h_1.appendChild(a_1);
    var div_5 = document.createElement("div");
    div_5.id = modgroup_id;
    div_5.setAttribute("data-redhawk_id", group_id);
    div_5.className = classname+" collapse";
    div_5.setAttribute("data-group_type",group_type);
    div_2.appendChild(div_5);
    return {div_1:div_1, a_1:a_1, div_5:div_5, div_3:div_3};
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
    var table = createTable(struct);
    parent_element.appendChild(table);
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
    console.log('.....invoking remove');
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

function appAccordion(group_id, child)
{
    var modgroup_id = group_id.replace(/\./g,"_");
    var accordion = accordionElement(group_id, modgroup_id,3,"App","default","panel-collapseSingleEntity");
    accordion.a_1.innerHTML=child;
    
    var sub_accordion_comps = accordionElement(group_id+"comps",modgroup_id+"comps",2,"comps","default","panel-collapseSingleEntity");
    sub_accordion_comps.a_1.innerHTML="Components";
    accordion.div_5.appendChild(sub_accordion_comps.div_1);
    var sub_accordion_ports = accordionElement(group_id+"ports",modgroup_id+"ports",2,"ports","default","panel-collapseSingleEntity");
    sub_accordion_ports.a_1.innerHTML="Ports";
    accordion.div_5.appendChild(sub_accordion_ports.div_1);
    var sub_accordion_props = accordionElement(group_id+"props",modgroup_id+"props",2,"props","default","panel-collapseSingleEntity");
    sub_accordion_props.a_1.innerHTML="Properties";
    accordion.div_5.appendChild(sub_accordion_props.div_1);
    return accordion.div_1;
};

function devMgrAccordion(group_id, child)
{
    var modgroup_id = group_id.replace(/\./g,"_");
    var accordion = accordionElement(group_id, modgroup_id,3,"devMgr","default","panel-collapseSingleEntity");
    accordion.a_1.innerHTML=child;
    
    var sub_accordion_devs = accordionElement(group_id+"devs",modgroup_id+"devs",2,"devs","default","panel-collapseSingleEntity");
    sub_accordion_devs.a_1.innerHTML="Devices";
    accordion.div_5.appendChild(sub_accordion_devs.div_1);
    var sub_accordion_svcs = accordionElement(group_id+"svcs",modgroup_id+"svcs",2,"svcs","default","panel-collapseSingleEntity");
    sub_accordion_svcs.a_1.innerHTML="Services";
    accordion.div_5.appendChild(sub_accordion_svcs.div_1);
    var sub_accordion_props = accordionElement(group_id+"props",modgroup_id+"props",2,"props","default","panel-collapseSingleEntity");
    sub_accordion_props.a_1.innerHTML="Properties";
    accordion.div_5.appendChild(sub_accordion_props.div_1);
    return accordion.div_1;
};

function domMgrAccordion(domMgr_element)
{
    var accordion_props = accordionElement("DomainManagerprops","DomainManagerprops",2,"props","default","panel-collapseSingleEntity");
    accordion_props.a_1.innerHTML="Properties";
    domMgr_element.appendChild(accordion_props.div_1);
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

function launchApplication()
{
    console.log('.............. launch application');
}

function createTable(idvalues)
{
    var container = document.createElement("div");
    for (idx=0;idx<idvalues.length;idx++) {
        var row_1 = document.createElement("div");
        row_1.className = "row offset-x1";
        var col_1 = document.createElement("div");
        col_1.className = "col-xs-6 col-md-4";
        col_1.innerHTML=idvalues[idx].prop_id;
        var col_2 = document.createElement("div");
        col_2.className = "col-xs-6 col-md-4";
        col_2.contenteditable=true;
        col_2.innerHTML=idvalues[idx].prop_value;
        row_1.appendChild(col_1);
        row_1.appendChild(col_2);
        container.appendChild(row_1);
    }
    return container;
}

function itemAccordion(group_id, child, item_type)
{
    var modgroup_id = group_id.replace(/[\.:]/g,"_");
    var accordion = accordionElement(group_id, modgroup_id,2,item_type,"default","panel-collapseSingleEntity");
    accordion.a_1.innerHTML=child;
    
    var sub_accordion_props = accordionElement(group_id+"props",modgroup_id+"props",2,"props","default","panel-collapseSingleEntity");
    sub_accordion_props.a_1.innerHTML="Properties";
    accordion.div_5.appendChild(sub_accordion_props.div_1);
    var sub_accordion_ports = accordionElement(group_id+"ports",modgroup_id+"ports",2,"ports","default","panel-collapseSingleEntity");
    sub_accordion_ports.a_1.innerHTML="Ports";
    accordion.div_5.appendChild(sub_accordion_ports.div_1);
    return accordion.div_1;
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
