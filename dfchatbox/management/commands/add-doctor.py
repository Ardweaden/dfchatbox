from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from dfchatbox.models import Doctor
    

class Command(BaseCommand):
    def add_arguments(self,parser):
        parser.add_argument("username")
        parser.add_argument("password")
        parser.add_argument("name")
        parser.add_argument("surname")

    def handle(self, *args, **options):
        username = options['username']
        password = options['password']
        name = options['name']
        surname = options['surname']

        print(username,password,name,surname)
        user = User.objects.create_user(username=username,password=password)
        user.save()

        user = User.objects.get(username=username)

        new_doctor = Doctor.objects.create(user=user,name=name,surname=surname)
        new_doctor.save()
