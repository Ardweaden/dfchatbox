from django.shortcuts import render,redirect
from django.conf import settings
from django.views.decorators.http import require_http_methods
from django.http import HttpResponse,JsonResponse
from django.core import serializers
from django.views.decorators.csrf import csrf_exempt
from django.core.cache import cache
from django.contrib.auth import login,authenticate,logout
from django.contrib.auth.models import User

from dfchatbox._helper_functions import *
from dfchatbox.models import Patient,Doctor

import re
import imgkit
import string
import random
from PIL import Image
from lxml.html import fromstring
import json
from bs4 import BeautifulSoup
import urllib3
import apiai
import requests
import base64
from datetime import datetime
import numpy as np
from dfchatbox._auth import credentials,CLIENT_ACCESS_TOKEN

# Create your views here.
# -*- coding: utf-8 -*-

@require_http_methods(['POST','GET'])
def index(request):
	if request.method == 'POST':
		message = request.POST['message']
		sessionID = request.POST['sessionID']


		patientInfo_patientName = None
		patientInfo_patientSurname = None
		patientInfo_patientEhrid = None
		patientInfo_isDoctor = False

		#print("*****SESSION ID*****   ",sessionID)

		#print("\n\n*****USER STATUS*****\nUser: ",request.user,"\nIs authenticated: ",request.user.is_authenticated,"\n\n")

		user_status = request.user.is_authenticated

		if user_status:

			if hasattr(request.user,"doctor"):
				patientInfo_isDoctor = True
				patientInfo_patientName = request.user.doctor.name
				patientInfo_patientSurname = request.user.doctor.surname
			else:
				patientInfo_isDoctor = False
				patientInfo_patientName = request.user.patient.name
				patientInfo_patientSurname = request.user.patient.surname
				patientInfo_patientEhrid = request.user.patient.ehrid


		if message[:5] != "getE ":
			#BECAUSE IJS SERVER ISN'T WORKING OTHER API
			translation = translate(message,api_link="http://translation-api.docker-e9.ijs.si/translate?sentence=",yandex=True)

			if translation != "":
				message = translation

		#print("*** message: ",message,"***\n")

		contexts = [{
		  "lifespan": 5,
		  "name": "user_data",
		  "parameters": {
		  "is_authenticated": user_status,
		  "user_ehrid": patientInfo_patientEhrid,
		  "user_patientName": patientInfo_patientName,
		  "user_patientSurname": patientInfo_patientSurname,
		  "user_isDoctor": patientInfo_isDoctor
		  }
		}]

		ai = apiai.ApiAI(CLIENT_ACCESS_TOKEN)

		request = ai.text_request()
		request.session_id = sessionID
		request.lang = 'en'
		request.contexts = contexts
		request.parameters = {"is_authenticated":user_status}
		request.query = message

		data = request.getresponse().read().decode('utf-8')

		answer_json = json.loads(data)

		print(answer_json)

		text_answer = answer_json['result']['fulfillment']['messages'][0]['speech']

		#print(text_answer)

		data = ""
		response_type = ""
		url = ""

		if 'data' in answer_json['result']['fulfillment']:
		    data = answer_json['result']['fulfillment']['data']['data']
		    response_type = answer_json['result']['fulfillment']['data']['responseType']
		    #print("RESPONSE TYPE: ",response_type)
		    url = answer_json['result']['fulfillment']['data']['url']
		    if url[:5] != "https" and url[0] != "/": 
		    	url = "https:" + url[5:]

		    

		#print("data: ",data)

		return HttpResponse('{{"text_answer":"{0}","response_type":"{1}","data":"{2}","url":"{3}"}}'.format(text_answer,response_type,data,url))
	else:
		return render(request,'dfchatbox/index.html')
	

@require_http_methods(['POST'])
def check_links(request):
	# Not in use currently
	if request.method == 'POST':
		message = request.POST['message']

		urls = re.findall("((https://www|http://www|www\.|http://|https://).*?(?=(www\.|http://|https://|$)))", message)

		#print("These are the urls: ", urls)

		if len(urls) != 0:
			url = urls[0][0]

			#print("We'll check this url: ", url)

			html = requests.get(url)

			# soup = BeautifulSoup(html.text,"lxml")

			# file_name = ''.join(random.choices(string.ascii_uppercase + string.digits, k=20)) + ".html"
			# file = "dfchatbox/static/dfchatbox/data/" + file_name

			# with open(file, "w", encoding='utf8') as f:
			# 	f.write(str(soup))

			tree = fromstring(html.content)
			title = tree.findtext('.//title')
			title = title.replace('"','\\"')

			image_name = ''.join(random.choices(string.ascii_uppercase + string.digits, k=20)) + ".jpg"
			image_path = "dfchatbox/static/dfchatbox/img/" + image_name

			#config = imgkit.config(wkhtmltoimage='C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltoimage.exe')
			options = {'zoom': '1.2', 'width': '500', 'height': '500'}
			#imgkit.from_url(url,image_path,config=config,options=options)
			imgkit.from_url(url,image_path,options=options)

			img = Image.open(image_path)

			return HttpResponse('{{"url":"{0}", "data":"{1}", "image_name":"{2}"}}'.format(url,title,image_name))

		else:
			return HttpResponse(urls)

