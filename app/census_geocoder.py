"""US Census Bureau Geocoder client.

Public, unauthenticated, no API key or documented rate limit. Does not
support CORS, so it's only ever called server-side (which is all we do
here anyway). Port of the same logic already verified against the live
API in frontend/api/_lib/censusGeocoder.ts.
"""
from __future__ import annotations

from typing import Any

import requests

BASE_URL = "https://geocoding.geo.census.gov/geocoder"
BENCHMARK = "4"  # Public_AR_Current — current public address ranges
TIMEOUT = 5.0


class GeocoderUnavailable(RuntimeError):
    """Raised on network failure or a non-200/400 response from Census."""


def _one_line(address: str, city: str | None, state: str | None, zip_code: str | None) -> str:
    tail = " ".join(p for p in (city, state, zip_code) if p)
    return f"{address}, {tail}" if tail else address


def geocode_address(
    address: str,
    city: str | None = None,
    state: str | None = None,
    zip_code: str | None = None,
) -> list[dict[str, Any]]:
    """Validates and geocodes a US address.

    Returns [] on no match — Census models "no match" as a 200 with an
    empty `addressMatches` list, not an error — so an empty result here
    means "checked, didn't resolve," not "failed to check."
    """
    one_line = _one_line(address, city, state, zip_code)
    try:
        resp = requests.get(
            f"{BASE_URL}/locations/onelineaddress",
            params={"address": one_line, "benchmark": BENCHMARK, "format": "json"},
            timeout=TIMEOUT,
        )
    except requests.RequestException as e:
        raise GeocoderUnavailable(str(e)) from e

    if resp.status_code == 400:
        raise GeocoderUnavailable(f"Census geocoder rejected the request: {resp.text[:200]}")
    if resp.status_code >= 400:
        raise GeocoderUnavailable(f"Census geocoder returned {resp.status_code}")

    body = resp.json()
    matches = (body.get("result") or {}).get("addressMatches") or []
    return [
        {
            "matched_address": m.get("matchedAddress"),
            "latitude": (m.get("coordinates") or {}).get("y"),
            "longitude": (m.get("coordinates") or {}).get("x"),
            "city": (m.get("addressComponents") or {}).get("city"),
            "state": (m.get("addressComponents") or {}).get("state"),
            "zip": (m.get("addressComponents") or {}).get("zip"),
        }
        for m in matches
    ]
