from django.db import models


class CaregiverProfile(models.Model):
    name = models.CharField(max_length=100)
    bio = models.TextField(blank=True)
    years_of_experience = models.PositiveIntegerField(default=0)
    service_area = models.CharField(max_length=150)
    profile_photo = models.ImageField(upload_to="caregiver/photos",blank=True,null=True)
    special_skills = models.TextField(blank=True)
    certifications = models.TextField(blank=True)
    accepting_new_bookings = models.BooleanField(default=False)
    profile_creation_date = models.DateTimeField(auto_now_add=True)
    profile_creation_date = models.DateTimeField(auto_now=True)
    supported_pet_types = models.ManyToManyField(
        "pets.PetType",
        blank=True
    )

    
    
