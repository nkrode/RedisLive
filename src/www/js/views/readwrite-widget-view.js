var ReadWriteWidget = BaseWidget.extend({

    initialize : function() {

      this.init()

      var templateSelector = "#readwrite-widget-template"
        , templateSource = $(templateSelector).html()
        
      this.template = Handlebars.compile(templateSource)
      this.$el.empty().html(this.template())

      this.chart = new google.visualization.AreaChart($("#readwrite-widget-chart").empty().get(0))
      this.dataTable = new google.visualization.DataTable();
      this.dataTable.addColumn('datetime', 'datetime')
      this.dataTable.addColumn('number', 'Reads');
      this.dataTable.addColumn('number', 'Writes');

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
            self.dataTable.addRow( [recordDate, obj[1], obj[2]] )        
      })
     
      var pointSize = model.data.length > 60 ? 0 : 5
        , options = {
                      title : ''
                    , colors: [ '#17BECF', '#9EDAE5' ]
                    , isStacked: true
                    , chartArea: {'width': '85%'}
                    , pointSize: pointSize 
                    , "hAxis.slantedText" : "true"
                    , "hAxis.slantedTextAngle" : "90" 
                    , areaOpacity : .9,
                      width: "100%" ,
                      height: 200,
                       animation: {
                                    duration: 500,
                                    easing: 'linear'
                                  }
                      
                    , vAxis: { minValue:0}                    
                    }

      this.chart.draw(this.dataTable, options)  



      // var model = this.model.toJSON()
      //   , markUp = this.template(model)

      // var dataTable = new google.visualization.DataTable();
      // dataTable.addColumn('datetime', 'datetime')
      // dataTable.addColumn('number', 'Reads');
      // dataTable.addColumn('number', 'Writes');
      
      // $.each(model.data, function(index, obj){
          
      //     // first item of the object contains datetime info
      //     // [ YYYY, MM, DD, HH, MM, SS ]
      //     var recordDate = new Date(obj[0][0], obj[0][1], obj[0][2], obj[0][3], obj[0][4], obj[0][5])
          
      //     dataTable.addRow( [recordDate, obj[1], obj[2]] )
      // })
      
      // this.chartData = dataTable
     
      // var pointSize = model.data.length > 60 ? 0 : 0
      //   , options = {
      //                 title : ''
      //               , colors: [ '#17BECF', '#9EDAE5' ]
      //               //, colors : [ '#2D3942', '#3B4147']
      //               , chartArea: {'width': '85%'}
      //               , areaOpacity : .8
      //               , pointSize: pointSize
      //               }

      // this.chart = new google.visualization.AreaChart($("#readwrite-widget-chart").empty().get(0))
      // this.chart.draw(this.chartData, options)    
    
    }

})