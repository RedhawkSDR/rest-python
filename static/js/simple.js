(function($,foo){
  var ListView = Backbone.View.extend({
    el: $('body'), // attaches `this.el` to an existing element.

    initialize: function(options){
      _.bindAll(this, 'render'); // fixes loss of context for 'this' within methods

       this.render(); // not all views are self-rendering. This one is.
    },

    render: function(){
      $(this.el).append("<h3>Domains</h3>");
      setDomain(this.el, foo);
      $(this.el).append("<ul> <li>hello world</li> </ul>");
    }
  });

  var listView = new ListView({foo:'hello'});
})(jQuery,my_name);

// $(".panel-collapse_domainMgr").on("shown.bs.collapse", function(e) {
//     console.log('showing dommgr....');
// });
