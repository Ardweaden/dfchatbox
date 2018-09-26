from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from dfchatbox.models import Patient,Doctor


class Command(BaseCommand):
    def add_arguments(self,parser):
        parser.add_argument("username")
        parser.add_argument("password")
        parser.add_argument("name")
        parser.add_argument("surname")
        parser.add_argument("ehrid")
        parser.add_argument("doctor_name",nargs='+')

    def handle(self, *args, **options):
        username = options['username']
        password = options['password']
        name = options['name']
        surname = options['surname']
        ehrid = options['ehrid']
        doctor_name = options['doctor_name']

        print(username,password,name,surname,ehrid,doctor_name)
        user = User.objects.create_user(username=username,password=password)
        user.save()

        user = User.objects.get(username=username)

        doctor_name = Doctor.objects.get(name=doctor_name[0], surname=doctor_name[1])

        new_patient = Patient.objects.create(user=user,name=name,surname=surname,ehrid=ehrid,doctor_name=doctor_name)
        new_patient.save()
