/* Info Widget
* ====================== */

var InfoWidget = Backbone.View.extend({

  updateFrequency : 1000

, server : ""

, initialize : function() {  

    self = this

    // set timer for real time update
    this.timer = setInterval( function () {       
    self.model.fetch({
        data : { "server" : self.server }
      }) 
    }, self.updateFrequency )

    // set event listners
    this.model
      .on("error", this.error, this)
      .on("change", this.render, this)
  
    // set listner for server drop down change
    $(document).on("ServerChange", function(e, server){      
      self.server = server      
      console.log("Info Widget: Server Changed to: " + server)
    })    
        
    // templates
    var templateSource        = $("#info-widget-template").html()
      , popOverTemplateSource = $("#popover-template").html()
      , infoTemplateSource    = $("#info-template").html() 

    this.template         = Handlebars.compile(templateSource)
    this.popOverTemplate  = Handlebars.compile(popOverTemplateSource)
    this.infoTemplate     = Handlebars.compile(infoTemplateSource)

  }
  
, render: function() {

    var model         = this.model.toJSON()
      , markUp        = this.template(model)
      , popoverMarkup = this.popOverTemplate(model.databases)
      , infoMarkup    = this.infoTemplate(model)

    $(this.el).html(markUp)
      
    $('#total-keys').popover({
                               "title" : "databases"
                             , "content" : popoverMarkup
                             })

    $('#misc-info').popover({
                              "title" : "info"
                            , "content" : infoMarkup
                            , "placement" : "bottom"
                            })      
  }

, error: function ( model, error ) {
      console.log(error)
  }

})