@require_http_methods(['GET'])
def entry_tree(request):
	dataLength = cache.get("dataLength")
	cache.delete("dataLength")
	#print("\n=== DATA LENGTH @ ENTRY_TREE: ===>  ", dataLength,"\n")
	dataList = []

	for i in range(int(dataLength)):
		dataList.append(cache.get('{}'.format(i)))
		cache.delete('{}'.format(i))

	return render(request,'dfchatbox/tree.html',{'data': json.dumps(dataList)})

def login_page(request):
	#print("Let's log in! Username: ", request.POST["username"],", password: ",request.POST["password"])

	if request.method == "POST":
		user = authenticate(username=request.POST["username"], password=request.POST["password"])

		if user is not None:
			login(request, user)
			#print("\n\nUser is authenticated: ",request.user.is_authenticated,"\n\n")

			#	GET NAME, SURNAME AND EHRID FROM DATABASE
			#	FOR NOW I'LL HAVE DEFAULTS
			# name = "mary"
			# surname = "wilkinson"
			# ehrid = "d8dcc924-edaf-4df5-8b84-e9e6d0ec590f"

			if hasattr(user,"doctor"):
				isDoctor = True
				name = user.doctor.name
				surname = user.doctor.surname
				ehrid = ""
				patients = user.doctor.patient_set.all()
				patients = [patient.name + " " + patient.surname for patient in patients]
				patients = json.dumps(patients)
			else:
				isDoctor = False
				name = user.patient.name
				surname = user.patient.surname
				ehrid = user.patient.ehrid
				patients = []


			return JsonResponse(json.dumps({'success': 1, 'message': 'Prijava je bila uspešna',"username": request.POST["username"], "name": name, "surname": surname, "ehrid": ehrid, "isDoctor": isDoctor, "patients": patients}),safe=False)
		else:
			return JsonResponse(json.dumps({'success': 0, 'message': 'Napačno ime ali geslo',"username": "Uporabnik"}),safe=False)

def logout_page(request):

	if request.method == "POST":
		logout(request)
		return JsonResponse(json.dumps({'success': 1, 'message': 'Odjava je bila uspešna',"username": "Uporabnik"}),safe=False)


def webhook(request):

	answer_json = json.loads(request.body)
	
	print("=========== WEBHOOK =============")

	print("\n\n ******************************************* \n\n ")
	print(answer_json)
	#print(request.user.is_authenticated)
	#print(request.user)
	#print(request)
	print("\n\n ******************************************* \n\n ")


	parameter_action = answer_json['queryResult']['action']
	json_response = {}
	response_data = {}
	warning = ""
	answer = "Prosim ponovno postavite zahtevo."
	session = answer_json["session"] + "/contexts/"
	#print("\nFull access: ",fullAccess,"\n")

	#	Checks if user is logged in
	if [context for context in answer_json["queryResult"]["outputContexts"] if context["name"] == session + "user_data"][0]["parameters"]["is_authenticated"] == "false" and parameter_action != "patientInfo" and parameter_action != "getHelp":
		print("$$$ HERE $$$")
		json_response = {"responseType": "not-authenticated"}
		json_response['data'] = ""
		json_response['url'] = "/"
		response_data['fulfillmentText'] = "Za iskanje se morate prijaviti."
		#response_data['displayText'] = "Za iskanje se morate prijaviti."
		response_data['payload'] = json_response
		response_data['source'] = "thinkEHR"
		print(response_data)
		return HttpResponse(
			json.dumps(response_data, indent=4),
			content_type="application/json"
			)

	fullAccess = PermissionCompliant(answer_json)
	answer_json["fullAccess"] = fullAccess

	if parameter_action == "labResults":
		print("labResults")
		json_response = getLabResultsData(answer_json)
	if parameter_action == "patientInfo":
		print("patientInfo")
		json_response = getPatientInfoData(answer_json)
	if parameter_action == "ECGResults":
		print("ECGResults")
		json_response = getECGResultsData(answer_json)
	if parameter_action == "allEntries":
		print("allEntries")
		json_response = getAllEntries(answer_json)
		print("\n$$$$$$$$$$$$$$$$$$$$\n",json_response,"\n$$$$$$$$$$$$$$$$$$$$\n")
		#response_data["fulfillmentMessages"] = [{"ehrid": json_response["ehrid"]}]
		#response_data['ehrid'] = json_response['ehrid']
		#del json_response['ehrid']
	if parameter_action == "getEntry":
		print("getEntry")
		json_response = getEntryData(answer_json)
		print(json_response)
	if parameter_action == "searchEntries":
		print("searchForEntry")
		json_response = searchForEntry(answer_json)
		print(json_response)
	if parameter_action == "myPatients":
		print("myPatients")
		json_response = getMyPatients(answer_json)
		print(json_response)
	if parameter_action == "myDoctor":
		print("myDoctor")
		json_response = getMyDoctor(answer_json)
		print(json_response)
	if parameter_action == "getHelp":
		print("getHelp")
		json_response = getHelp()

	if "new_name" in json_response:
		new_name = json_response["new_name"]
		del json_response["new_name"]
		new_lastname = json_response["new_lastname"]
		del  json_response["new_lastname"]
		response_data["outputContexts"] = answer_json["queryResult"]["outputContexts"]

		for context in response_data["outputContexts"]:
			context["parameters"]["given-name"] = new_name
			context["parameters"]["last-name"] = new_lastname

	answer = json_response['answer']
	del json_response['answer']
	# response_data['speech'] = warning + answer
	# response_data['displayText'] = answer
	# response_data['data'] = json_response
	# response_data['source'] = "thinkEHR"
	# print("\n\n ******************************************* \n\n ")
	#print(response_data)
	#print("\n\n ******************************************* \n\n ")
	#print("=========== END WEBHOOK =============")

	response_data['fulfillmentText'] = warning + answer
	#response_data["fulfillmentMessages"] = [{"text": [answer]}]
	response_data['payload'] = json_response
	response_data['source'] = "thinkEHR"
	print(response_data)
	print("\n\n ******************************************* \n\n ")
	
	return HttpResponse(
			json.dumps(response_data, indent=4),
			content_type="application/json"
			)

