var KeysWidget = BaseWidget.extend({

  initialize: function() {

    this.init()

    var templateSelector = "#keys-widget-template"
      , templateSource = $(templateSelector).html()
        
    this.template = Handlebars.compile(templateSource)
    this.$el.empty().html(this.template())

    this.chart = new google.visualization.PieChart($("#keys-widget-chart").empty().get(0))
    this.dataTable = new google.visualization.DataTable();
    this.dataTable.addColumn('string', 'keytype')
    this.dataTable.addColumn('number', 'count');    

    // this.model.on("change", this.render, this)
      
    // this.model.fetch()      

    // //refresh widgets every second
    // var self = this
    // this.timer = setInterval( function() { self.model.fetch() }, this.updateFrequency )
    
  }  

, render: function() {

    var model = this.model.toJSON()
      , markUp = this.template(model)     

    this.dataTable.removeRows( 0, this.dataTable.getNumberOfRows() )

    this.dataTable.addRows(model.data)
  
    var options = {
        title : ''
      , colors : ['#E70B20', '#454545']
      , areaOpacity : 1.0      
      , animation : {
          duration : 500
        , easing: 'in'
        }      
      , width: 400
      , height : 400
      , chartArea: { 
                     'left' : 0
                   , 'top' : 30
                   , 'width': '100%'

                   }
      , legenArea : {
          'top' : 0
      }
      , legend : 'bottom'
    }

    this.chart.draw(this.dataTable, options)    
  }   

})