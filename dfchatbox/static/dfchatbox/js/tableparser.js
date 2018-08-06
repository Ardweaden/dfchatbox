//Generates an array from the tree (Use tableFromTreeWithColspan)
function tableFromTree(tree) {
  tableArray = [];

  while(true){
    row = [];
    offspring = []

    if (tree.length == 0) {
      break
    }

    for (var i = 0; i < tree.length; i++) {
      branch = [];

      for (var j = 0; j < tree[i].length; j++) {
        branch.push(tree[i][j]['name'].replace("_"," ").replace(":0",""));

        if (!!tree[i][j]['children']){
          offspring.push(tree[i][j]['children']);
        }
        else {
          offspring.push([]);
        }
      }
      row.push(branch);
    }
    tableArray.push(row);
    tree = offspring;
  }

  return tableArray
}

//Calculates the length of a row
function rowLength(row) {
  rowLen = 0;

  for (var i = 0; i < row.length; i++) {
    rowLen += row[i].length
  }

  return rowLen
}

//Generates a HTML string for the table from the array
function tableFromArray(array,colspanMatrix,widthMatrix){
  tableString = "";

  previousWidth = 100;

  for (var i = 0; i < (array.length - 1); i++) {
    row = "";

    for (var j = 0; j < array[i].length; j++) {

      if (array[i][j].length == 0) {
        row += "<th class='empty' colspan='1' width='" + widthMatrix[i][j][0] + "%'>&nbsp;</td>";
      }

      for (var k = 0; k < array[i][j].length; k++) {

        try {
          if (!!colspanMatrix[i][j][k]) {
            colspan = colspanMatrix[i][j][k];
          }
          else {
            colspan = 1;
          }
        }
        catch (err) {
          colspan = 1;
        }

        elementIndex = j + calculateShift(array[i],j);

        if (array[i+1][elementIndex].length == 0) {
          row += "<th class='value' colspan='" + colspan + "' width='" + widthMatrix[i][j][k] + "%'>" + array[i][j][k].replace("_"," ").replace(":0","") + "</td>";
        }
        else {
          row += "<th colspan='" + colspan + "' width='" + widthMatrix[i][j][k] + "%'>" + array[i][j][k].replace("_"," ").replace(":0","") + "</td>";
        }
      } 

    }
    row = "<tr>" + row + "</tr>";
    tableString += row;
  }

  return tableString;
}

//Calculates how many more than 1 elements are there in all branches of a row
function calculateShift(row,j) {
  shift = 0;
  for (var i = 0; i < j; i++) {
    if (row[i].length > 1) {
      shift += (row[i].length - 1)
    }
  }

  return shift
}

//Adds in empty elements in missing places
function rectangulateArray(array) {
  for (var i = 0; i < (array.length - 1); i++){ 

    for (var j = 0; j < array[i].length; j++) {

      if (array[i][j].length == 0) {
        shift = calculateShift(array[i],j);
        array[i+1].splice(j + shift,0,[]);
      }
    }
  }
  return array
}

//Calculates the number of leaves of a tree, which is colspan
function calculateColspan(tree,colspan){
  for (var i = 0; i < tree.length; i++) {
    if (!!tree[i]['children']) {
      colspan += calculateColspan(tree[i]['children'],0);
    }
    else {
      colspan += 1;
    }
  }
  return colspan;
}

//Converts tree to an array and generates the colspan matrix for <th> tags.
//colspanMatrix needs to be rectangulated before usage 
function tableFromTreeWithColspan(tree) {
  tableArray = [];
  colspanMatrix = [];

  while(true){
    row = [];
    colspanRow = [];
    offspring = [];

    if (tree.length == 0) {
      break
    }

    for (var i = 0; i < tree.length; i++) {
      branch = [];
      colspanBranch = [];

      for (var j = 0; j < tree[i].length; j++) {
        branch.push(tree[i][j]['name']);
        colspanBranch.push(calculateColspan([tree[i][j]],0));

        if (!!tree[i][j]['children']){
          offspring.push(tree[i][j]['children']);
        }
        else {
          offspring.push([]);
        }
      }
      row.push(branch);
      colspanRow.push(colspanBranch);
    }
    tableArray.push(row);
    colspanMatrix.push(colspanRow);
    tree = offspring;
  }

  return [tableArray,colspanMatrix]
}


//Gets the width of index-th <th> tag
function getElementWidth(row,index) {
  counter = 0;
  for (var i = 0; i < row.length; i++) {
    for (var j = 0; j < row[i].length; j++) {
      if (counter == index) {
        return row[i][j]
      }
      counter += 1;
    }
  }
}

//Method for creating a clone of an array
Array.prototype.clone = function() {
  var arr = this.slice(0);
  for( var i = 0; i < this.length; i++ ) {
      if( this[i].clone ) {
          arr[i] = this[i].clone();
      }
  }
  return arr;
}

//Creates a width matrix for <th> tags in the table.
//Width of a child is the width of the parent divided by the number of children
function calculateWidth(array) {
  var widthMatrix = array.clone();
  widthMatrix[0][0][0] = 100;

  for (var i = 1; i < array.length; i++) {
    for (var j = 0; j < array[i].length; j++) {
      parentElementWidth = getElementWidth(widthMatrix[i-1],j);
      newLength = parentElementWidth/array[i][j].length;

      if (array[i][j].length == 0) {
        widthMatrix[i][j].push(parentElementWidth);
      }
      else {
        for (var k = 0; k < array[i][j].length; k++) {
          widthMatrix[i][j][k] = newLength;
        }
      }
    }
  }

  return widthMatrix
}

function sortWithIndices(toSort) {
  for (var i = 0; i < toSort.length; i++) {
    toSort[i] = [toSort[i], i];
  }
  toSort.sort(function(left, right) {
    return left[0] < right[0] ? -1 : 1;
  });
  toSort.sortIndices = [];
  for (var j = 0; j < toSort.length; j++) {
    toSort.sortIndices.push(toSort[j][1]);
    toSort[j] = toSort[j][0];
  }
  return toSort;
}