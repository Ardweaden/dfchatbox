from django.db import models

# Create your models here.

class PatientNames(models.Model):
    name = models.CharField(max_length=30)
    lastname = models.CharField(max_length=30)

# class Patient(models.Model):
#     """docstring for Patient"""
#     username = models.CharField(max_length=30)
#     name = models.CharField(max_length=30)
#     surname = models.CharField(max_length=30)
#     ehrid = models.CharField(max_length=30)
#     doctor = models.ForeignKey(Doctor,on_delete=models.CASCADE)

#     fullAccess = False


# class Doctor(models.Model):
#     """docstring for Doctor"""
#     name = models.CharField()
#     surname = models.CharField(max_length=30)
#     patients = models.OneToOneField()

#     fullAccess = True