from django.db import models
from django.contrib.auth.models import User


# Create your models here.

# class PatientNames(models.Model):
#     name = models.CharField(max_length=30)
#     lastname = models.CharField(max_length=30)

class Patient(models.Model):
    """docstring for Patient"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=30)
    surname = models.CharField(max_length=30)
    ehrid = models.CharField(max_length=30)
    doctor_name = models.ForeignKey("Doctor",on_delete=models.CASCADE)

    fullAccess = False


class Doctor(models.Model):
    """docstring for Doctor"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=30)
    surname = models.CharField(max_length=30)
    patients = models.ManyToManyField(Patient, blank=True)

    fullAccess = True