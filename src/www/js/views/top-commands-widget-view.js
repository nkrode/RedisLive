var TopCommandsWidget = BaseWidget.extend({

    initialize : function() {

      this.Name = "Top Commands Widget"

      this.init()      
      
      // templates
      var templateSelector = "#top-commands-widget-template"
        , templateSource = $(templateSelector).html()
        
      this.template = Handlebars.compile(templateSource)
      this.$el.empty().html(this.template())

      // chart
      //this.chart = new google.visualization.PieChart($("#top-commands-widget-chart").empty().get(0))
      this.chart = new google.visualization.ColumnChart($("#top-commands-widget-chart").empty().get(0))
      this.dataTable = new google.visualization.DataTable();
      this.dataTable.addColumn('string', 'command')
      this.dataTable.addColumn('number', 'count');        

    }

  , render : function() {

      var model = this.model.toJSON()
        , markUp = this.template(model)
        , self = this

      this.dataTable.removeRows( 0, this.dataTable.getNumberOfRows() )

      this.dataTable.addRows(model.data)

      //https://developers.google.com/chart/interactive/docs/gallery/piechart#Configuration_Options    
        
        var options = {
                      title : ''
                    , colors : ['#006B9F', '#008FD5', '#454545', '#E70B20' ]                                        
                    , chartArea: { 'left' : 30, 'top' : 20, 'width': '85%', 'height': '300' }  
                    , "hAxis.slantedText" : "true"
                    , "hAxis.slantedTextAngle" : "90" 
                    , areaOpacity : .9                      
                    ,height: 350
                    ,  animation: {
                                    duration: 500,
                                    easing: 'linear'
                                  }
                    //, pieSliceText : 'label'                 
                    //  , legend : 'bottom'
                    }      

      this.chart.draw(this.dataTable, options)      

    }  

})