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

function onBlursupport(e) { // blur is 'leaving focus' in html
    console.log(e.target.innerHTML);
}

function accordionElement(group_id, modgroup_id, level, group_type, color, classname,visible_text)
{
    var div_1 = $('<div id="group_parent_'+modgroup_id+'" class="panel-group" data-group_id="'+group_id+'" data-modgroup_id="'+modgroup_id+'" data-group_type="'+group_type+'"/>');
    var div_2 = $('<div class="panel panel-'+color+' offset-x1"/>');
    $(div_1).append(div_2);
    var div_3 = $('<div class="panel-heading"/>');
    $(div_2).append(div_3);
    var h_1 = $('<h'+level+' class="panel-title"/>');
    $(div_3).append(h_1);
    var anchor_id = "group_anchor_"+modgroup_id
    var a_1 = $('<a id="'+anchor_id+'" data-toggle="collapse" data-parent="#accordion" href="#'+modgroup_id+'"/>');
    a_1.html(visible_text);
    $(h_1).append(a_1);
    var div_5 = $('<div id="'+modgroup_id+'" class="'+classname+' collapse" data-redhawk_id="'+group_id+'" data-group_type="'+group_type+'"/>');
    $(div_2).append(div_5);
    return div_1;
};

var AccordionView = Backbone.View.extend({
    tagName: 'div',
    events: {
        'show.bs.collapse': 'show',
        'hide.bs.collapse': 'hide'
    },
    initialize: function(options){
      if (typeof(options.group_id) == "undefined") {
        console.log("group_id needs to be passed as an argument");
      }
      if (typeof(options.modgroup_id) == "undefined") {
        console.log("modgroup_id needs to be passed as an argument");
      }
      if (typeof(options.level) == "undefined") {
        console.log("level needs to be passed as an argument");
      }
      if (typeof(options.group_type) == "undefined") {
        console.log("group_type needs to be passed as an argument");
      }
      if (typeof(options.color) == "undefined") {
        console.log("color needs to be passed as an argument");
      }
      if (typeof(options.classname) == "undefined") {
        console.log("classname needs to be passed as an argument");
      }
      if (typeof(options.visible_text) == "undefined") {
        console.log("text needs to be passed as an argument");
      }
      this.group_id = options.group_id;
      this.modgroup_id = options.modgroup_id;
      this.level = options.level;
      this.group_type = options.group_type;
      this.color = options.color;
      this.classname = options.classname;
      this.visible_text = options.visible_text;
      this.widget = null;
      _.bindAll(this, 'render'); // fixes loss of context for 'this' within methods
      
      this.derived_initialize(options);

      this.render(); // not all views are self-rendering. This one is.
    },
    derived_initialize: function(options) {
    },
    show: function() {
        console.log('show inside the view');
    },
    hide: function() {
        console.log('hide inside the view');
    },

    render: function(){
        console.log('.......................... rendering',this.group_id);
        if (this.widget == null) {
            this.widget = accordionElement(this.group_id,this.modgroup_id,this.level,this.group_type,this.color,this.classname,this.visible_text);
            $(this.el).append(this.widget);
        }
        return this;
    }
});

function createTable(idvalues, table_id)
{
    var container = $('<div data-table_id="'+table_id+'"/>');
    for (idx=0;idx<idvalues.length;idx++) {
        var row_1 = $('<div class="row offset-x1 data-contained_data_id="'+idvalues[idx].prop_id+'"/>');
        var col_1 = $('<div class="col-xs-6 col-md-4 id_col"/>');
        col_1.html(idvalues[idx].prop_id);
        var col_2 = $('<div class="col-xs-6 col-md-4 val_col" contentEditable="true" contenteditable="true"/>');
        col_2.html(idvalues[idx].prop_value);
        row_1.append(col_1);
        row_1.append(col_2);
        container.append(row_1);
    }
    return container;
};

var DevMgrView = AccordionView.extend({
    /*show: function(e) {
        if (e.target.id != this.modgroup_id) {
            return;
        }
        console.log('show device manager');
        retrieveDevMgr(this.group_id, function(data){
            var domain = JSON.parse(data);
            console.log(domain);
            for (var idx in domain.domain) {
                console.log(domain.domain[idx]);
            }
            //addToAccordion(domain.domain,document.getElementById("deviceManagers_acc"),"devMgrName","devMgrName",devMgrAccordion);
            //cleanAccordion(domain.domain,document.getElementById("deviceManagers_acc"),"devMgrName","devMgrName",devMgrAccordion);
        });
    },
    hide: function(e) {
        if (e.target.id != this.modgroup_id) {
            return;
        }
        console.log('hide show device manager');
    },*/
    render: function(){
        if (this.widget == null) {
            this.widget = accordionElement(this.group_id,this.modgroup_id,this.level,this.group_type,this.color,this.classname,this.visible_text);
            $(this.el).append(this.widget);
            var accordion_props = new DevMgrDevsView({group_id:this.group_id+"devs", modgroup_id:this.modgroup_id+"devs",level:2,group_type:"devs",
                color:"default",classname:"panel-collapseSingleEntity",visible_text:"Devices"});
            this.widget.find("#"+this.modgroup_id).append(accordion_props.render().el);
            var accordion_props = new DevMgrSvcsView({group_id:this.group_id+"svcs", modgroup_id:this.modgroup_id+"svcs",level:2,group_type:"svcs",
                color:"default",classname:"panel-collapseSingleEntity",visible_text:"Services"});
            this.widget.find("#"+this.modgroup_id).append(accordion_props.render().el);
            var accordion_props = new DevMgrPropsView({group_id:this.group_id+"props", modgroup_id:this.modgroup_id+"props",level:2,group_type:"props",
                color:"default",classname:"panel-collapseSingleEntity",visible_text:"Properties"});
            this.widget.find("#"+this.modgroup_id).append(accordion_props.render().el);
        }
        return this;
    }
});

