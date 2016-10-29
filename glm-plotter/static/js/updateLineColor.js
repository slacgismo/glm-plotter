// JAC - jdechalendar@stanford.edu
// Oct 27, 2016

// script to create and manipulate a slider that allows the user to play the simulation in time
// line colors are set according to value of voltage on the line

// initialize using the bar slider when the user gives a certain input
// d3.select("#updateLineColor").on("input", initializeLineColoring);

// create the bar slider and append it to main
var sliderDiv = d3.select("#main").append('div').attr("id", "sliderDiv").attr("style", "width: 960px;");
sliderDiv.append('label')
    .attr('for', 'time')
    .attr('style', "display: inline-block; align: left; width: 140px; text-align: right")
	.text("Time = ")
  .append('span')
  	.attr("id", "prettyTime");
var sliderDivInput = sliderDiv.append('input')
	.attr("type", "range")
	.attr("id", "curr_time")
	.attr("min", "240")
	.attr("max", "1440")
	.attr("style", "width:600px")
	.attr("value", "460");

// create callback
d3.select("#curr_time").on("input", changeLineColor);

// Flask endPoint where d3 will get the data for a given timestamp
function updateEndPoint() {
	console.log()
	return "/data/timestamp/" + document.getElementById('curr_time').value
	alue;
}

function update_slider(time) {
	var dateObj = new Date();
	dateObj.setHours(Math.floor(time/60));
	dateObj.setMinutes(time % 60);
	d3.select("#prettyTime")
		.text(dateObj.toTimeString().substring(0, 5));
}

// this function takes a real number as an input and outputs a color to represent that number
function colorMapping(val) {
	if (Math.abs(val - 50) < 40) {
		return 'green';
	} else if ((Math.abs(val - 50) >= 40) && ((Math.abs(val - 50) < 47))) {
		return 'orange';
	} else {
		return 'red';
	}
		
}

function changeLineColor() {
	update_slider(+document.getElementById("curr_time").value);
	endPoint = updateEndPoint();
	d3.csv(endPoint, function(error, data) {
		// select all the links and make the color of the link dependent on the data
		svgNetwork.selectAll(".link").each(function(d){
			// TODO: optimize this - very inefficient
			for (var i=0; i<data.length; i++){
				if (d.linkName == data[i].lineID) {
					d3.select(this).select('line')
					.attr('stroke', colorMapping(data[i].currentValue));
				}
			}
		});

	});
}
// changeLineColor();



