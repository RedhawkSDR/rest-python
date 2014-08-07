
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
            console.log('---------- triggering properties model');
            parent_obj.trigger('update_view',parent_obj.models);
        });
    }
});

var DeviceItem = Backbone.Model.extend({
    defaults: {
        id: '',
        name: '',
        object_url: '',
        auto_update: true,
    },
    initialize: function(options) {
        this.name = options.name;
        this.id = options.id;
        this.devMgr = options.devMgr;
        this.object_url = options.object_url;
        if (typeof(options.auto_update) != 'undefined') {
            this.auto_update = options.auto_update;
        }
    },
    update: function(callback) {
        console.log('retrieving device manager...');
        var parent_obj = this;
        var update_url = this.object_url+"/devicemanagers/"+this.devMgr_id+'/'+this.id;
        retrieveDev(function(data){
        });
/*        $.getJSON(update_url, function(data) {
            console.log(data);
        })*/
    }
});

var DeviceList = Backbone.Collection.extend({
    model: DeviceItem,
    update: function() {
        var parent_obj = this;
        var update_url = this.object_url+"/devicemanagers/"+this.devMgr.id+"/devs/";
        retrieveDevs(this.devMgr.id,function(data){
            console.log('------------ retrieving devs');
            var msg = JSON.parse(data);
            console.log(msg);
            devs = []
            for (var idx in msg) {
                console.log('msg[idx]:',msg[idx]);
                devs.push([msg[idx][0].devName, msg[idx][1].devId]);
            }
            console.log('devs',devs);
            console.log(parent_obj.models);
            _(devs).each(function(dev){
                if (_(parent_obj.models).find(function(item){return item.id == dev[1]}) == undefined) {
                    var prop = new parent_obj.model({id:dev[1],name:dev[0],object_url:update_url+dev[1],auto_update:false,devMgr:parent_obj.devMgr});
                    parent_obj.add(prop);
                };
            });
            console.log(parent_obj.models);
            //_(parent_obj.models).each(function(item){ // clear out items that are no longer needed
            //    if (_(devs).find(function(dev) {return item.id == dev[1]}) == undefined) {
            //        parent_obj.remove(item);
            //    };
            //});
            console.log('---------- triggering device list model');
            console.log(parent_obj.models);
            console.log('---------- triggering device list model');
            parent_obj.trigger('collection_update_view',parent_obj.models,parent_obj.devMgr.id);
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
        this.devs = new DeviceList();
        console.log('init devs set:',this.devs);
        this.devs.devMgr = this;
        if (typeof(options.auto_update) != 'undefined') {
            this.auto_update = options.auto_update;
        }
    },
    update: function() {
        var parent_obj = this;
        var update_url = this.object_url+"/devicemanagers/"+this.id;
        retrieveDevMgr(this.id,function(data){
            var devmgr = JSON.parse(data);
            var devs = []
            var svcs = []
            var props = []
            for (var idx in devmgr.devMgr) {
                console.log(devmgr.devMgr[idx]);
                if (devmgr.devMgr[idx].dev != undefined) {
                    devs.push([devmgr.devMgr[idx].dev.id,devmgr.devMgr[idx].dev.name]);
                } else if (devmgr.devMgr[idx].svc != undefined) {
                    svcs.push(devmgr.devMgr[idx].svc.name);
                }
            }
            _(devs).each(function(dev){
                console.log('================ running over each dev',dev)
                if (_(parent_obj.devs).find(function(item){return item.name == dev[1]}) == undefined) {
                    var new_dev = new DeviceItem({id:dev.id,name:dev.name,object_url:update_url+'/devs/'+dev.id,auto_update:false,devMgr:parent_obj.id});
                    parent_obj.devs.add(new_dev);
                };
            });
            _(parent_obj.devs.models).each(function(item){
                if (_(devs).find(function(dev) {return item.name == dev.name}) == undefined) {
                    parent_obj.devs.remove(item);
                };
            });
            console.log('---------- triggering device manager model');
            parent_obj.trigger('update_view',parent_obj.devs.models);
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
            console.log('---------- triggering device manager list model');
            parent_obj.trigger('collection_update_view',parent_obj.models);
        });
    }
});