def PermissionCompliant(answer_json):
	#print("\n***contexts: ",answer_json["queryResult"]["outputContexts"],"***\n")
	session = answer_json["session"] + "/contexts/"
	is_authenticated = [context for context in answer_json["queryResult"]["outputContexts"] if context["name"] == session + "user_data"][0]["parameters"]["is_authenticated"]

	if is_authenticated == "false":
		return False

	isDoctor = [context for context in answer_json["queryResult"]["outputContexts"] if context["name"] == session + "user_data"][0]["parameters"]["user_isDoctor"]

	if isDoctor == "true":
		name = [context for context in answer_json["queryResult"]["outputContexts"] if context["name"] == session + "user_data"][0]["parameters"]["user_patientName"]
		surname = [context for context in answer_json["queryResult"]["outputContexts"] if context["name"] == session + "user_data"][0]["parameters"]["user_patientSurname"]

		user = Doctor.objects.get(name=name,surname=surname)

		return user.fullAccess
	
	else:
		name = [context for context in answer_json["queryResult"]["outputContexts"] if context["name"] == session + "user_data"][0]["parameters"]["user_patientName"]
		surname = [context for context in answer_json["queryResult"]["outputContexts"] if context["name"] == session + "user_data"][0]["parameters"]["user_patientSurname"]

		user = Patient.objects.get(name=name,surname=surname)

		return user.fullAccess

def getPatientInfoData(answer_json):

	baseUrl = 'https://rest.ehrscape.com/rest/v1'
	base = base64.b64encode(credentials)
	authorization = "Basic " + base.decode()

	queryUrl = baseUrl + "/demographics/party/query"

	json_response = {"responseType": "userInfo"}
	json_object = {}
	searchData = []

	parameter_name =answer_json['queryResult']['parameters']['given-name']
	parameter_last_name =answer_json['queryResult']['parameters']['last-name']

	if parameter_name != "":
		searchData.append({"key": "firstNames", "value": parameter_name})
	if parameter_last_name != "":
		searchData.append({"key": "lastNames", "value": parameter_last_name})

	#print("queryUrl: ", queryUrl)
	#print("searchData: ", searchData)

	r = requests.post(queryUrl, data=json.dumps(searchData), headers={"Authorization": authorization, 'content-type': 'application/json'})

	if r.status_code == 200:
		js = json.loads(r.text)
		json_object["name"] = js['parties'][0]['firstNames']
		json_object["lastname"] = js['parties'][0]['lastNames']
		json_object["gender"] = js['parties'][0]['gender']
		json_object["dateofbirth"] = js['parties'][0]['dateOfBirth']

		answer = "Za podano ime sem našel sledeče podatke."
	else:
		answer = "Za podano ime nisem našel ustreznih vnosov."	


	json_response['answer'] = answer
	json_response['data'] = json_object
	json_response['url'] = "/"
	json_response['speech'] = answer

	print("$$$$\n",json_response,"\n$$$$")

	return json_response

def getAllowedEhrids(answer_json):
	#print("Getting allowedEhrids")
	session = answer_json["session"] + "/contexts/"
	fullAccess = answer_json["fullAccess"]
	context = [context for context in answer_json["queryResult"]["outputContexts"] if context["name"] == session + "user_data"][0]

	if fullAccess == False:
		allowed_ehrids = [context["parameters"]["user_ehrid"]]
	elif context["parameters"]["user_isDoctor"] == "true":
		name = context["parameters"]["user_patientName"]
		surname = context["parameters"]["user_patientSurname"]
		doctor = Doctor.objects.get(name=name,surname=surname)
		allowed_ehrids = doctor.patient_set.all()
		allowed_ehrids = [i.ehrid for i in allowed_ehrids]

	#print("\nALLOWED EHRIDS: \n",allowed_ehrids)
	return allowed_ehrids

