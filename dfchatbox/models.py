from django.db import models

# Create your models here.

class PatientNames(models.Model):
    first_names = models.Charfield()
    last_names = models.Charfield()