var MemoryWidget = BaseWidget.extend({

    initialize : function() {

      this.Name = "Memory Widget"

      this.init()
      
      // templates
      var templateSelector = "#memory-widget-template"
        , templateSource = $(templateSelector).html()
        
      this.template = Handlebars.compile(templateSource)
      this.$el.empty().html(this.template())

      // chart
      this.chart = new google.visualization.LineChart($("#memory-widget-chart").empty().get(0))
      this.dataTable = new google.visualization.DataTable()
      this.dataTable.addColumn('datetime', 'datetime')
      this.dataTable.addColumn('number', 'Max')
      this.dataTable.addColumn('number', 'Current')      
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
                    , colors: [ '#1581AA', '#77BA44' ]                    
                    , pointSize: pointSize 
                    , chartArea: { 'top' : 10, 'width' : '85%' }
                    , width : "100%"
                    , height : 200
                    , animation : { duration : 500, easing : 'out' }                    
                    }

      this.chart.draw(this.dataTable, options)
    }
})