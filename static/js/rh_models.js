
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
    },
    update: function(callback) {
        var parent_obj = this;
        var update_url = this.object_url+"/props/"+this.id;
        $.getJSON(update_url, function(data) {
            for (var first_idx in props_resp) {
                if (props_resp[first_idx] != 'props') {
                    continue;
                }
                for (var idx in props_resp[first_idx]) {
                    if (props_resp[first_idx][idx]["name"] != parent_obj.id) {
                        continue;
                    }
                    parent_obj.val = props_resp[first_idx]["value"];
                    callback(parent_obj.val);
                    break;
                }
            }
        })
    }
});

var PropertiesList = Backbone.Collection.extend({
    model: PropertyItem,
    update: function(callback) {
        var parent_obj = this;
        var update_url = this.object_url+"/props/";
        $.getJSON(update_url, function(data) {
            for (var first_idx in data) {
                if (first_idx != 'props') {
                    continue;
                }
                for (var idx in data[first_idx]) {
                    var p=data[first_idx][idx];
                    if (_(parent_obj.models).find(function(item){return p["name"] == item.id}) == undefined) {
                        var prop = new parent_obj.model({val:p["value"],id:p["name"],object_url:update_url+p["name"],auto_update:false});
                        parent_obj.add(prop);
                    }
                }
            }
            parent_obj.trigger('update_view',parent_obj.models);
        });
    }
});

var DeviceManagerItem = Backbone.Model.extend({
    defaults: {
        id: '',
        object_url: '',
        auto_update: true,
    },
    initialize: function(options) {
        this.id = options.id;
        this.object_url = options.object_url;
        if (typeof(options.auto_update) != 'undefined') {
            this.auto_update = options.auto_update;
        }
    },
    update: function() {
        var parent_obj = this;
        var update_url = this.object_url+"/devicemanagers/";
        retrieveDevMgr(function(data){
            var domain = JSON.parse(data);
            group_ids = []
            for (var idx in domain.domain) {
                group_ids.push(domain.domain[idx].devMgrName);
            }
            _(group_ids).each(function(group_id){
                if (_(parent_obj.models).find(function(item){return item.id == group_id}) == undefined) {
                    var prop = new parent_obj.model({id:group_id,object_url:update_url+group_id,auto_update:false});
                    parent_obj.add(prop);
                };
            });
            _(parent_obj.models).each(function(item){ // clear out items that are no longer needed
                if (_(group_ids).find(function(group_id) {return item.id == group_id}) == undefined) {
                    parent_obj.remove(item);
                };
            });
            parent_obj.trigger('update_view',parent_obj.models);
        });
    }
});

var DeviceItem = Backbone.Model.extend({
    defaults: {
        id: '',
        object_url: '',
        auto_update: true,
    },
    initialize: function(options) {
        this.id = options.id;
        this.devMgr_id = options.devMgr_id;
        this.object_url = options.object_url;
        if (typeof(options.auto_update) != 'undefined') {
            this.auto_update = options.auto_update;
        }
    },
    update: function(callback) {
        var parent_obj = this;
        var update_url = this.object_url+"/devicemanagers/"+this.devMgr_id+'/'+this.id;
        $.getJSON(update_url, function(data) {
            console.log(data);
        })
    }
});

var DeviceList = Backbone.Collection.extend({
    model: DeviceItem,
    update: function() {
        var parent_obj = this;
        var update_url = this.object_url+"/devicemanagers/";
        retrieveDev(function(data){
            var domain = JSON.parse(data);
            group_ids = []
            for (var idx in domain.domain) {
                group_ids.push(domain.domain[idx].devMgrName);
            }
            _(group_ids).each(function(group_id){
                if (_(parent_obj.models).find(function(item){return item.id == group_id}) == undefined) {
                    var prop = new parent_obj.model({id:group_id,object_url:update_url+group_id,auto_update:false});
                    parent_obj.add(prop);
                };
            });
            _(parent_obj.models).each(function(item){ // clear out items that are no longer needed
                if (_(group_ids).find(function(group_id) {return item.id == group_id}) == undefined) {
                    parent_obj.remove(item);
                };
            });
            parent_obj.trigger('update_view',parent_obj.models);
        });
    }
});

var DeviceManagerList = Backbone.Collection.extend({
    model: DeviceManagerItem,
    update: function() {
        var parent_obj = this;
        var update_url = this.object_url+"/devicemanagers/";
        retrieveDevMgrs(function(data){
            var domain = JSON.parse(data);
            group_ids = []
            for (var idx in domain.domain) {
                group_ids.push(domain.domain[idx].devMgrName);
            }
            _(group_ids).each(function(group_id){
                if (_(parent_obj.models).find(function(item){return item.id == group_id}) == undefined) {
                    var prop = new parent_obj.model({id:group_id,object_url:update_url+group_id,auto_update:false});
                    parent_obj.add(prop);
                };
            });
            _(parent_obj.models).each(function(item){ // clear out items that are no longer needed
                if (_(group_ids).find(function(group_id) {return item.id == group_id}) == undefined) {
                    parent_obj.remove(item);
                };
            });
            parent_obj.trigger('update_view',parent_obj.models);
        });
    }
});
