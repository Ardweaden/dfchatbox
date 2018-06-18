from django.db import models

# Create your models here.

class PatientNames(models.Model):
    first_names = models.CharField(max_length=30)
    last_names = models.CharField(max_length=30)