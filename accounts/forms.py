from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import AccountProfile

class SignUpForm(UserCreationForm):
    account_type = forms.ChoiceField(
    choices=AccountProfile.Role.choices,
    widget=forms.RadioSelect,
    required=True,
)

    email = forms.EmailField(required=True)

    first_name = forms.CharField(max_length=150, required=True)
    last_name = forms.CharField(max_length=150, required=True)

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()

        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(
                "This email already has an account. Log in."
            )
        return email
    class Meta():
        model = User
        fields = ["username", "first_name", "last_name", "email"]