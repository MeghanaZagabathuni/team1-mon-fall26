from django import forms
from .models import CaregiverProfile, CaregiverService

class CaregiverProfileForm(forms.ModelForm):
    class Meta:
        model = CaregiverProfile
        fields = [
            "name", 
            "bio",
            "years_of_experience", 
            "service_area", 
            "profile_photo", 
            "special_skills", 
            "certifications", 
            "supported_pet_types", 
            "accepting_new_bookings",
            ]

class CaregiverServicesForm(forms.ModelForm):
    class Meta:
        model = CaregiverService 
        fields = [
            "caregiver",
            "service_type",
            "price_unit",
            "price",
            "description",
            "is_active"
        ]