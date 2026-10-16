from django import forms
from .models import CaregiverProfile

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