import numpy as np
from dfchatbox._hungarian import linear_sum_assignment
import requests
from django.core.cache import cache

def organise_entries(entries):
    json_entries = []
    names = []
    json_object = {}

    for counter,item in enumerate(entries):
        json_object_name = item['#0']['archetype_details']['template_id']['value']
        json_object_value = str(counter)

        if json_object_name in names:
            index = names.index(json_object_name)
            json_entries[index]['value'].append(json_object_value)
        else:
            json_object['name'] = json_object_name
            json_object['value'] = [json_object_value]
            json_entries.append(json_object)
            names.append(json_object_name)
            json_object = {}

    return json_entries

def translate(input):
    input=input.replace(",","").replace("("," ").replace(")"," ").replace("-"," ")
    url = "http://translate.dis-apps.ijs.si/translate?sentence="+input
    req = requests.get(url)
    if req.text == '{"errors": {"sentence": "Invalid text value provided"}}' or req.text[1:-3] == '':
        output=""
        words=input.split(" ")
        if(len(words)>1):
            for word in words:
                if word:
                    output+=translate(word)+" "
            return output
        return input
    return req.text[1:-3]


def levenshteinDistance(s1, s2):
    if len(s1) > len(s2):
        s1, s2 = s2, s1

    distances = range(len(s1) + 1)
    for i2, c2 in enumerate(s2):
        distances_ = [i2+1]
        for i1, c1 in enumerate(s1):
            if c1 == c2:
                distances_.append(distances[i1])
            else:
                distances_.append(1 + min((distances[i1], distances[i1 + 1], distances_[-1])))
        distances = distances_
    return distances[-1]



def selectMinimums(scores,phraseLength,hung):
    if len(scores) < int(0.75*phraseLength):
      minimums = []
      for i in range(phraseLength):
          minimums.append(float(sum(scores[:,i:(i+1)])))
      return minimums
    if hung == 1:
        a,b = linear_sum_assignment(scores)
        return [scores[a, b].sum()/phraseLength]


def weightedLevenshteinDistance(searchList,phrase,hung=0):
    new_searchList = []
    for i in range(len(searchList)):
        new_searchList += searchList[i].split(" ")
    phraseList = phrase.split(" ")
    phraseLength = len(phraseList) 
    
    scores = np.zeros((len(new_searchList),len(phraseList)))
    
    for i in range(len(new_searchList)):
        for j in range(len(phraseList)):
            scores[i][j] = levenshteinDistance(new_searchList[i],phraseList[j])

    minimums = selectMinimums(scores,phraseLength,hung) 
    return sum(minimums)/len(minimums)


def search_in_data(data,phrase,hung=0):
    fitsArray = []
    maxLev = float("inf")

    bestPerformers = []
    bestPerformersIndices = []
    
    for i in range(len(data)):
        a = [j.replace("|","/").split("/") for j in list(data[i].keys())]
        new_a = list(a)
    
        for k in range(len(a)):
            for l in range(len(a[k])):
                new_a[k][l] = "".join(c if c.isalpha() else " " for c in a[k][l]).strip()
                sequence = new_a[k][l].split(" ")
    
            searchString = " ".join(new_a[k])
            
            print("Comparing ",new_a[k]," to ",phrase,"....")
                
            LevDist = weightedLevenshteinDistance(new_a[k],phrase,hung=hung)

            print("Weighted Levenshtein distance is: ",LevDist,"\n")
            if LevDist == maxLev:
                bestPerformers.append(new_a[k])
                bestPerformersIndices.append([i,k])
                
            if LevDist < maxLev:
                bestPerformers = [new_a[k]]
                bestPerformersIndices = [[i,k]]
                fitsArray.append([searchString,LevDist])
                maxLev = LevDist
                bestFit = [new_a[k]]
        
    print("\n fitsArray: ")
    print(fitsArray[-1])
    print("\n Best performers:\n",bestPerformers)
    print("\n Best performers indices:\n",bestPerformersIndices)
    return bestPerformers,np.array(bestPerformersIndices)

def valuesOfBestPerformers(data,bestPerformers,bestPerformersIndices):
    if len(bestPerformers) > 1 and bestPerformers[0][-1] == "unit" or bestPerformers[0][-1] == "magnitude":
        for i in range(1,len(bestPerformers)):
            if len(bestPerformers[0]) == len(bestPerformers[i]) and bestPerformers[0][:-1] == bestPerformers[i][:-1]:
                print("We found his sibling! His sibling is:\n",bestPerformers[i])
                return str(list(data[bestPerformersIndices[0][0]].values())[bestPerformersIndices[0][1]]) + " " + str(list(data[bestPerformersIndices[i][0]].values())[bestPerformersIndices[i][1]])
        else:
            return list(data[bestPerformersIndices[0][0]].values())[bestPerformersIndices[0][1]]

def saveBestPerformersDataToCache(data,bestPerformersIndices):
    indicesList = list(set(np.array(bestPerformersIndices)[:,0]))
    cache.set("dataLength",len(indicesList),None)

    for i in range(len(indicesList)):
        cache.set("{}".format(i),data[indicesList[i]],None)