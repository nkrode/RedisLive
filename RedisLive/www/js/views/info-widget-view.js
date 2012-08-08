/* Info Widget
* ====================== */

var InfoWidget = BaseWidget.extend({

  initialize : function() {  

    this.Name = "Info Widget"

    this.init()
    this.updateFrequency = 5000 // every 5 seconds
        
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

})