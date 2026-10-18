from django.shortcuts import render, redirect, get_object_or_404
from .models import CaregiverProfile, CaregiverService
from .forms import CaregiverProfileForm, CaregiverServicesForm


def create_caregiver_profile(request):
    if request.method == "POST":
        form = CaregiverProfileForm(request.POST, request.FILES)

        if form.is_valid():
            caregiver = form.save()

            selected_services = form.cleaned_data["selected_services"]

            for service_type in selected_services:
                CaregiverService.objects.get_or_create(
                    caregiver=caregiver,
                    service_type=service_type,
                    defaults={
                        "price": None,
                        "is_active": False,
                    }
                )

            return redirect("caregiver", pk=caregiver.pk)

    else:
        form = CaregiverProfileForm()

    return render(
        request,
        "caregivers/create_profile.html",
        {"form": form}
    )


def edit_caregiver_profile(request, pk):
    caregiver = get_object_or_404(CaregiverProfile, pk=pk)

    if request.method == "POST":
        form = CaregiverProfileForm(request.POST, request.FILES, instance=caregiver)

        if form.is_valid():
            # Keep your existing service update logic here!
            form.save()

            return redirect("caregiver", pk=caregiver.pk)

    else:
        form = CaregiverProfileForm(
            instance=caregiver,
            initial={
                "selected_services": CaregiverService.objects.filter(
                    caregiver=caregiver
                ).values_list("service_type_id", flat=True)
            }
        )

    return render(
        request,
        "caregivers/create_profile.html",
        {
            "form": form,
            "caregiver": caregiver,
        }
    )


    
def delete_caregiver_service(request, pk, service_id):
    caregiver = get_object_or_404(CaregiverProfile, pk=pk)

    service = get_object_or_404(
        CaregiverService,
        pk=service_id,
        caregiver=caregiver
    )

    if request.method == "POST":
        service.delete()
        return redirect("services", pk=caregiver.pk)

    return render(
        request,
        "caregivers/delete_service.html",
        {
            "caregiver": caregiver,
            "service": service,
        }
    )


    return render(
        request,
        "caregivers/edit_profile.html",
        {"form": form, "caregiver": caregiver}
    )


def caregiver_profile_detail(request, pk):
    caregiver = get_object_or_404(CaregiverProfile, pk=pk)

    provided_services = CaregiverService.objects.filter(
        caregiver=caregiver
    ).select_related("service_type")

    service_listings = provided_services.filter(
        is_active=True,
        price__isnull=False
    )

    return render(
        request,
        "caregivers/profile_detail.html",
        {
            "caregiver": caregiver,
            "provided_services": provided_services,
            "service_listings": service_listings,
        }
    )


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

def edit_caregiver_service(request, pk, service_id):
    caregiver = get_object_or_404(CaregiverProfile, pk=pk)

    service = get_object_or_404(
        CaregiverService,
        pk=service_id,
        caregiver=caregiver
    )

    if request.method == "POST":
        form = CaregiverServicesForm(request.POST, instance=service)

        if form.is_valid():
            form.save()
            return redirect("services", pk=caregiver.pk)
    else:
        form = CaregiverServicesForm(instance=service)

    return render(
        request,
        "caregivers/edit_service.html",
        {
            "form": form,
            "caregiver": caregiver,
            "service": service,
        }
    )
