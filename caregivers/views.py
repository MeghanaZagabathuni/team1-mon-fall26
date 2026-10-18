from django.shortcuts import render, redirect, get_object_or_404
from .models import CaregiverProfile, CaregiverService
from .forms import CaregiverProfileForm, CaregiverServicesForm


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
    caregiver = get_object_or_404(CaregiverProfile, pk=pk)
    services = CaregiverService.objects.filter(caregiver=caregiver)
    return render(request,"caregivers/list_services.html",{"services": services, "caregiver": caregiver})

def add_caregiver_service(request, pk):
    caregiver = get_object_or_404(CaregiverProfile, pk=pk)

    if request.method == "POST":
        form = CaregiverServicesForm(request.POST)

        if form.is_valid():
            service = form.save(commit=False)
            service.caregiver = caregiver
            service.save()

            return redirect("services", pk=caregiver.pk)

    else:
        form = CaregiverServicesForm()

    return render(
        request,
        "caregivers/add_service.html",
        {"form": form, "caregiver": caregiver}
    )
