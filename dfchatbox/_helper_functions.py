import numpy as np
from dfchatbox._hungarian import linear_sum_assignment
import requests
from django.core.cache import cache
import base64
from dfchatbox.models import Patient

import json
import apiai


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

def strippedKeys(data):
    keys2 = []

    keys = [i.replace("|","/").split("/") for i in data.keys()]
    for i in range(len(keys)):
        line = ""
        for j in range(len(keys[i])):
            line += " " + "".join(c if c.isalpha() else " " for c in keys[i][j]).strip()
        keys2.append(line.strip().split(" "))

    return keys2

# def valuesOfBestPerformers(data,bestPerformers,bestPerformersIndices):
#     if len(bestPerformers) > 1 and bestPerformers[0][-1] == "unit" or bestPerformers[0][-1] == "magnitude":
#         for i in range(1,len(bestPerformers)):
#             if len(bestPerformers[0]) == len(bestPerformers[i]) and bestPerformers[0][:-1] == bestPerformers[i][:-1]:
#                 print("We found his sibling! His sibling is:\n",bestPerformers[i])
#                 return str(list(data[bestPerformersIndices[0][0]].values())[bestPerformersIndices[0][1]]) + " " + str(list(data[bestPerformersIndices[i][0]].values())[bestPerformersIndices[i][1]])
#         else:
#             return str(list(data[bestPerformersIndices[0][0]].values())[bestPerformersIndices[0][1]])
#     else:
#         return str(list(data[bestPerformersIndices[0][0]].values())[bestPerformersIndices[0][1]])

# def valuesOfBestPerformers(data,bestPerformers,bestPerformersIndices):
#     print("Getting values ....")
#     bestPerformer = []

#     for i in range(len(bestPerformers[0])):
#         bestPerformer += bestPerformers[0][i].split(" ")

#     print(bestPerformer)
#     if bestPerformer[-1] == "unit" or bestPerformer[-1] == "magnitude":
#         keys = strippedKeys(data[bestPerformersIndices[0][0]])
#         for i in range(len(keys)):
#             print(keys[i])
#             if len(bestPerformer) == len(keys[i]) and bestPerformer[:-1] == keys[i][:-1] and bestPerformer[-1] != keys[i][-1]:
#                 print("We found his sibling! His sibling is:\n",keys[i])
#                 if bestPerformer[-1] == "magnitude":
#                     return str(list(data[bestPerformersIndices[0][0]].values())[bestPerformersIndices[0][1]]) + " " + str(list(data[bestPerformersIndices[0][0]].values())[i])
#                 else:
#                     return str(list(data[bestPerformersIndices[0][0]].values())[i]) + " " + str(list(data[bestPerformersIndices[0][0]].values())[bestPerformersIndices[0][1]])
#         else:
#             print("No sibling was found.")
#             return str(list(data[bestPerformersIndices[0][0]].values())[bestPerformersIndices[0][1]])
#     else:
#         return str(list(data[bestPerformersIndices[0][0]].values())[bestPerformersIndices[0][1]])

def valuesOfBestPerformers(data,bestPerformers,bestPerformersIndices):
    print("Getting values ....")

    values = []

    for j in range(len(bestPerformers)):
        bestPerformer = []
        siblings = []

        for i in range(len(bestPerformers[j])):
            bestPerformer += bestPerformers[j][i].split(" ")

        #print(bestPerformer)
        if bestPerformer[-1] == "unit" or bestPerformer[-1] == "magnitude":
            keys = strippedKeys(data[bestPerformersIndices[j][0]])
            for i in range(len(keys)):
                #print(keys[i])
                if len(bestPerformer) == len(keys[i]) and bestPerformer[:-1] == keys[i][:-1] and bestPerformer[-1] != keys[i][-1] and keys[i] not in siblings:
                    #print("We found his sibling! His sibling is:\n",keys[i])
                    siblings.append(keys[i])
                    if bestPerformer[-1] == "magnitude":
                        values.append(str(list(data[bestPerformersIndices[j][0]].values())[bestPerformersIndices[j][1]]) + " " + str(list(data[bestPerformersIndices[j][0]].values())[i]))
                        break
                        #return str(list(data[bestPerformersIndices[j][0]].values())[bestPerformersIndices[j][1]]) + " " + str(list(data[bestPerformersIndices[j][0]].values())[i])
                    else:
                        values.append(str(list(data[bestPerformersIndices[j][0]].values())[i]) + " " + str(list(data[bestPerformersIndices[j][0]].values())[bestPerformersIndices[j][1]]))
                        break
                        #return str(list(data[bestPerformersIndices[j][0]].values())[i]) + " " + str(list(data[bestPerformersIndices[j][0]].values())[bestPerformersIndices[j][1]])
            else:
                print("No sibling was found.")
                values.append(str(list(data[bestPerformersIndices[j][0]].values())[bestPerformersIndices[j][1]]))
                #return str(list(data[bestPerformersIndices[j][0]].values())[bestPerformersIndices[j][1]])
        else:
            values.append(str(list(data[bestPerformersIndices[j][0]].values())[bestPerformersIndices[j][1]]))
            continue
            #return str(list(data[bestPerformersIndices[j][0]].values())[bestPerformersIndices[j][1]])

    return values

