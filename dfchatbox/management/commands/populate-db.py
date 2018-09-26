from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from dfchatbox.models import Patient,Doctor

import json
import base64
import requests
import numpy as np
from dfchatbox._auth import credentials

def allPatients():
    baseUrl = 'https://rest.ehrscape.com/rest/v1'
    ehrId = ''
    base = base64.b64encode(credentials)
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
    base = base64.b64encode(credentials)
    authorization = "Basic " + base.decode()
    r = requests.get("https://rest.ehrscape.com/rest/v1/demographics/party/query/?ehrId={}".format(ehrId),headers={"Authorization": authorization, 'content-type': 'application/json'})
    if r.status_code != 200:
        return
    js = json.loads(r.text)
    return js["parties"][0]["firstNames"].lower(),js["parties"][0]["lastNames"].lower()
    

def createDoctor(self,username,password,name,surname):
    user = User.objects.create_user(username=username,password="abc123")
    user.save()

    new_doctor = Doctor.objects.create(user=user,name=name,surname=surname)
    new_doctor.save()

class Command(BaseCommand):
    def handle(self, *args, **options):
        js = allPatients()

        res = []

        for result in js['resultSet']:
          res.append(result["#0"]["value"])

        names = []
        print("    Fetching data ....")
        for ehrid in set(res):
            name = patientName(ehrid)
            if name:
                names.append(name)
                print(name[0],name[1])

        print("    Fetching data completed!")

        res = list(set(res))

        for i in range(len(res)):
            username = "_".join(names[i])
            print("USERNAME: ",username)
            user = User.objects.create_user(username=username,password='abc123')
            user.save()

            user = User.objects.get(username=username)

            name = names[i][0]
            surname = names[i][1]
            ehrid = res[i]
            doctor_name = Doctor.objects.get(surname="Jezeršek")

            new_patient = Patient.objects.create(user=user,name=name,surname=surname,ehrid=ehrid,doctor_name=doctor_name)
            new_patient.save()
