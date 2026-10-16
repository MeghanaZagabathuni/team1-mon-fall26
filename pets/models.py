from django.db import models

#using this to store unique types of pets, i use it in caregiver/models.py but figure you would also
#find this useful so i put it here!
class PetType(models.Model):
    name = models.CharField(max_length=100, unique=True)