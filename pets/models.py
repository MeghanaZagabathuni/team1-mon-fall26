from django.db import models

class PetType(models.Model):
    name = models.CharField(max_length=100, unique=True)