def getPatientEHRID(answer_json,json_response):
	searchData = []
	answ_part = ""
	#Authorisation setup
	baseUrl = 'https://rest.ehrscape.com/rest/v1'
	base = base64.b64encode(credentials)
	authorization = "Basic " + base.decode()

	queryUrl = baseUrl + "/demographics/party/query"
	session = answer_json["session"] + "/contexts/"

	parameter_name = answer_json['queryResult']['outputContexts'][0]['parameters']['given-name']
	parameter_last_name = answer_json['queryResult']['outputContexts'][0]['parameters']['last-name']

	if parameter_name != "":
		searchData.append({"key": "firstNames", "value": parameter_name})
	if parameter_last_name != "":
		searchData.append({"key": "lastNames", "value": parameter_last_name})

	#Use provided ehrid
	parameter_ehrid = answer_json['queryResult']['parameters']['ehrid']
	context = [context_n for context_n in answer_json["queryResult"]["outputContexts"] if context_n["name"] == session + "user_data"][0]

	if parameter_name == "" and parameter_last_name == "" and parameter_ehrid == "" and context["parameters"]["user_isDoctor"] != "true":
		parameter_ehrid = context["parameters"]["user_ehrid"]
		
	if not(parameter_ehrid):
		r = requests.post(queryUrl, data=json.dumps(searchData), headers={"Authorization": authorization, 'content-type': 'application/json'})

		if r.status_code == 200:
			js = json.loads(r.text)
			ehrId = js['parties'][0]['partyAdditionalInfo'][0]['value']
			#print("Found ehrid "+ehrId+" for user "+parameter_name+" "+parameter_last_name)
			answ_part = "Za pacienta "+parameter_name+" "+parameter_last_name

	
	if parameter_ehrid != "":
		ehrId = str(parameter_ehrid)
	else:
		# User entered the wrong name, we try again
		searchData = []

		parameter_name, parameter_last_name = list(closestPatientName(parameter_name + " " + parameter_last_name,database=1)[-1])

		searchData.append({"key": "firstNames", "value": parameter_name})
		searchData.append({"key": "lastNames", "value": parameter_last_name})

		r = requests.post(queryUrl, data=json.dumps(searchData), headers={"Authorization": authorization, 'content-type': 'application/json'})

		if r.status_code == 200:
			js = json.loads(r.text)
			ehrId = js['parties'][0]['partyAdditionalInfo'][0]['value']
			#print("Found ehrid "+ehrId+" for user "+parameter_name+" "+parameter_last_name)

			answ_part = "V bazi nisem našel pacienta s tem imenom. Ste morda mislili " + parameter_name.title() + " " + parameter_last_name.title() + "? "

			json_response['new_name'] = parameter_name
			json_response['new_lastname'] = parameter_last_name


	return ehrId,answer_json,json_response,answ_part


def getLabResultsData(answer_json):
	#print(answer_json)

	allowed_ehrids = getAllowedEhrids(answer_json)

	baseUrl = 'https://rest.ehrscape.com/rest/v1'
	#ehrId = 'd8dcc924-edaf-4df5-8b84-e9e6d0ec590f'
	ehrId = ''
	base = base64.b64encode(credentials)
	authorization = "Basic " + base.decode()

	# Match the action -> provide correct data
	parameter_action = answer_json['queryResult']['action']
	json_response = {"responseType": "list"}
	json_lab_results = []
	json_object = {} 

	ehrId,answer_json,json_response, answ_part = getPatientEHRID(answer_json,json_response)

	if answ_part == "":
		answ_part = "Za pacienta"

	#User wants to see lab results for a specific date or date period.
	if ehrId != '':
		parameter_date_range =answer_json['queryResult']['parameters']['date-period']
		parameter_date =answer_json['queryResult']['parameters']['date']
		queryUrl = baseUrl + "/view/"+ehrId+"/labs"
		r = requests.get(queryUrl, headers={"Authorization": authorization})
		js = json.loads(r.text)

		answer = "Za podan datum ni zabeleženih rezultatov laboratorijskih preiskav."
		if parameter_date_range != "":
			dateFrom  = datetime.strptime(parameter_date_range.split("/")[0], '%Y-%M-%d')
			dateTo  = datetime.strptime(parameter_date_range.split("/")[1], '%Y-%M-%d')

			for lab in js:
				datetime_object = datetime.strptime(lab['time'].split('T')[0], '%Y-%M-%d')
				if dateFrom <= datetime_object <= dateTo:
					#print(lab['name']+" = "+lab['name']+" time: "+str(datetime_object))
					json_object['name'] = lab['name']
					json_object['value'] = str(lab['value'])+" "+lab['unit']
					json_object['date'] = str(datetime_object)
					json_lab_results.append(json_object)
					json_object = {}
			if json_lab_results:	
				answer = answ_part + " in podani casovni okvir sem nasel sledece izvide laboratorijskih preiskav:"
		elif parameter_date != "":
			#print(parameter_date)
			dateFrom  = datetime.strptime(parameter_date, '%Y-%M-%d')
			dateTo  = dateFrom
			for lab in js:
				datetime_object = datetime.strptime(lab['time'].split('T')[0], '%Y-%M-%d')
				if dateFrom <= datetime_object <= dateTo:
					#print(lab['name']+" = "+lab['name']+" time: "+str(datetime_object))
					json_object['name'] = lab['name']
					json_object['value'] = str(lab['value'])+" "+lab['unit']
					json_object['date'] = str(datetime_object)
					json_lab_results.append(json_object)
					json_object = {}
			if json_lab_results:	
				answer = answ_part + " in podan datum "+str(parameter_date)+" sem nasel sledece laboratorijske izvide:"
		else:
			for lab in js:
				datetime_object = datetime.strptime(lab['time'].split('T')[0], '%Y-%M-%d')
				json_object['name'] = lab['name']
				json_object['value'] = str(lab['value'])+" "+lab['unit']
				json_object['date'] = str(datetime_object)
				json_lab_results.append(json_object)
				json_object = {}
				if json_lab_results:	
					answer = answ_part + " sem nasel sledeče laboratorijske izvide:"
	else: 
		answer = "Za podanega pacienta nisem nasel podatkov v sistemu."
	# Generate the JSON response
	json_response['answer'] = answer
	json_response['data'] = json_lab_results
	json_response['url'] = "/"
	json_response['speech'] = answer

	return json_response

