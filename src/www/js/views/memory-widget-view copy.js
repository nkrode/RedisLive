var MemoryWidget = Backbone.View.extend({

    updateFrequency : 1000

  , server : ""

  , initialize : function() {

      var self = this

      // set timer for real time update
      this.timer = setInterval( function () {       
      self.model.fetch({
          data : { "server" : self.server }
        }) 
      }, this.updateFrequency )

      // set event listners
      this.model
        .on("error", this.error, this)
        .on("change", this.render, this)

      //set listner for server drop down change
      $(document).on("ServerChange", function(e, server){      
        self.server = server    
        console.log("Memory Widget: Server Changed to: " + server)  
      })     

      // templates
      var templateSelector = "#memory-widget-template"
        , templateSource = $(templateSelector).html()
        
      this.template = Handlebars.compile(templateSource)
      this.$el.empty().html(this.template())

      // chart
      this.chart = new google.visualization.LineChart($("#memory-widget-chart").empty().get(0))
      this.dataTable = new google.visualization.DataTable();
      this.dataTable.addColumn('datetime', 'datetime')
      this.dataTable.addColumn('number', 'Max');
      this.dataTable.addColumn('number', 'Current');      
      
      //this.model.fetch()      
    }

  , events : {
               "click .time-period" : "ChangeTimeFrame"
             , "click .go" : "UpdateModel"          
    }

  , render : function() {

      var model = this.model.toJSON()
        , markUp = this.template(model)
        , self = this

      self.dataTable.removeRows(0,self.dataTable.getNumberOfRows())
            
      $.each(model.data, function(index, obj){          
          
          // first item of the object contains datetime info
          // [ YYYY, MM, DD, HH, MM, SS ]
          var recordDate = new Date(obj[0][0], obj[0][1]-1, obj[0][2], obj[0][3], obj[0][4], obj[0][5])
          
          if(self.dataTable)
            self.dataTable.addRow( [recordDate, obj[1], obj[2]] )        
      })
     
      var pointSize = model.data.length > 120 ? 1 : 5
        , options = {
                      title : ''
                    , colors: ['#1581AA','#77BA44']
                    , chartArea: {'width': '85%'}
                    , pointSize: pointSize 
                    , "hAxis.slantedText" : "true"
                    , "hAxis.slantedTextAngle" : "90" 
                    , areaOpacity : .9,
                      width: "100%" ,
                      height: 200,
                       animation: {
                                    duration: 500,
                                    easing: 'in'
                                  },
                      vAxis: {minValue:0},
                    }

      this.chart.draw(this.dataTable, options)    

    }

  , ChangeTimeFrame : function ( el ) {

    var selectionType = $(el.target).data("type")
      , timeFrame = parseInt( $(el.target).data("time") )

    $(el.target)
      .closest(".btn-group")
      .children()
      .first()
      .text($(el.target).text())

    if ( selectionType == "custom" ) {
      $(el.target)
        .closest(".btn-group")
        .siblings(".date-control")
        .css("display","inline")      
    }
    
    else if ( selectionType == "realtime" ) {
      $(el.target)
        .closest(".btn-group")
        .siblings(".date-control")
        .css("display","none")
      
      var self = this
      this.timer = setInterval( function() { 
        self.model.fetch({
          data : { "server" : self.server }
        }) 
      }, this.updateFrequency )
    }
    
    else {

      $(el.target)
        .closest(".btn-group")
        .siblings(".date-control")
        .css("display","none")

      clearInterval(this.timer)

      var endDate = new Date()
        , startDate = endDate          

      switch(selectionType) {

        case 'minute' : 
          startDate = new Date(endDate - timeFrame * 60000)
          break
                       
        case 'hour' :  
          startDate = new Date(endDate - timeFrame * 60*60000)
          break

        case 'day' :  
          startDate = new Date(endDate - timeFrame * 24*60*60000)
          break

        case 'week' :  
          startDate = new Date(endDate - timeFrame * 7*24*60*60000)
          break

        case 'month' :  
          startDate = new Date(endDate - timeFrame * 30*24*60*60000)
          break
      }

      this.$el.find('[name=from]').val(this.ISODateString(startDate))
      this.$el.find('[name=to]').val(this.ISODateString(endDate))              
      this.UpdateModel()
    }
  }

, ISODateString : function ( d ) {

    function pad ( n ) {
      return n < 10 ? '0'+n : n
    }
    
    return d.getFullYear()+'-'
         + pad(d.getMonth()+1)+'-'
         + pad(d.getDate())+' '
         + pad(d.getHours())+':'
         + pad(d.getMinutes())+':'
         + pad(d.getSeconds())
  }

, UpdateModel : function ( el ) {

    this.model.fetch({
        data : { 
          from : this.$el.find('[name=from]').val()
        , to : this.$el.find('[name=to]').val()
        , server : this.server
      }
    })  
  }

})