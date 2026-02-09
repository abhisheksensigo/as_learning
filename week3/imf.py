"""IMF DataMapper API integration."""

import httpx

IMF_BASE = "https://www.imf.org/external/datamapper/api/v1"


async def list_indicators() -> dict[str, str]:
    """List available IMF indicators. Returns {indicator_id: label}."""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(f"{IMF_BASE}/indicators")
            resp.raise_for_status()
            data = resp.json()
    except httpx.HTTPError:
        return {}

    if not isinstance(data, dict):
        return {}
    return {k: (v.get("label", k) if isinstance(v, dict) else str(v)) for k, v in data.items()}


async def get_indicator_data(
    indicator_id: str,
    country_codes: list[str],
    periods: str = "",
    limit: int = 50,
) -> list[dict]:
    """Fetch IMF indicator data for countries.

    indicator_id: e.g. NGDP_RPCH (Real GDP growth), PCPIPCH (Inflation).
    country_codes: 3-letter codes (ARG, IRL, USA).
    periods: comma-separated years e.g. 2019,2020,2021.
    """
    path = "/".join([indicator_id] + country_codes)
    url = f"{IMF_BASE}/{path}"
    params = {}
    if periods:
        params["periods"] = periods

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()
    except httpx.HTTPError:
        return []

    if not isinstance(data, dict):
        return []

    # IMF returns nested structure: {indicator: {country: {year: value}}}
    results = []
    val_block = data.get(indicator_id)
    if not isinstance(val_block, dict):
        return []

    for country_code, years in val_block.items():
        if not isinstance(years, dict):
            continue
        for year, val in years.items():
            results.append({
                "country": country_code,
                "date": str(year),
                "value": str(val) if val is not None else "",
            })
            if len(results) >= limit:
                return results[:limit]

    return results[:limit]