def getECGResultsData(answer_json):
	#print(answer_json)

	allowed_ehrids = getAllowedEhrids(answer_json)

	baseUrl = 'https://rest.ehrscape.com/rest/v1'
	ehrId = ''
	base = base64.b64encode(credentials)
	url = "/"
	authorization = "Basic " + base.decode()
	answ_part = "Za pacienta "

	# Match the action -> provide correct data
	parameter_action = answer_json['queryResult']['action']
	json_response = {"responseType": "list"}
	json_lab_results = []
	json_object = {} 

	ehrId, answer_json, json_response, answ_part2 = getPatientEHRID(answer_json,json_response)

	if answ_part2 != "":
		answ_part = answ_part2

	#User wants to see lab results for a specific date or date period.
	if ehrId != '':

		if ehrId not in allowed_ehrids:
			json_response['url'] = "/"
			json_response['answer'] = "Nimate dovoljenja za to poizvedbo."
			json_response['data'] = []
			json_response['speech'] = answer

			return json_response

		parameter_date_range =answer_json['queryResult']['parameters']['date-period']
		parameter_date =answer_json['queryResult']['parameters']['date']

		aql = "/query?aql=select a from EHR e[ehr_id/value='{}'] contains COMPOSITION a".format(ehrId)

		queryUrl = baseUrl + aql

		r = requests.get(queryUrl, headers={"Authorization": authorization,'content-type': 'application/json'})

		js = json.loads(r.text)
		js = js['resultSet']

		answer = "Za podan datum ni zabeleženih rezultatov EKG preiskav."

		if parameter_date_range != "":
			dateFrom  = datetime.strptime(parameter_date_range.split("/")[0], '%Y-%M-%d')
			dateTo  = datetime.strptime(parameter_date_range.split("/")[1], '%Y-%M-%d')

			for item in js:
				if item['#0']['archetype_details']['template_id']['value'] == "Measurement ECG Report":
					datetime_object = datetime.strptime(item['#0']['context']['start_time']['value'].split('T')[0], '%Y-%M-%d')

					if dateFrom <= datetime_object <= dateTo:
						json_object['start_time'] = str(datetime_object)
						json_object['setting'] = item['#0']['context']['setting']['value']
						json_lab_results.append(json_object)
						json_object = {}

			if json_lab_results:	
				answer = answ_part + " in podani casovni okvir sem nasel sledece izvide EKG preiskav:"

		elif parameter_date != "":
			#print(parameter_date)
			dateFrom  = datetime.strptime(parameter_date, '%Y-%M-%d')
			dateTo  = dateFrom

			for item in js:
				if item['#0']['archetype_details']['template_id']['value'] == "Measurement ECG Report":
					datetime_object = datetime.strptime(item['#0']['context']['start_time']['value'].split('T')[0], '%Y-%M-%d')

					if dateFrom <= datetime_object <= dateTo:
						json_object['start_time'] = str(datetime_object)
						json_object['setting'] = item['#0']['context']['setting']['value']
						json_lab_results.append(json_object)
						json_object = {}

			if json_lab_results:	
				answer = answ_part + " in podan datum " + str(parameter_date) + " sem našel sledeče EKG izvide:"
		else:
			for item in js:
				if item['#0']['archetype_details']['template_id']['value'] == "Measurement ECG Report":
					datetime_object = datetime.strptime(item['#0']['context']['start_time']['value'].split('T')[0], '%Y-%M-%d')

					if getECGpdfLink(item):
						#print("URI IN THE FUCKING ITEM!!")
						url = getECGpdfLink(item)
						#print(url)
					#else:
						#print("URI NOT IN THE FUCKING ITEM")

					#json_object['name'] = lab['name']
					json_object['start_time'] = str(datetime_object)
					json_object['setting'] = item['#0']['context']['setting']['value']
					json_lab_results.append(json_object)
					json_object = {}

			if json_lab_results:	
				answer = answ_part + " sem nasel sledece EKG izvide:"
	else:
		answer = "Za podanega pacienta nisem nasel podatkov v sistemu."

	# Generate the JSON response
	json_response['answer'] = answer
	json_response['data'] = json_lab_results
	json_response['url'] = url
	json_response['speech'] = answer

	return json_response

