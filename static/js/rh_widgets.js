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

var PropertyItem = Backbone.Model.extend({
    defaults: {
        id: '',
        object_url: '',
        val: '',
        auto_update: true,
        view: null
    },
    initialize: function(options) {
        this.id = options.id;
        this.object_url = options.object_url;
        if (typeof(options.val) != 'undefined') {
            this.val = options.val;
        }
        if (typeof(options.auto_update) != 'undefined') {
            this.auto_update = options.auto_update;
        }
    }
});

var PropertiesList = Backbone.Collection.extend({
    model: PropertyItem
});


var PropertyView = Backbone.View.extend({
    /*events: {
    },*/
    initialize: function(options){
      this.widget = null;
      _.bindAll(this, 'render'); // fixes loss of context for 'this' within methods

      this.render(); // not all views are self-rendering. This one is.
    },
    render: function(){
        if (this.model.auto_update) {
            var parent_obj = this;
            var update_url = this.model.object_url+"/props/"+this.model.id;
            $.getJSON(update_url, function(data) {
                for (var first_idx in props_resp) {
                    if (props_resp[first_idx] != 'props') {
                        continue;
                    }
                    for (var idx in props_resp[first_idx]) {
                        if (props_resp[first_idx][idx]["name"] != parent_obj.model.id) {
                            continue;
                        }
                        parent_obj.model.val = props_resp[first_idx]["value"];
                        parent_obj.widget.html(parent_obj.model.val);
                        break;
                    }
                }
            })
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

/*var PropertiesView = Backbone.View.extend({
    initialize: function(options){
      this.idvalues = options.idvalues;
      this.table_id = options.table_id;
      this.widget = null;
      _.bindAll(this, 'render'); // fixes loss of context for 'this' within methods

      this.render(); // not all views are self-rendering. This one is.
    },
    render: function(){
        if (this.widget == null) {
            this.widget = createTable(this.idvalues,this.table_id);
            $(this.el).append(this.widget);
        }
        return this;
    }
});*/

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

var PropertiesView = Backbone.View.extend({
    /*events: {
    },*/
    defaults: {
        idvalues:null,
        table_id:null,
        obj_url:null,
        props:null,
        view_id:null
    },
    initialize: function(options){
      this.idvalues = options.idvalues;
      this.table_id = options.table_id;
      this.obj_url = options.object_url;
      this.view_id = options.view_id;
      this.props = new PropertiesList();
      for (idx=0;idx<this.idvalues.length;idx++) {
        var prop = new PropertyItem({id:this.idvalues[idx].prop_id,object_url:this.obj_url+'/props/'+this.idvalues[idx].prop_id,auto_update:false});
        this.props.add(prop);
      }
      this.widget = null;
      _.bindAll(this, 'render'); // fixes loss of context for 'this' within methods

      this.render(); // not all views are self-rendering. This one is.
    },
    updateProperties: function(){
        if (typeof(this.obj_url) != 'undefined') {
            var parent_obj = this;
            var update_url = this.obj_url+"/props/";
            $.getJSON(update_url, function(data) {
                if (parent_obj.props == null) {
                    return;
                }
                for (var first_idx in data) {
                    if (first_idx != 'props') {
                        continue;
                    }
                    for (var idx in data[first_idx]) {
                        _(parent_obj.props.models).each(function(item){
                            if (data[first_idx][idx]["name"] == item.id) {
                                item.val = data[first_idx][idx]["value"];
                                item.widget.html(item.val);
                            }
                        });
                    }
                }
            });
        }
    },
    render: function(){
        console.log('rendering table');
        this.updateProperties();
        if (this.widget == null) {
            this.widget = $('<div data-table_id="'+this.table_id+'"/>');
            _(this.props.models).each(function(item){
                var row_1 = $('<div class="row offset-x1 data-contained_data_id="'+item.id+'"/>');
                var col_1 = $('<div class="col-xs-6 col-md-4 id_col"/>');
                col_1.html(item.id);
                var col_2 = $('<div class="col-xs-6 col-md-4 val_col" contentEditable="true" contenteditable="true"/>');
                var propview = new PropertyView({model:item});
                col_2.html(propview.render().el);
                row_1.append(col_1);
                row_1.append(col_2);
                this.widget.append(row_1);
            }, this);
            $(this.el).append(this.widget);
        }
        return this;
    }
});

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

      this.render(); // not all views are self-rendering. This one is.
    },
    show: function() {
        console.log('show inside the view');
    },
    hide: function() {
        console.log('hide inside the view');
    },

    render: function(){
        if (this.widget == null) {
            this.widget = accordionElement(this.group_id,this.modgroup_id,this.level,this.group_type,this.color,this.classname,this.visible_text);
            $(this.el).append(this.widget);
        }
        return this;
    }
});
