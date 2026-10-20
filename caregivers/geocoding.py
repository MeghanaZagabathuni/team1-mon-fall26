"""Turn a New York City street address into map coordinates.

Uses NYC Planning's GeoSearch service (https://geosearch.planninglabs.nyc),
which is free, needs no API key and covers the five boroughs only. Its data
comes from the city's Property Address Directory and is refreshed quarterly.
"""

import json
import math
import re
from dataclasses import dataclass
from decimal import Decimal
from urllib.error import URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

GEOSEARCH_URL = "https://geosearch.planninglabs.nyc/v2/search"
TIMEOUT_SECONDS = 5

# Coordinates are stored rounded to 3 decimal places (about 100 m), so a
# caregiver's exact home is never kept or shown.
COORDINATE_PLACES = Decimal("0.001")

EARTH_RADIUS_MILES = 3958.8


class GeocodingUnavailable(Exception):
    """The GeoSearch service could not be reached or sent a bad response."""


@dataclass(frozen=True)
class Location:
    latitude: Decimal
    longitude: Decimal
    neighborhood: str
    borough: str
    label: str = ""  # the matched address, e.g. "70 WASHINGTON SQUARE SOUTH, New York, NY, USA"


# A leading house number such as "70" or Queens-style "31-00".
HOUSE_NUMBER = re.compile(r"^\s*(\d+(?:-\d+)?)\b")


def _round(value):
    return Decimal(str(value)).quantize(COORDINATE_PLACES)


def geocode(address):
    """Return the Location of an NYC address, or None if it isn't found.

    Raises GeocodingUnavailable if the service can't be reached.
    """
    address = (address or "").strip()
    if not address:
        return None

    url = f"{GEOSEARCH_URL}?{urlencode({'text': address, 'size': 1})}"
    request = Request(url, headers={"User-Agent": "PawPal (NYU course project)"})
    try:
        with urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            data = json.load(response)
    except (URLError, TimeoutError, ValueError) as error:
        raise GeocodingUnavailable(str(error)) from error

    features = data.get("features") or []
    if not features:
        return None

    longitude, latitude = features[0]["geometry"]["coordinates"][:2]
    properties = features[0].get("properties", {})
    label = properties.get("label") or ""

    # GeoSearch always returns its closest guess, even for addresses outside
    # NYC ("1 Hudson Pl, Hoboken" comes back as "45 HUDSON PLACE, Staten
    # Island"). If the caregiver typed a house number, the match must have it.
    typed = HOUSE_NUMBER.match(address)
    matched = HOUSE_NUMBER.match(label)
    if typed and (not matched or typed.group(1) != matched.group(1)):
        return None

    return Location(
        latitude=_round(latitude),
        longitude=_round(longitude),
        neighborhood=properties.get("neighbourhood") or "",
        borough=properties.get("borough") or "",
        label=label,
    )


def distance_miles(lat1, lng1, lat2, lng2):
    """Straight-line distance between two points on Earth, in miles."""
    lat1, lng1, lat2, lng2 = (math.radians(float(v)) for v in (lat1, lng1, lat2, lng2))
    a = (
        math.sin((lat2 - lat1) / 2) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin((lng2 - lng1) / 2) ** 2
    )
    return 2 * EARTH_RADIUS_MILES * math.asin(math.sqrt(a))