def getAllEntries(answer_json):
	allowed_ehrids = getAllowedEhrids(answer_json)

	baseUrl = 'https://rest.ehrscape.com/rest/v1'
	ehrId = ''
	base = base64.b64encode(credentials)
	authorization = "Basic " + base.decode()
	answer = ""

	# Match the action -> provide correct data
	parameter_action = answer_json['queryResult']['action']
	json_response = {"responseType": "button"}
	json_entries = []
	json_object = {}

	ehrId,answer_json,json_response, answ_part = getPatientEHRID(answer_json,json_response)

	if ehrId != '':

		if ehrId not in allowed_ehrids:
			json_response['url'] = "/"
			json_response['answer'] = "Nimate dovoljenja za to poizvedbo."
			json_response['data'] = []
			json_response['ehrid'] = ehrId
			json_response['speech'] = answer

			return json_response

		json_response['ehrid'] = ehrId

		aql = "/query?aql=select a from EHR e[ehr_id/value='{}'] contains COMPOSITION a".format(ehrId)

		queryUrl = baseUrl + aql

		r = requests.get(queryUrl, headers={"Authorization": authorization,'content-type': 'application/json'})

		js = json.loads(r.text)
		js = js['resultSet']

		if not len(js):
			answer = "Podani pacient nima vpisov v sistemu."
		else:
			parameter_date_range =answer_json['queryResult']['parameters']['date-period']
			parameter_date =answer_json['queryResult']['parameters']['date']

			if parameter_date_range == "" and parameter_date == "":
				answer = answ_part + "Za podanega pacienta sem našel naslednje vpise v sistemu:"
				json_entries = organise_entries(js)
			elif parameter_date_range != "":
				answer = answ_part + "Za podanega pacienta sem našel naslednje vpise v sistemu za časovno obdobje {}:".format(parameter_date_range)
				json_entries = organise_entries(js,date_range=parameter_date_range)
			elif parameter_date != "":
				answer = answ_part + "Za podanega pacienta sem našel naslednje vpise v sistemu za datum {}:".format(parameter_date)
				json_entries = organise_entries(js,date=parameter_date)

		if len(json_entries) == 0:
			print("NO VALUES FOR SPECIFIED DATES OR DATE RANGE")
			answer = "Za podanega pacienta nisem našel podatkov za ta datum oziroma časovno obdobje."

	else: 
		answer = "Za podanega pacienta nisem nasel podatkov v sistemu."
		json_response['ehrid'] = ehrId
	# Generate the JSON response
	json_response['answer'] = answer
	json_response['data'] = json_entries
	json_response['url'] = "/"
	json_response['speech'] = answer

	return json_response

def getEntryData(answer_json):
	allowed_ehrids = getAllowedEhrids(answer_json)

	#print("\n\n ############################################################## \n\n")
	#print(answer_json)
	#print("\n\n ############################################################## \n\n")
	baseUrl = 'https://rest.ehrscape.com/rest/v1'
	ehrId = ''
	base = base64.b64encode(credentials)
	authorization = "Basic " + base.decode()

	# Match the action -> provide correct data
	parameter_action = answer_json['queryResult']['action']
	json_response = {"responseType": "entry"}
	json_entries = []

	response = json_response

	numberList = answer_json['queryResult']['outputContexts'][0]['parameters']['numberList']
	#print(numberList)
	numberList = list(map(int,numberList[0].split(",")))
	ehrId,answer_json,json_response, answ_part = getPatientEHRID(answer_json,json_response)

	if ehrId != '':

		if ehrId not in allowed_ehrids:
			json_response['url'] = "/"
			json_response['answer'] = "Nimate dovoljenja za to poizvedbo."
			json_response['data'] = []
			json_response['speech'] = answer

			return json_response

		aql = "/query?aql=select a from EHR e[ehr_id/value='{}'] contains COMPOSITION a".format(ehrId)

		queryUrl = baseUrl + aql

		r = requests.get(queryUrl, headers={"Authorization": authorization,'content-type': 'application/json'})

		js = json.loads(r.text)
		js = js['resultSet']

		if not len(js):
			answer = "Podani pacient nima vpisov v sistemu."
		elif max(numberList) >= len(js):
			answer = "Izbrani vpis ne obstaja."
		else:
			answer = "Našel sem podatke o vpisu."

			cache.set("dataLength",len(numberList),None)

			json_response['url'] = "/entry_tree"

			for counter,item in enumerate(js):
				if counter in numberList:
					uid = item['#0']['uid']['value']

					queryUrl = baseUrl + "/composition/"

					queryUrl += uid

					r = requests.get(queryUrl, headers={"Authorization": authorization, 'content-type': 'application/json'})

					if r.status_code == 200:
						json_entries = json.loads(r.text)['composition']
						#print("======================== JSON ENTRIES ========================")
						#print(numberList.index(counter))
						#print("===============================================================")
						cache.set("{}".format(numberList.index(counter)),json_entries,None)

					else:
						answer = "Prišlo je do napake. Prosim, poskusite ponovno."
						json_response['url'] = "/"
						break


	else:
		json_response['url'] = "/" 
		answer = "Prišlo je do napake. Prosim, poskusite ponovno."

	# Generate the JSON response
	json_response['answer'] = answer
	json_response['data'] = [{"some":"data"}]
	#json_response['data'] = json_entries
	json_response['speech'] = answer

	return json_response


