"""PurgoMalum profanity filter client.

Public, unauthenticated, no API key or documented rate limit. Port of the
same logic already verified against the live API in
frontend/api/_lib/purgomalum.ts.
"""
from __future__ import annotations

import requests

BASE_URL = "https://www.purgomalum.com/service/json"
TIMEOUT = 5.0


class ProfanityFilterUnavailable(RuntimeError):
    """Raised on network failure or a non-2xx response from PurgoMalum."""


def filter_text(
    text: str,
    add: str | None = None,
    fill_text: str | None = None,
    fill_char: str | None = None,
) -> str:
    """Filters profanity out of `text`, returning the processed result.

    `add` extends the blocklist for this request only; `fill_text`/
    `fill_char` control what matched words are replaced with.
    """
    params: dict[str, str] = {"text": text}
    if add:
        params["add"] = add
    if fill_text is not None:
        params["fill_text"] = fill_text
    if fill_char is not None:
        params["fill_char"] = fill_char

    try:
        resp = requests.get(BASE_URL, params=params, timeout=TIMEOUT)
    except requests.RequestException as e:
        raise ProfanityFilterUnavailable(str(e)) from e

    if resp.status_code >= 400:
        raise ProfanityFilterUnavailable(f"PurgoMalum returned {resp.status_code}")

    body = resp.json()
    return body.get("result", text)
