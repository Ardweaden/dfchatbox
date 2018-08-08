function setupNode(key_chain,value) {
   var newChild;
   for (var i = key_chain.length - 1; i >= 0; i--) {
        if (i == key_chain.length - 1) {
             newChild = {};
             newChild['name'] = key_chain[i];
             values = [];
             values.push({"name": value});
             newChild['children'] = values;
        }
        else {
             var newChildCopy = newChild;
             newChild = {};

             newChild['name'] = key_chain[i];
             newChild['children'] = [newChildCopy];
        }
   }

   return newChild
}


function addToNode(key_chain,node,node_path,value) {
   newChild = setupNode(key_chain,value);

   var exec_str = "node";

   for (var i = 0; i < node_path.length; i++) {
        exec_str += "[" + node_path[i] + "]['children']";
   }

   try {
        eval(exec_str + ".push(newChild)");
   }
   catch(err) {
        new_exec_str = exec_str;
        new_exec_str += "=[];"
        eval(new_exec_str);
        exec_str += ".push(newChild)";
        eval(exec_str);
   }

   return node
}

function createNodePath(i,key_chain,result) {
   node_path = [i];
   node = result[i]['children'];
   key_chain = key_chain.slice(1);

   var check = 0;

   for (var j = 0; j < key_chain.length; j++) {
        check = 0;
        for (var k = 0; k < node.length; k++) {
             if (key_chain[j] == node[k]['name']) {
                  node_path.push(k);
                  if (!!node[k]['children']) {
                       node = node[k]['children'];
                       check = 1;
                       break;
                  }
                  else {
                       node[k]['children'] = [];
                       check = 1;
                       break;
                  }
             }
        }
        if (!check) {
            break;
        }
   }

   return node_path
}

function array_move(arr, old_index, new_index) {
    if (new_index >= arr.length) {
        var k = new_index - arr.length + 1;
        while (k--) {
            arr.push(undefined);
        }
    }
    arr.splice(new_index, 0, arr.splice(old_index, 1)[0]);
    return arr; // for testing
};

function insertIntoKeychains(key_chain,key_chains,values) {
  for (var i = 0; i < key_chains.length; i++) {
    for (var j = 0; j < key_chains[i].length; j++) {
      if (j == key_chain.length) {
        key_chains.splice(i,0,key_chain);
        array_move(values,key_chains.length-1,i);

        return key_chains
      }
      if (key_chains[i][j] == key_chain[j]) {
        continue
      }
      else {
        break
      }
    }
  }
  key_chains.push(key_chain);
  return key_chains
}

function orderKeychains(keys,values) {
  var key_chains = [];

  for (var i = 0; i < keys.length; i++) {
    key_chain = keys[i].replace("|","/").replace("/_/g"," ").replace("/:0/g","").split("/");
    key_chains = insertIntoKeychains(key_chain,key_chains,values);
    console.log(key_chain);
  }

  return key_chains
}

function removeFromData(key_chains,values,categories,subcategories) {
  for (var i = 0; i < key_chains.length; i++) {
    if (categories.includes(key_chains[i][1])) {
      key_chains.splice(i,1);
      values.splice(i,1);
      i -= 1;
    }
    else {
      for (var j = 0; j < subcategories.length; j++) {
        if (key_chains[i].includes(subcategories[j])) {
          key_chains.splice(i,1);
          values.splice(i,1);
          i -= 1;
          break
        }
      }
    }
  }
}

function getEntryTime(key_chains,values) {
  for (var i = 0; i < key_chains.length; i++) {
     if (key_chains[i][key_chains[i].length - 1] == "time" || key_chains[i][key_chains[i].length - 1] == "start_time") {
      return values[i]
     }
   }

  return "No date" 
}


function parseTree(data) {
  var result = [];

  var keys = Object.keys(data);
  var values = Object.values(data);
  var categories = ["_uid","language","context","category"];
  var subcategories = ["terminology","code","time"];

  key_chains = orderKeychains(keys,values);

  var entry_time = getEntryTime(key_chains,values);

  removeFromData(key_chains,values,categories,subcategories);

  for (var i = 0; i < key_chains.length; i++) {
      key_chain = key_chains[i];
      value = values[i];

      for (var j = 0; j < result.length; j++) {
           if (result[j]['name'] == key_chain[0]){
                node_path = createNodePath(j,key_chain,result);
                result = addToNode(key_chain.slice(node_path.length),result,node_path,value);
                break;
           }
           else {
                if (j == result.length - 1) {
                     result.push(setupNode(key_chain,value));
                     break;
                }
           }
      }

      if (result.length == 0) {
           result.push(setupNode(key_chain,value));
      }
  }

  return [result,entry_time]
}