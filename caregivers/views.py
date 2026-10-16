from django.shortcuts import render

from .forms import CaregiverProfileForm

def create_caregiver_profile(request):
    if request.method == "POST":
        #handle
        print()
    else:
        #display an empty form
        print()