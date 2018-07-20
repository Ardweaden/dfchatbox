from django.db import models

# Create your models here.

class PatientNames(models.Model):
    name = models.CharField(max_length=30)
    lastname = models.CharField(max_length=30)

# class UnrestrictedSearch(models.Model):
#     content_type