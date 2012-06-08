var ServerList = Backbone.View.extend({

  initialize : function() {       
    this.$el.empty()
    this.model.on("change", this.render, this)    
    this.$el.on("change", this.ServerChanged)
    this.model.fetch()   
  }

, ServerChanged : function(){
    $(document).trigger("ServerChange", $(this).val())   
}

, render : function() {
    var model = this.model.toJSON()   
      , self = this  

    $.each(model.servers,function(index, obj){
      self.$el.append("<option value='" + obj.id + "'>" + obj.id + "</option>")
    })

    self.$el.trigger("change")
  }

})