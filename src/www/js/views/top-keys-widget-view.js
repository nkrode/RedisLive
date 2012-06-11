var TopKeysWidget = BaseWidget.extend({

    initialize : function() {

      this.Name = "Top Keys Widget"

      this.init()      
      
      // templates
      var templateSelector = "#top-keys-widget-template"
        , templateSource = $(templateSelector).html()
        
      this.template = Handlebars.compile(templateSource)
      this.$el.empty().html(this.template())

      // chart
      this.chart = new google.visualization.ColumnChart($("#top-keys-widget-chart").empty().get(0))
      this.dataTable = new google.visualization.DataTable()
      
    }

  , render : function() {

      var model = this.model.toJSON()
        , markUp = this.template(model)
        , self = this

      this.dataTable.removeRows( 0, this.dataTable.getNumberOfRows() )
      this.dataTable.removeColumns(0, this.dataTable.getNumberOfColumns())

      this.dataTable.addColumn('string', 'key')
      this.dataTable.addColumn('number', 'count')
      this.dataTable.addRows(model.data)    

      var options = {
                      title : ''
                    , colors : [ '#008FD5', '#006B9F', '#454545', '#E70B20' ]     
                    , chartArea: { 'left' : 30, 'top' : 20, 'width': '85%', 'height': '300' }  
                    , height : 350                    
                    , legend: { position: 'none' }                    
                   }      

      this.chart.draw(this.dataTable, options)
    }  
})