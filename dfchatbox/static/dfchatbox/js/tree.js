var tables = [];
var dates = [];
    
for (var i = 0; i < data.length; i++) {
    tree_data = data[i];
    converted = parseTree(tree_data);

    tree = converted[0];
    entry_time = converted[1];

    if (entry_time != "No date") {
        unix_time = dates.push(Date.parse(entry_time));
    }
    else {
        dates.push(entry_time)
    }

    tabledata = tableFromTreeWithColspan([tree]);

    tablearray = tabledata[0];
    colspanMatrix = rectangulateArray(tabledata[1]);

    tablee = rectangulateArray(tablearray);

    widthMatrix = calculateWidth(tablee);

    shownTable = tableFromArray(tablee,colspanMatrix,widthMatrix);

    tables.push("<table id='entryTable" + i + "' class='table table-bordered table-striped' style='width: 98%;margin-left: 1%;margin-right: 1%;'>" + shownTable + "</table><br>");

}

dates = sortWithIndices(dates);
sort_indices = dates.sortIndices;

for (var i = 0; i < dates.length; i++) {
    if (dates[i] != "No date") {
        entry_time = new Date(dates[i]).toLocaleDateString();
    }
    else {
        entry_time = "Ni znan"
    }
    $("#tableHolder").append("<p style='margin-left: 5%;'>Datum vpisa: " + entry_time + "</p><br>");
    $("#tableHolder").append(tables[sort_indices[i]]);
}

$("tr").addClass("collapse");
$("tbody tr:first-child").removeClass("collapse");


$("tbody tr:first-child").click(function(){
    $(this).siblings(".collapse").toggleClass('show');
});

////////////////////////////////// CHARTS //////////////////////////////////////////

var rowsToChart = rowsToGraph(data);
var rows = rowsToChart[0];
var units = rowsToChart[1];
var maxLen = 0;

dataSet = [];

if (rowsToChart.length > 0) {

    for (var c = 0; c < rows.length; c++) {
            
        chartData = [];

        var validE = validEntries(data,rowsToGraph(data)[0][c])
        var valid = validE[0];
        var validData = validE[1];
        var title = generateTitle(Object.keys(data[0])[rows[c]]);

        var chartData = [];

        for (var i = 0; i < valid.length; i++) {
            chartData.push({x: new Date(dates[i]) ,y: validData[i]});
        }

        if (chartData.length > maxLen) {
            maxLen = chartData.length
        }

        if (c == 0) {
            dataSet.push({
                label: title,
                data: chartData,
                backgroundColor: [
                    //'#d3d8ea'
                    'rgba(211, 216, 234, 0.4)',
                ],
                borderColor: [
                    'rgba(211, 216, 234, 1)',
                ],
                borderWidth: 1,
                borderDash: [10,5],
            });
            var unit = units[0];


        }
        else {
            dataSet.push({
                label: title,
                data: chartData,
                backgroundColor: [
                    //'#d3d8ea'
                    'rgba(211, 216, 234, 0.4)',
                ],
                borderColor: [
                    'rgba(211, 216, 234, 1)',
                ],
                borderWidth: 1,
                borderDash: [10,5],
                hidden: true,
            })
        }
        
    }

    if (maxLen > 1) {
        $("#btnHolder").append('<button class="btn btn-default" id="chartBtn">Prikaži graf vrednosti</button>')
    }


    var ctx = document.getElementById("chart").getContext('2d');
    Chart.defaults.global.defaultFontSize = 25;

    var myChart = new Chart(ctx, {
        type: 'line',
        data: {
            datasets: dataSet
        },
        options: { 
            elements: {
                line: {
                    tension: 0,
                }
            },
            title: {
                display: false,
                text: title,
                fontSize: 40
            },
            tooltips: {
                titleFontSize: 30,
                bodyFontSize: 30
              },
            scales: {
                xAxes: [{
                  type: 'time',
                  time: {
                    unit: 'day',
                    unitStepSize: 2,
                    displayFormats: {
                       'day': 'DD-MM-YYYY'
                        }
                    },
                    ticks: {
                        fontSize: 20,
                    },
                }],
                yAxes: [{
                    ticks: {
                        fontSize: 25,
                    },
                    scaleLabel: {
                        display: true,
                        labelString: unit,
                        fontSize: 30,
                        padding: 50
                      }
                }]
            }
        }
    });

    //Spremenil zakomentiral rotation = isLeft ? -0.5 * Math.PI : 0.5 * Math.PI;

    $("#chartBtn").click(function() {
        $("#chartsHolder").toggleClass("show");

    });

    var prev_hidden = [1,2,3,4,5,6];


    $("#chart").click(function() {
        new_hidden = getHiddenDatasets(myChart);

        if (new_hidden.length < prev_hidden.length) {
            newElement = $(prev_hidden).not(new_hidden).get()[0];
            if (unit != units[newElement]) {
                unit = units[newElement];

                for (var i = 0; i < myChart.data.datasets.length; i++) {
                    if (!new_hidden.includes(i) && units[i] != unit) {
                        if (i == 0) {
                            meta = myChart.getDatasetMeta(i);
                            meta.hidden = true;
                        }
                        else {
                            meta = myChart.getDatasetMeta(i);
                            meta.hidden = null;
                        }
                    }
                }

                myChart.options.scales.yAxes[0].scaleLabel.labelString = unit;

                myChart.update();
            }
        }

        prev_hidden = getHiddenDatasets(myChart);

    });
}