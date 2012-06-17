var CommandsWidget = BaseWidget.extend({

    initialize : function() {

      this.Name = "Commands Widget"

      this.init()      
      
      // templates
      var templateSelector = "#commands-widget-template"
        , templateSource = $(templateSelector).html()
        
      this.template = Handlebars.compile(templateSource)
      this.$el.empty().html(this.template())

      // chart
      this.chart = new google.visualization.AreaChart($("#commands-widget-chart").empty().get(0))
      this.dataTable = new google.visualization.DataTable()
      this.dataTable.addColumn('datetime', 'datetime')
      this.dataTable.addColumn('number', 'Commands Processed')      
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
            self.dataTable.addRow( [recordDate, obj[1]] )        
      })
     
      var pointSize = model.data.length > 120 ? 1 : 5
        , options = {
                      title : ''
                    , colors: [ '#17BECF', '#9EDAE5' ]
                    , areaOpacity : .9                    
                    , pointSize: pointSize                      
                    , chartArea: { 'top' : 10, 'width' : '85%' }
                    , width : "100%"
                    , height : 200
                    , animation : { duration : 500, easing: 'out' } 
                    , vAxis: { minValue : 0 }
                    }

      this.chart.draw(this.dataTable, options)
    }
})