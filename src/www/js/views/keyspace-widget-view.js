var KeySpaceWidget = BaseWidget.extend({

    initialize : function() {

      this.init()

      var templateSelector = "#keyspace-widget-template"
        , templateSource = $(templateSelector).html()
        
      this.template = Handlebars.compile(templateSource)
      this.$el.empty().html(this.template())

      this.chart = new google.visualization.ColumnChart($("#keyspace-widget-chart").empty().get(0))
      this.dataTable = new google.visualization.DataTable();
      this.dataTable.addColumn('string', 'datetime')
      this.dataTable.addColumn('number', 'Hits');
      this.dataTable.addColumn('number', 'Misses');


      // this.model.on("change", this.render, this)
      
      // this.model.fetch()      

      // var self = this
      // this.timer = setInterval( function() { self.model.fetch() }, this.updateFrequency )
    }

  , render : function() {

      var model = this.model.toJSON()
        , markUp = this.template(model)
        , self = this

      self.dataTable.removeRows(0,self.dataTable.getNumberOfRows())
            
      $.each(model.data, function(index, obj){
          
          // first item of the object contains datetime info
          // [ YYYY, MM, DD, HH, MM, SS ]
          var recordDate = new Date(obj[0][0], obj[0][1], obj[0][2], obj[0][3], obj[0][4], obj[0][5])

          if(self.dataTable)
            self.dataTable.addRow( [obj[6], obj[1], obj[2]] )        
      })
     
      var pointSize = model.data.length > 60 ? 0 : 5
        , options = {
                      title : ''
                    , colors: ['#008FD5','#006B9F']
                    , chartArea: {'top' : '0px' , 'width': '70%'}
                    //, pointSize: pointSize 
                    //, "hAxis.slantedText" : "true"
                    //, "hAxis.slantedTextAngle" : "90" 
                    //, areaOpacity : .9,
                    ,  width: "100%" 
                    , height: 300
                    , animation: {
                                    duration: 500,
                                    easing: 'in'
                                  }
                     //  vAxis: {minValue:0},
                    }

      this.chart.draw(this.dataTable, options)    

    }

})