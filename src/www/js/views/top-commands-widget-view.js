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
      this.chart = new google.visualization.ColumnChart($("#top-commands-widget-chart").empty().get(0))
      this.dataTable = new google.visualization.DataTable()
      this.dataTable.addColumn('string', 'command')
      this.dataTable.addColumn('number', 'count')

    }

  , render : function() {

      var model = this.model.toJSON()
        , markUp = this.template(model)
        , self = this

      this.dataTable.removeRows(0, this.dataTable.getNumberOfRows())

      this.dataTable.addRows(model.data)

      //https://developers.google.com/chart/interactive/docs/gallery/columnchart#Configuration_Options        
      var options = {
                      title : ''
                    , colors : ['#006B9F', '#008FD5', '#454545', '#E70B20' ]                                        
                    , chartArea: { 'left' : 100, 'top' : 10, 'width': '90%', 'height': '200' } 
                    , height: 250
                    , animation: { duration : 500, easing : 'linear' }
                    , legend: { position: 'none' }                                  
                    }      

      this.chart.draw(this.dataTable, options)
    }
})