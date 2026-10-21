"""Finding caregivers near a place in New York City (story #33)."""

import json
from functools import lru_cache
from pathlib import Path

from django.db.models import Prefetch, Q

from .geocoding import distance_miles
from .models import CaregiverProfile, CaregiverService

NEIGHBORHOODS_FILE = Path(__file__).resolve().parent / "data" / "nyc_neighborhoods.json"

# The largest service radius a caregiver can set (see CaregiverProfile).
MAX_RADIUS_MILES = 25
# Degrees of latitude / longitude that cover MAX_RADIUS_MILES around NYC,
# used to narrow the database query before measuring exact distances.
LAT_DEGREES = MAX_RADIUS_MILES / 69.0
LNG_DEGREES = MAX_RADIUS_MILES / 52.0


@lru_cache(maxsize=1)
def neighborhoods():
    """NYC neighborhoods with a center point, sorted by borough and name."""
    with NEIGHBORHOODS_FILE.open() as f:
        return json.load(f)["neighborhoods"]


def neighborhood(code):
    """The neighborhood with this NTA code (e.g. "MN0202"), or None."""
    return next((n for n in neighborhoods() if n["code"] == code), None)


def searchable_caregivers(viewer):
    """Caregivers an owner can send a request to, with what the cards show."""
    caregivers = (
        CaregiverProfile.objects.filter(user__isnull=False, accepting_new_bookings=True)
        .prefetch_related(
            "supported_pet_types",
            Prefetch(
                "caregiverservice_set",
                queryset=CaregiverService.objects.filter(
                    is_active=True, price__isnull=False
                ).select_related("service_type"),
                to_attr="listed_services",
            ),
        )
        .order_by("name")
    )
    if viewer.is_authenticated:
        caregivers = caregivers.exclude(user=viewer)
    return caregivers


def caregivers_near(caregivers, latitude, longitude):
    """Caregivers whose service radius covers the point, nearest first.

    Each returned caregiver gets a `distance` attribute in miles.
    """
    latitude, longitude = float(latitude), float(longitude)
    nearby = caregivers.filter(
        latitude__range=(latitude - LAT_DEGREES, latitude + LAT_DEGREES),
        longitude__range=(longitude - LNG_DEGREES, longitude + LNG_DEGREES),
    )
    results = []
    for caregiver in nearby:
        caregiver.distance = distance_miles(
            latitude, longitude, caregiver.latitude, caregiver.longitude
        )
        if caregiver.distance <= caregiver.service_radius_miles:
            results.append(caregiver)
    results.sort(key=lambda c: (c.distance, c.name))
    return results


def caregivers_matching_text(caregivers, text):
    """Fallback when the address lookup is down: match the area by name."""
    return list(
        caregivers.filter(Q(neighborhood__icontains=text) | Q(service_area__icontains=text))
    )
