from django.shortcuts import render, redirect
from .forms import CaregiverProfileForm
from django.shortcuts import get_object_or_404
from .models import CaregiverProfile, CaregiverService

def create_caregiver_profile(request):
    if request.method == "POST":
        form = CaregiverProfileForm(request.POST,request.FILES)
        if form.is_valid():
            caregiver = form.save()
            return redirect("caregiver_profile_detail", pk=caregiver.pk)          
    else:
        form = CaregiverProfileForm()
    return render(request,"caregivers/create_profile.html",{"form":form})

def caregiver_profile_detail(request, pk):
    caregiver = get_object_or_404(CaregiverProfile, pk=pk)
    return render(request, "caregivers/profile_detail.html",{"caregiver": caregiver})

def caregiver_list_services(request, pk):
    services = get_object_or_404(CaregiverService, pk=pk)
    return render(request, "caregivers/list_services", {"services": services})
