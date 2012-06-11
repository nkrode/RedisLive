/* Main App
* ====================== */

var App = {

    init: function() {

        this.RegisterPartials()
        this.RegisterHelpers()

        var ServerDropDown = new ServerList({            
            el : $("#server-list")
          , model : new ServerListModel()
        })

        var infoWidget = new InfoWidget({            
            el : $("#info-widget-placeholder")
          , model : new InfoWidgetModel()
        })

        var memoryWidget = new MemoryWidget({
            el : $("#memory-widget-placeholder")
          , model : new MemoryWidgetModel()
        })  

        var commandsWidget = new CommandsWidget({            
            el : $("#commands-widget-placeholder")
          , model : new CommandsWidgetModel()
        })        
        
        var topCommandsWidget = new TopCommandsWidget({            
            el : $("#top-commands-widget-placeholder")
          , model : new TopCommandsWidgetModel()
        })        

        var topKeysWidget = new TopKeysWidget({            
            el : $("#top-keys-widget-placeholder")
          , model : new TopKeysWidgetModel()
        })        
    }

  , RegisterPartials : function(){

       Handlebars.registerPartial("date-dropdown", $("#date-dropdown-template").html());

  } 

  , RegisterHelpers : function(){

    Handlebars.registerHelper('hash', function ( context, options ) {
  
              var ret = ""
                , counter = 0

              $.each(context, function ( key, value ) {
                
                if (typeof value != "object") {
                  obj = { "key" : key, "value" : value , "index" : counter++ }
                  ret = ret + options.fn(obj)
                }

              })

              return ret
    })

  }
}
