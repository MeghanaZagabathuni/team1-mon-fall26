from django.db import models


class CaregiverProfile(models.Model):
    name = models.CharField(max_length=100)
    bio = models.TextField(blank=True)
    years_of_experience = models.PositiveIntegerField(default=0)
    service_area = models.CharField(max_length=150)
    profile_photo = models.ImageField(upload_to="caregiver/photos",blank=True,null=True)
    special_skills = models.TextField(blank=True)
    certifications = models.TextField(blank=True)
    accepting_new_bookings = models.BooleanField(default=True)
    profile_creation_date = models.DateTimeField(auto_now_add=True)
    profile_creation_date = models.DateTimeField(auto_now=True)
    supported_pet_types = models.ManyToManyField("pets.PetType", blank=True)

class ServiceType(models.Model):
    name = models.CharField(max_length=100,unique=True)
    description = models.TextField(blank=True)

class CaregiverService(models.Model):
    caregiver = models.ForeignKey("CaregiverProfile",on_delete=models.CASCADE)
    service_type = models.ForeignKey("ServiceType", on_delete=models.CASCADE)
    PRICE_UNITS = [
        ("hour", "Per Hour"),
        ("night", "Per Night"),
        ("visit", "Per Visit / Check-in"),
        ("day", "Per Day"),
        ("walk", "Per Walk"),
    ]

    price_unit = models.CharField(
        max_length=10,
        choices=PRICE_UNITS,
        default="hour"
    )
    price = models.DecimalField(max_digits=8, decimal_places=2)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["caregiver", "service_type"],
                name="unique_caregiver_service"
            )
        ]