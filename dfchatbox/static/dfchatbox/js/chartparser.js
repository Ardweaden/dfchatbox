function rowsToGraph(data) {
	var test = data[0];
	var keys = Object.keys(test);
	var values = Object.values(test);

	var rows = [];
	var units = [];

	keychains = []

	for (var i = 0; i < keys.length; i++) {
		keychains.push(keys[i].replace("|","/").replace("_"," ").replace(":0","").split("/"));
	}

	for (var i = 0; i < keychains.length; i++) {
		if (keychains[i][keychains[i].length - 1] == "magnitude") {
			rows.push(i);
			units.push(getRowUnit(keychains,i,values))
		}
	}
	return [rows,units]
}


function getRowUnit(keychains,i,values) {
	if (i > 0) {
		if (keychains[i-1][keychains[i-1].length - 1] == "unit") {
			return values[i-1]
		}
	}
	if (i < values.length - 1) {
		if (keychains[i+1][keychains[i+1].length - 1] == "unit") {
			return values[i+1]
		}
	}
	return ""
}

function validEntries(data,row){
	var valid = [];

	var valid_keys = Object.keys(data[0]);
	var searched_key = valid_keys[row];
	var row_data = [];

	for (var i = 0; i < data.length; i++) {
		keys = Object.keys(data[i]);
		values = Object.values(data[i]);

		if (keys.indexOf(searched_key) != -1) {
			valid.push(i);
			row_data.push(values[keys.indexOf(searched_key)])
		}

	}
	return [valid,row_data]
}

function generateTitle(row) {
	var titleArray = [];
	var keychain = row.replace("|","/").replace("_"," ").replace(":0","").split("/");
	var len = keychain.length;
	titleArray.push(keychain[len - 2].replace(/[^0-9a-z]/gi, ' ').replace(/[0-9]/g, ''));
	titleArray.push(keychain[len - 4].replace(/[^0-9a-z]/gi, ' ').replace(/[0-9]/g, ''));
	return titleArray.join(" - ");

}

function getHiddenDatasets(chart) {
	var hidden = [];
	for (var i = 0; i < chart.data.datasets.length; i++) {
		meta = chart.getDatasetMeta(i);
		if (i == 0 && meta.hidden == true) {
			hidden.push(i)
		}
		else if (meta.hidden == null  && i != 0) {
			hidden.push(i)
		}
	}
	return hidden
}