def saveBestPerformersDataToCache(data,bestPerformersIndices):
    indicesList = list(set(np.array(bestPerformersIndices)[:,0]))
    print("\n\ndata length is: ",len(indicesList),"\n\n")
    cache.set("dataLength",len(indicesList),None)

    for i in range(len(indicesList)):
        cache.set("{}".format(i),data[indicesList[i]],None)


def allPatients():
    baseUrl = 'https://rest.ehrscape.com/rest/v1'
    ehrId = ''
    base = base64.b64encode(b'ales.tavcar@ijs.si:ehrscape4alestavcar')
    authorization = "Basic " + base.decode()

    aql = "/query?aql=select e/ehr_id from EHR e contains COMPOSITION a"

    queryUrl = baseUrl + aql

    print(queryUrl)

    r = requests.get(queryUrl, headers={"Authorization": authorization, 'content-type': 'application/json'})

    if r.status_code == 200:
        js = json.loads(r.text)

        return js
    else:
        return 0

def patientName(ehrId):
    base = base64.b64encode(b'ales.tavcar@ijs.si:ehrscape4alestavcar')
    authorization = "Basic " + base.decode()
    r = requests.get("https://rest.ehrscape.com/rest/v1/demographics/party/query/?ehrId={}".format(ehrId),headers={"Authorization": authorization, 'content-type': 'application/json'})
    if r.status_code != 200:
        return
    js = json.loads(r.text)
    return js["parties"][0]["firstNames"].lower(),js["parties"][0]["lastNames"].lower()


def closestPatientName(enteredName,database=0):
    enteredName = enteredName.lower()
    bestPerformers = []
    ehrids = []
    minimum = 999

    if not database:
        patients = allPatients()

        for ehrid in patients['resultSet']:
            ehrids.append(ehrid["#0"]["value"])


        for ehrid in set(ehrids):
            patient_name = patientName(ehrid)
            if patient_name == None:
                continue
            else:
                LevDist = weightedLevenshteinDistance(list(patient_name),enteredName,hung=1)
                if LevDist <= minimum:
                    bestPerformers.append(patient_name)
                    minimum = LevDist
                print("Weighted Levenshtein distance between ",enteredName," and ",list(patient_name)," is: ",LevDist)
    else:
        patientNames = list(Patient.objects.values("name","surname"))
        for i in patientNames:
            LevDist = weightedLevenshteinDistance(list((i["name"],i["surname"])),enteredName,hung=1)

            if LevDist <= minimum:
                bestPerformers.append((i["name"],i["surname"]))
                minimum = LevDist
            print("Weighted Levenshtein distance between ",enteredName," and ",list((i["name"],i["surname"]))," is: ",LevDist)

    print(bestPerformers)
    print(minimum)
    return bestPerformers

def getECGpdfLink(data):
    data = str(data)

    lower = re.search("'uri': {'@class': 'DV_URI', 'value': '",data).span()[1]

    if not lower:
        return None
    else:
        lower = lower.span()[1]

    data = data[lower:]

    upper = re.search("'",data)

    if not upper:
        return None
    else:
        upper = upper.span()[0]

    data = data[:upper]

    print(data)

    return "https://rest.ehrscape.com/store/rest" + data