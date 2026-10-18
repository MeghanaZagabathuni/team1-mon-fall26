from django import forms
from .models import CaregiverProfile, CaregiverService, ServiceType

class CaregiverProfileForm(forms.ModelForm):
    selected_services = forms.ModelMultipleChoiceField(
        queryset=ServiceType.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )
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
        widgets = {
            "supported_pet_types": forms.CheckboxSelectMultiple(
                attrs={"class": "pet-checkbox"}
            ),
            "bio": forms.Textarea(attrs={"rows": 3}),
            "special_skills": forms.Textarea(attrs={"rows": 3}),
            "certifications": forms.Textarea(attrs={"rows": 3}),
            "supported_pet_types": forms.CheckboxSelectMultiple(),
        }

class CaregiverServicesForm(forms.ModelForm):
    class Meta:
        model = CaregiverService 
        fields = [
            "service_type",
            "price_unit",
            "price",
            "description",
            "is_active"
        ]