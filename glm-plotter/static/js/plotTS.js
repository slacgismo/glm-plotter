// JAC - jdechalendar@stanford.edu
// Oct 12, 2016

// script to plot a timeseries

// initialize plotting of time series when user presses button

// d3.select("#plotTS").on("input", initializePlot);
togglePlotTS = sliderDiv.append("select")
  .attr("id", "togglePlotTS")
  .attr("style", "float: right;");
togglePlotTS.append("option")
  .text("No plotTS");
togglePlotTS.append("option")
  .text("With plotTS");

var margin = {top: 20, right: 20, bottom: 30, left: 50},
    width = 960 - margin.left - margin.right,
    height = 300 - margin.top - margin.bottom;

var x = d3.time.scale()
    .range([0, width]);

var y = d3.scale.linear()
    .range([height, 0]);

var xAxis = d3.svg.axis()
    .scale(x)
    .orient("bottom");

var yAxis = d3.svg.axis()
    .scale(y)
    .orient("left");

var svgPlotTS = d3.select("#main").append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
  .append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

svgPlotTS.append("g")
  .attr("class", "x axis")
  .attr("transform", "translate(0," + height + ")")
  .call(xAxis)
.append("text")
  .attr("y", 15)
  .attr("x", 450)
  .style("text-anchor", "end")
  .text("time");

svgPlotTS.append("g")
  .attr("class", "y axis")
  .call(yAxis)
.append("text")
  .attr("transform", "rotate(-90)")
  .attr("y", 6)
  .attr("dy", "-3em")
  .style("text-anchor", "end")
  .text("Voltage (V)");

var myLine = svgPlotTS.append("path")

// var myInput = d3.select("body")
//     .append("input")
//     .attr("type","button")
//     .attr("value", "change ts")
//     .on("click", updateTSPlot);

var fieldToPlot = "voltage_A.real";

var line = d3.svg.line()
    .x(function(d) { return x(d.timestamp); })
    .y(function(d) { return y(d[fieldToPlot]); });

function updateTSPlot(nodeID){
    if (typeof nodeID !== 'undefined'){
        var endPoint = "data/ts/" + nodeID
    } else{
        var endPoint = "data/ts/" + document.getElementById('tsPlotID').value
    }
    // d3.tsv(endPoint, type, function(error, data) {
    //   if (error) throw error;

    //   x.domain(d3.extent(data, function(d) { return d.date; }));
    //   y.domain(d3.extent(data, function(d) { return d.close; }));

    //   myLine.datum(data)
    //       .attr("class", "line")
    //       .attr("d", line);
    // });
    // console.log(endPoint)
    d3.csv(endPoint, typeTSData, function(data) {
      // console.log(data)
      // extract header vals
      // assume that 'timestamp'column is always there - remove it from the header list
      var header = d3.keys(data[0])
      var id = header.indexOf('timestamp');
      if (id > -1) {header.splice(id, 1);}
      // console.log(header)
      // console.log(data)
      // TODO: give the user an option to select which ones he wants to plot
      // for now use hack

      // set limits of axes
      x.domain(d3.extent(data, function(d) { return d.timestamp; }));
      y.domain(d3.extent(data, function(d) { return d[fieldToPlot]; }));
      // console.log(data)
      myLine.datum(data)
          .attr("class", "line")
          .attr("d", line);
    });
}

// this may be a bit tricky - should be converted in the python parser maybe
// since D3 doesn't seem to support microseconds or tz in the PST format

var formatDate = d3.time.format("%Y-%m-%d %H:%M:%S.%L PST");

function typeTSData(d) {
  // console.log(d.timestamp)
  d.timestamp = formatDate.parse(d.timestamp);
  // console.log(d.timestamp)
  var headers = d3.keys(d)
  for (var i = 0; i < headers.length; i++){
    if (headers[i] != 'timestamp'){d[headers[i]] = +d[headers[i]];}
  }
  // console.log(d)
  return d;
}

svgPlotTS.attr("visibility", "collapse");
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