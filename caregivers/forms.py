from django import forms

from .geocoding import GeocodingUnavailable, geocode
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
            "address",
            "service_radius_miles",
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
            "address": forms.TextInput(
                attrs={"placeholder": "e.g. 70 Washington Square South"}
            ),
        }
        labels = {
            "address": "Street address",
            "service_radius_miles": "How far you'll travel (miles)",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Required for new entries; the model allows blank so older profiles
        # without an address still load.
        self.fields["address"].required = True
        # Set when the address lookup service is down: the profile still saves,
        # without map coordinates, and the view tells the caregiver.
        self.geocoding_unavailable = False
        self._location = None

    @property
    def matched_location(self):
        """The Location found for a new or changed address, if any."""
        return self._location

    def clean_address(self):
        address = self.cleaned_data["address"].strip()
        instance = self.instance
        unchanged = (
            instance.pk
            and address == instance.address
            and instance.latitude is not None
        )
        if unchanged:
            return address
        try:
            self._location = geocode(address)
        except GeocodingUnavailable:
            self.geocoding_unavailable = True
            return address
        if self._location is None:
            raise forms.ValidationError(
                "We couldn't find this address in New York City. "
                "Check the house number and street name."
            )
        return address

    def save(self, commit=True):
        caregiver = super().save(commit=False)
        if self._location is not None:
            caregiver.latitude = self._location.latitude
            caregiver.longitude = self._location.longitude
            caregiver.neighborhood = self._location.neighborhood
        elif self.geocoding_unavailable:
            # Don't keep coordinates that belong to an old address.
            caregiver.latitude = caregiver.longitude = None
            caregiver.neighborhood = ""
        if commit:
            caregiver.save()
            self.save_m2m()
        return caregiver

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