def searchForEntry(answer_json):
	allowed_ehrids = getAllowedEhrids(answer_json)

	baseUrl = 'https://rest.ehrscape.com/rest/v1'
	ehrId = ''
	base = base64.b64encode(credentials)
	authorization = "Basic " + base.decode()

	# Match the action -> provide correct data
	parameter_action = answer_json['queryResult']['action']
	json_response = {"responseType": "search"}
	json_entries = []
	searchData = []
	data = []
	answer = ""
	session = answer_json["session"] + "/contexts/"

	message = answer_json['queryResult']['parameters']['search-phrase']
	message = " ".join(message)
	#print("The search phrase is: ",message)

	response = json_response
	#json_object = {}

	queryUrl = baseUrl + "/demographics/party/query"

	try:
		parameter_name =answer_json['queryResult']['outputContexts'][0]['parameters']['given-name']
		parameter_last_name =answer_json['queryResult']['outputContexts'][0]['parameters']['last-name']
	except:
		try:
			parameter_name =answer_json['queryResult']['parameters']['given-name']
			parameter_last_name =answer_json['queryResult']['parameters']['last-name']
		except:
			parameter_name,parameter_last_name = "",""

	if parameter_name != "":
		searchData.append({"key": "firstNames", "value": parameter_name})
	if parameter_last_name != "":
		searchData.append({"key": "lastNames", "value": parameter_last_name})

	#Use provided ehrid
	parameter_ehrid = answer_json['queryResult']['parameters']['ehrid']
	context = [context_n for context_n in answer_json["queryResult"]["outputContexts"] if context_n["name"] == session + "user_data"][0]

	if parameter_name == "" and parameter_last_name == "" and parameter_ehrid == "" and context["parameters"]["user_isDoctor"] != "true":
		parameter_ehrid = context["parameters"]["user_ehrid"]

	if not(parameter_ehrid):
		r = requests.post(queryUrl, data=json.dumps(searchData), headers={"Authorization": authorization, 'content-type': 'application/json'})

		if r.status_code == 200:
			js = json.loads(r.text)
			ehrId = js['parties'][0]['partyAdditionalInfo'][0]['value']
			#print("Found ehrid "+ehrId+" for user "+parameter_name+" "+parameter_last_name)

	if parameter_ehrid != "":
		ehrId = str(parameter_ehrid)
	elif ehrId == "":
		# User entered the wrong name, we try again
		searchData = []

		parameter_name, parameter_last_name = list(closestPatientName(parameter_name + " " + parameter_last_name,database=1)[-1])

		searchData.append({"key": "firstNames", "value": parameter_name})
		searchData.append({"key": "lastNames", "value": parameter_last_name})

		r = requests.post(queryUrl, data=json.dumps(searchData), headers={"Authorization": authorization, 'content-type': 'application/json'})

		if r.status_code == 200:
			js = json.loads(r.text)
			ehrId = js['parties'][0]['partyAdditionalInfo'][0]['value']
			#print("Found ehrid "+ehrId+" for user "+parameter_name+" "+parameter_last_name)

			answer = "V bazi nisem našel pacienta s tem imenom. Ste morda mislili " + parameter_name.title() + " " + parameter_last_name.title() + "? "

			json_response['new_name'] = parameter_name
			json_response['new_lastname'] = parameter_last_name

	if ehrId != '':

		if ehrId not in allowed_ehrids:
			json_response['url'] = "/"
			json_response['answer'] = "Nimate dovoljenja za to poizvedbo."
			json_response['data'] = []
			json_response['speech'] = answer

			return json_response

		aql = "/query?aql=select a from EHR e[ehr_id/value='{}'] contains COMPOSITION a".format(ehrId)

		queryUrl = baseUrl + aql

		r = requests.get(queryUrl, headers={"Authorization": authorization,'content-type': 'application/json'})

		js = json.loads(r.text)
		js = js['resultSet']

		if not len(js):
			answer = "Podani pacient nima vpisov v sistemu."
		else:
			#answer = "Našel sem podatke o vpisu."

			json_response['url'] = "/"

			for counter,item in enumerate(js):
				uid = item['#0']['uid']['value']

				queryUrl = baseUrl + "/composition/"

				queryUrl += uid

				r = requests.get(queryUrl, headers={"Authorization": authorization, 'content-type': 'application/json'})

				if r.status_code == 200:
					json_entries = json.loads(r.text)['composition']
					#print("======================== JSON ENTRIES ========================")
					##print(numberList.index(counter))
					##print(json_entries)
					#print("===============================================================")
					data.append(json_entries)

				else:
					answer = "Prišlo je do napake. Prosim, poskusite ponovno."
					#json_response['url'] = "http://www.rtvslo.si/"
					break

			if data:
				bestPerformers,bestPerformersIndices = search_in_data(data,message,hung=1)
				bestPerformersValues = valuesOfBestPerformers(data,bestPerformers,bestPerformersIndices)
				#print("Best performers values:\n",bestPerformersValues)
				#print("\n************************ ANSWER ************************\n")
				#print(answer)
				#print("\n************************ ANSWER ************************\n")
				answer = answer + "Našel sem naslednje podatke, ki se skladajo s poizvedbo: "
				saveBestPerformersDataToCache(data,bestPerformersIndices)

				indicesList = list(set(np.array(bestPerformersIndices)[:,0]))
				#print("\n\ndata length is: ",len(indicesList),"\n\n")

				data = []

				for i in range(len(bestPerformersIndices)):
					data.append({"value" : bestPerformersValues[i], "index" : str(bestPerformersIndices[i][0]), "name" : " ".join(bestPerformers[i]).capitalize()})
				

	else: 
		answer = "Prišlo je do napake. Prosim, poskusite ponovno. Preverite, da ste uporabili pravilno ime osebe. Ste morda mislili: " + " ".join(list(closestPatientName(parameter_name + " " + parameter_last_name,database=1)[-1]))
		data = []
		json_response['url'] = "/"

	# Generate the JSON response
	json_response['answer'] = answer
	json_response['data'] = data
	json_response['speech'] = answer

	return json_response