var DevMgrsView = AccordionView.extend({
    derived_initialize: function(options) {
        this.devMgrs = new DeviceManagerList();
        this.listenTo(this.devMgrs,"update_view",this.updateView);
    },
    updateView: function(ret_models) {
        devmgrs_el = $('#deviceManagers_acc');
        model_mod_ids = [];
        _(ret_models).each(function(item){
            var group_id = item.id;
            var modgroup_id = group_id.replace(/\./g,"_");
            model_mod_ids.push(modgroup_id);
            if (($('#'+modgroup_id,this.widget)).length == 0) {
                var devmgr = new DevMgrView({group_id:group_id, modgroup_id:modgroup_id,level:3,group_type:"devMgr",
                    color:"default",classname:"panel-collapseSingleEntity",visible_text:group_id});
                devmgrs_el.append(devmgr.render().el);
            }
        })
        el_to_remove = [];
        _(devmgrs_el.children()).each(function(item_el){
            if (item_el.childElementCount != 0) {
                var modid = item_el.childNodes[0].getAttribute("data-modgroup_id");
                if (_(model_mod_ids).find( function(devmgrid){return modid==devmgrid})==undefined){el_to_remove.push(modid)};
            }
        })
        for (var idx in el_to_remove) {
            $('#group_parent_'+el_to_remove[idx]).remove();
        }
    },
    show: function(e) {
        if (e.target.id != this.modgroup_id) {
            return;
        }
        console.log('show device managers');
        this.devMgrs.update();
    },
    hide: function(e) {
        if (e.target.id != this.modgroup_id) {
            return;
        }
        console.log('hide show device managers');
    }
});

var PropertyView = Backbone.View.extend({
    /*events: {
    },*/
    initialize: function(options){
      this.widget = null;
      _.bindAll(this, 'render'); // fixes loss of context for 'this' within methods

      this.render(); // not all views are self-rendering. This one is.
    },
    updateView: function(value) {
        this.widget.html(parent_obj.model.val);
    },
    render: function(){
        if (this.model.auto_update) {
            this.model.udpate(this.updateView);
        }
        if (this.widget == null) {
            this.widget = $('<div data-redhawk_id="'+this.model.id+'" data-redhawk_object="'+this.model.object_url+'"/>');
            this.widget.html(this.model.val);
            this.model.widget = this.widget;
            $(this.el).append(this.widget);
        }
        return this;
    }
});

var PropertiesView = Backbone.View.extend({
    events: {
        'show.bs.collapse': 'show',
        'hide.bs.collapse': 'hide'
    },
    show: function() {
        console.log('show inside the table view');
    },
    hide: function() {
        console.log('hide inside the table view');
    },
    initialize: function(options){
      this.table_id = options.table_id;
      this.obj_url = options.object_url;
      this.view_id = options.view_id;
      this.widget = null;
      this.props = new PropertiesList();
      this.props.object_url = this.obj_url;
      this.listenTo(this.props,'update_view',this.updateView);
      _.bindAll(this, 'render'); // fixes loss of context for 'this' within methods

      this.render(); // not all views are self-rendering. This one is.
    },
    updateView: function(ret_models){
        _(ret_models).each(function(item){
            if (item.widget == null) {
                var row_1 = $('<div class="row offset-x1 data-contained_data_id="'+item.id+'"/>');
                var col_1 = $('<div class="col-xs-6 col-md-4 id_col"/>');
                col_1.html(item.id);
                var col_2 = $('<div class="col-xs-6 col-md-4 val_col" contentEditable="true" contenteditable="true"/>');
                var propview = new PropertyView({model:item});
                col_2.html(propview.render().el);
                row_1.append(col_1);
                row_1.append(col_2);
                this.widget.append(row_1);
            }
        }, this);
    },
    render: function(){
        if (this.widget == null) {
            this.widget = $('<div id="'+this.table_id+'" data-table_id="'+this.table_id+'"/>');
            $(this.el).append(this.widget);
        }
        this.props.update(this.updateView);
        return this;
    }
});
