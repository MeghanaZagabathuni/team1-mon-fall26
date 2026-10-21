from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from .models import CaregiverProfile, CaregiverService
from .forms import CaregiverProfileForm, CaregiverServicesForm
from .geocoding import GeocodingUnavailable, geocode
from .search import (
    caregivers_matching_text,
    caregivers_near,
    neighborhood,
    neighborhoods,
    searchable_caregivers,
)


@login_required
def create_caregiver_profile(request):
    # Each account has at most one caregiver profile.
    existing = getattr(request.user, "caregiver_profile", None)
    if existing:
        return redirect("caregiver", pk=existing.pk)

    if request.method == "POST":
        form = CaregiverProfileForm(request.POST, request.FILES)

        if form.is_valid():
            caregiver = form.save(commit=False)
            caregiver.user = request.user
            caregiver.save()
            form.save_m2m()
            location = form.matched_location
            if location is not None:
                messages.info(
                    request,
                    f"We placed you at {location.label.split(',')[0].title()}"
                    f" ({location.neighborhood}, {location.borough}). "
                    "If that's not right, edit your address.",
                )
            if form.geocoding_unavailable:
                messages.warning(
                    request,
                    "Your profile was saved, but we couldn't look up your address "
                    "right now, so you won't appear in map search yet. "
                    "Please save your profile again later.",
                )

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
        form = CaregiverProfileForm(
            request.POST,
            request.FILES,
            instance=caregiver
        )

        if form.is_valid():
            caregiver = form.save()
            location = form.matched_location
            if location is not None:
                messages.info(
                    request,
                    f"We placed you at {location.label.split(',')[0].title()}"
                    f" ({location.neighborhood}, {location.borough}). "
                    "If that's not right, edit your address.",
                )
            if form.geocoding_unavailable:
                messages.warning(
                    request,
                    "Your profile was saved, but we couldn't look up your address "
                    "right now, so you won't appear in map search yet. "
                    "Please save your profile again later.",
                )

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
        existing_services = CaregiverService.objects.filter(
            caregiver=caregiver
        ).values_list("service_type_id", flat=True)

        form = CaregiverProfileForm(
            instance=caregiver,
            initial={
                "selected_services": existing_services
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
            service_type = form.cleaned_data["service_type"]

            already_exists = CaregiverService.objects.filter(
                caregiver=caregiver,
                service_type=service_type
            ).exists()

            if already_exists:
                form.add_error(
                    "service_type",
                    "You already have this service! Please edit your existing listing instead."
                )
            else:
                service = form.save(commit=False)
                service.caregiver = caregiver
                service.save()

                return redirect("services", pk=caregiver.pk)

    else:
        form = CaregiverServicesForm()

    return render(
        request,
        "caregivers/add_service.html",
        {
            "form": form,
            "caregiver": caregiver,
        }
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


@login_required
def caregiver_list(request):
    """Story #33: owners search caregivers by location and see them on a map."""
    caregivers = searchable_caregivers(request.user)
    area_code = request.GET.get("area", "").strip()
    address = request.GET.get("address", "").strip()
    latitude, longitude = _coordinates(request.GET)

    origin = None  # where the owner is searching from: {"label", "latitude", "longitude"}
    notice = ""
    results = None

    if latitude is not None and address:
        # Picked from the address suggestions in the browser.
        origin = {"label": address, "latitude": latitude, "longitude": longitude}
    elif address:
        try:
            location = geocode(address)
        except GeocodingUnavailable:
            location = None
            results = caregivers_matching_text(caregivers, address)
            notice = (
                "Address search is unavailable right now, so these results "
                "match the neighborhood name instead."
            )
        else:
            if location is None:
                notice = "We couldn't find that address in New York City."
                results = []
            else:
                origin = {
                    "label": address,
                    "latitude": location.latitude,
                    "longitude": location.longitude,
                }
    elif area_code:
        area = neighborhood(area_code)
        if area is None:
            notice = "Choose a neighborhood from the list."
        else:
            origin = {
                "label": f"{area['name']}, {area['borough']}",
                "latitude": area["latitude"],
                "longitude": area["longitude"],
            }

    if origin is not None:
        results = caregivers_near(caregivers, origin["latitude"], origin["longitude"])
    elif results is None:
        results = list(caregivers)

    map_points = [
        {
            "id": c.pk,
            "name": c.name,
            "latitude": float(c.latitude),
            "longitude": float(c.longitude),
            "url": reverse("caregiver", args=[c.pk]),
        }
        for c in results
        if c.latitude is not None and c.longitude is not None
    ]
    return render(
        request,
        "caregivers/caregiver_list.html",
        {
            "caregivers": results,
            "neighborhoods": neighborhoods(),
            "area_code": area_code,
            "address": address,
            "origin": origin,
            "notice": notice,
            "searched": bool(address or area_code),
            "map_data": {
                "points": map_points,
                "origin": (
                    {
                        "latitude": float(origin["latitude"]),
                        "longitude": float(origin["longitude"]),
                    }
                    if origin
                    else None
                ),
            },
        },
    )


def _coordinates(params):
    """Latitude/longitude from the query string, or (None, None) if missing or invalid."""
    try:
        latitude = float(params.get("lat", ""))
        longitude = float(params.get("lng", ""))
    except ValueError:
        return None, None
    # Roughly the five boroughs; anything else came from a tampered URL.
    if not (40.4 <= latitude <= 41.0 and -74.3 <= longitude <= -73.6):
        return None, None
    return latitude, longitude
