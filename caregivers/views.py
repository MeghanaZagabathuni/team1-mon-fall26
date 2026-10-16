from django.shortcuts import render, redirect

from .forms import CaregiverProfileForm

def create_caregiver_profile(request):
    if request.method == "POST":
        form = CaregiverProfileForm(request.POST,request.FILES)
        if form.is_valid():
            form.save()
            return redirect("create_caregiver_profile")          
    else:
        form = CaregiverProfileForm()
    return render(request,"caregivers/create_profile.html",{"form":form})