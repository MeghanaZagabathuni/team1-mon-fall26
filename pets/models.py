from django.db import models

class Pet(models.Model):
    name = models.CharField(max_length=100)
    pet_type = models.ForeignKey(
        "PetType",
        on_delete=models.CASCADE
    )
    breed = models.CharField(max_length=100)
    date_of_birth = models.DateField(blank=True,null=True)
    photo = models.ImageField(upload_to="caregiver/photos",blank=True,null=True)
    description = models.TextField(blank=True)
    special_care_instructions = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class PetType(models.Model):
    name = models.CharField(max_length=100, unique=True)