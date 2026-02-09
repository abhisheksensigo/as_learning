"""FRED (Federal Reserve Economic Data) API integration."""

import os

import httpx

FRED_BASE = "https://api.stlouisfed.org/fred"


def _get_api_key() -> str | None:
    return os.environ.get("FRED_API_KEY")


async def search_series(search_text: str, limit: int = 10) -> list[dict]:
    """Search FRED for economic data series matching the given text."""
    api_key = _get_api_key()
    if not api_key:
        return []

    url = f"{FRED_BASE}/series/search"
    params = {
        "api_key": api_key,
        "search_text": search_text.strip(),
        "file_type": "json",
        "limit": min(max(limit, 1), 100),
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()
    except httpx.HTTPError:
        return []

    series_list = data.get("seriess") or []
    return [
        {
            "id": s.get("id", ""),
            "title": s.get("title", ""),
            "frequency": s.get("frequency", ""),
            "units": s.get("units", ""),
            "observation_start": s.get("observation_start", ""),
            "observation_end": s.get("observation_end", ""),
        }
        for s in series_list
    ]


async def get_observations(
    series_id: str,
    observation_start: str = "",
    observation_end: str = "",
    limit: int = 100,
) -> list[dict]:
    """Fetch observations (data points) for a FRED series."""
    api_key = _get_api_key()
    if not api_key or not series_id.strip():
        return []

    url = f"{FRED_BASE}/series/observations"
    params = {
        "api_key": api_key,
        "series_id": series_id.strip(),
        "file_type": "json",
        "limit": min(max(limit, 1), 10000),
    }
    if observation_start:
        params["observation_start"] = observation_start
    if observation_end:
        params["observation_end"] = observation_end

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()
    except httpx.HTTPError:
        return []

    obs_list = data.get("observations") or []
    return [{"date": o.get("date", ""), "value": o.get("value", "")} for o in obs_list]