def getMyPatients(answer_json):
	session = answer_json["session"] + "/contexts/"
	isDoctor = [context for context in answer_json["queryResult"]["outputContexts"] if context["name"] == session + "user_data"][0]["parameters"]["user_isDoctor"]

	json_response = {"responseType": "PatientList"}

	if isDoctor == "true":
		doctor_name = [context for context in answer_json["queryResult"]["outputContexts"] if context["name"] == session + "user_data"][0]["parameters"]["user_patientName"]
		doctor_surname = [context for context in answer_json["queryResult"]["outputContexts"] if context["name"] == session + "user_data"][0]["parameters"]["user_patientSurname"]

		doctor = Doctor.objects.get(name=doctor_name,surname=doctor_surname)
		all_patients = list(doctor.patient_set.all())

		all_patients = [patient.name.title() + " " + patient.surname.title() for patient in all_patients]
		#print("\nPATIENTS:")
		#print(all_patients)

		json_response['url'] = "/"
		json_response['answer'] = "Našel sem vse vaše paciente: "
		json_response['data'] = all_patients
		json_response['speech'] = "Našel sem vse vaše paciente: "
		return json_response

	else:
		json_response['url'] = "/"
		json_response['answer'] = "Ta poizvedba ni veljavna. Ste morda želeli iskati svojega zdravnika?"
		json_response['data'] = ""
		json_response['speech'] = "Ta poizvedba ni veljavna. Ste morda želeli iskati svojega zdravnika?"
		return json_response

def getMyDoctor(answer_json):
	session = answer_json["session"] + "/contexts/"
	json_response = {"responseType": "PatientList"}

	isDoctor = [context for context in answer_json["queryResult"]["outputContexts"] if context["name"] == session + "user_data"][0]["parameters"]["user_isDoctor"]

	if isDoctor == "false":
		name = [context for context in answer_json["queryResult"]["outputContexts"] if context["name"] == session + "user_data"][0]["parameters"]["user_patientName"]
		surname = [context for context in answer_json["queryResult"]["outputContexts"] if context["name"] == session + "user_data"][0]["parameters"]["user_patientSurname"]

		patient = Patient.objects.get(name=name,surname=surname)

		doctor = str(patient.doctor_name.name) + " " + str(patient.doctor_name.surname)

		json_response['url'] = "/"
		json_response['answer'] = "To je seznam vaših zdravnikov: "
		json_response['data'] = [doctor]
		json_response['speech'] = answer
		return json_response
	else:
		json_response['url'] = "/"
		json_response['answer'] = "Ta poizvedba ni veljavna. Ste morda želeli iskati svoje paciente?"
		json_response['data'] = ""
		json_response['speech'] = "Ta poizvedba ni veljavna. Ste morda želeli iskati svoje paciente?"
		return json_response



def getHelp():
	help_list = ['Za prikaz podatkov o pacientu vpišite &quot;Prikaži podatke o pacientu &lt;ime in priimek&gt;&quot;', 
	'Za prikaz vseh vpisov vpišite &quot;Vsi vpisi &lt;ime in priimek&gt;&quot;',
	'Za iskanje po vpisih vpišite &quot;Išči &lt;iskana fraza&gt; pacientu &lt;ime in priimek&gt&quot;',
	'Za prikaz laboratorijskih izvidov vpišite &quot;Prikaži laboratorijske izvide &lt;ime in priimek&gt;&quot;',
	'Za prikaz vaših zdravnikov vpišite &quot;Moj doktor&quot;']

	json_response = {"responseType": "getHelp"}
	json_response['url'] = "/"
	json_response['answer'] = "Za dodatno pomoč kontaktirajte razvijalca."
	json_response['data'] = help_list
	json_response['speech'] = "Za dodatno pomoč kontaktirajte razvijalca."
	return json_response
