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
        }

    def edit_caregiver_profile(request, pk):
        caregiver = get_object_or_404(CaregiverProfile, pk=pk)

        if request.method == "POST":
            form = CaregiverProfileForm(
                request.POST,
                request.FILES,
                instance=caregiver
            )

            if form.is_valid():
                form.save()
                return redirect("caregiver_profile_detail", pk=caregiver.pk)

        else:
            form = CaregiverProfileForm(instance=caregiver)

        return render(
            request,
            "caregivers/edit_profile.html",
            {
                "form": form,
                "caregiver": caregiver,
            }
        )

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
        widgets = {
            "description": forms.Textarea(attrs={
                "rows": 3,
                "placeholder": "Tell pet owners what's included in this service..."
            }),
            "price": forms.NumberInput(attrs={
                "step": "0.01",
                "placeholder": "e.g. 25.00"
            }),
        }

def clean(self):
    cleaned_data = super().clean()

    is_active = cleaned_data.get("is_active")
    price = cleaned_data.get("price")

    if is_active and price is None:
        self.add_error(
            "price",
            "Please set a price before activating this service."
        )

    return cleaned_data


