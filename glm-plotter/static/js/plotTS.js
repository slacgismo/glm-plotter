// JAC - jdechalendar@stanford.edu
// Oct 12, 2016

// script to plot a timeseries

togglePlotTS = sliderDiv.append("select")
  .attr("id", "togglePlotTS")
  .attr("style", "float: right;");
togglePlotTS.append("option")
  .text("No plotTS");
togglePlotTS.append("option")
  .text("With plotTS");

var margin = {top: 20, right: 20, bottom: 30, left: 50},
    wPlot = 960 - margin.left - margin.right,
    hPlot = 300 - margin.top - margin.bottom,
    padding = 50;

var dummyData=[{"date":new Date(2020,0,1)},
            {"date":new Date(2020,0,2)}];

var xScale = d3.time.scale()
    .range([padding, wPlot-padding])
    .domain(d3.extent(dummyData, function(d) { return d.date; }));

var yScale = d3.scale.linear()
    .range([hPlot-padding,padding/2])
    .domain([0, 40]);

var date_format = d3.time.format("%d-%b %H:%m");
var xAxis = d3.svg.axis()
    .scale(xScale)
    .orient("bottom")
    .ticks(10)
    .tickFormat(date_format);

var yAxis = d3.svg.axis()
    .scale(yScale)
    .orient("left")
    .ticks(6);

var svgPlotTS = d3.select("#main").append("svg")
    .attr("width", wPlot + margin.left + margin.right)
    .attr("height", hPlot + margin.top + margin.bottom)
  .append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

// add x axis
svgPlotTS.append("g")
  .attr("class", "x_axis")
  .attr("transform", "translate(0," + (hPlot-padding) + ")")
  .call(xAxis)
// x label
xlabel = svgPlotTS.append("text")
  .attr("text-anchor", "middle")
  .attr("transform", "translate(" + (wPlot/2) + "," + (hPlot-(padding/3)) + ")")
  .text("Time");

// add y axis
svgPlotTS.append("g")
  .attr("class", "y_axis")
  .attr("transform", "translate(" + padding + ",0)")
  .call(yAxis)
// y label
ylabel = svgPlotTS.append("text")
  .attr("text-anchor", "middle")
  .attr("transform", "translate(" + 0 + "," + (hPlot/2) + ")rotate(-90)")
  .text("Voltage (V)");

svgPlotTS.selectAll(".x_axis text")  // select all the text elements for the xaxis
    .attr("transform", function(d) {
      return "translate(" + this.getBBox().height*-2 + "," + this.getBBox().height + ")rotate(-30)";
    });

var myLine = svgPlotTS.append("path")

var fieldToPlot = "voltage_A.real";

var line = d3.svg.line()
    .x(function(d) { return xScale(d.timestamp); })
    .y(function(d) { return yScale(d[fieldToPlot]); });

function updateTSPlot(nodeID){
    if (typeof nodeID !== 'undefined'){
        var endPoint = "data/ts/" + nodeID
    } else{
        var endPoint = "data/ts/" + document.getElementById('tsPlotID').value
    }
    ylabel.text("Voltage - " + nodeID + " (V)");

    d3.csv(endPoint, typeTSData, function(data) {
      // extract header vals
      // assume that 'timestamp'column is always there - remove it from the header list
      var header = d3.keys(data[0])
      var id = header.indexOf('timestamp');
      if (id > -1) {header.splice(id, 1);}
      // TODO: give the user an option to select which ones he wants to plot
      // for now use hack

      // set limits of axes
      xScale.domain(d3.extent(data, function(d) { return d.timestamp; }));
      yScale.domain(d3.extent(data, function(d) { return d[fieldToPlot];})).nice();
      svgPlotTS.selectAll("g.x_axis")
        .call(xAxis);
      svgPlotTS.selectAll("g.y_axis")
        .call(yAxis);

      myLine.datum(data)
          .attr("class", "line")
          .attr("d", line);
    });
}

// this may be a bit tricky - should be converted in the python parser maybe
// since D3 doesn't seem to support microseconds or tz in the PST format

var formatDate = d3.time.format("%Y-%m-%d %H:%M:%S.%L PST");

function typeTSData(d) {
  d.timestamp = formatDate.parse(d.timestamp);
  var headers = d3.keys(d)
  for (var i = 0; i < headers.length; i++){
    if (headers[i] != 'timestamp'){d[headers[i]] = +d[headers[i]];}
  }
  return d;
}

// svgPlotTS.attr("visibility", "collapse");
togglePlotTS.on("input", togglePlotTSChart);

function togglePlotTSChart() {
  if (document.getElementById("togglePlotTS").value == "With plotTS"){
    console.log("with")
    svgPlotTS.attr("visibility", "visible");  
    svgNetwork.attr("height", hNetworkSmall);
    force.size([wNetwork, hNetworkSmall]);
  } else {
    console.log("without")
    svgPlotTS.attr("visibility", "collapse");
    svgNetwork.attr("height", hNetworkBig);
    force.size([wNetwork, hNetworkBig]);
  }
}