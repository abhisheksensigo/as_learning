"""World Bank Open Data API integration."""

import httpx

WB_BASE = "https://api.worldbank.org/v2"

# Common indicators for search by keyword
COMMON_INDICATORS = [
    ("NY.GDP.MKTP.CD", "GDP (current US$)"),
    ("NY.GDP.MKTP.KD.ZG", "GDP growth (annual %)"),
    ("SP.POP.TOTL", "Population, total"),
    ("FP.CPI.TOTL.ZG", "Inflation, consumer prices (annual %)"),
    ("GC.DOD.TOTL.GD.ZS", "Central government debt, total (% of GDP)"),
    ("NE.EXP.GNFS.ZS", "Exports of goods and services (% of GDP)"),
    ("NE.IMP.GNFS.ZS", "Imports of goods and services (% of GDP)"),
    ("BN.CAB.XOKA.GD.ZS", "Current account balance (% of GDP)"),
    ("SL.UEM.TOTL.ZS", "Unemployment, total (% of labor force)"),
]


async def search_indicators(search_text: str, limit: int = 20) -> list[dict]:
    """Search World Bank indicators by keyword. Returns list of {id, name}."""
    search_lower = (search_text or "").strip().lower()
    if not search_lower:
        return [{"id": ind_id, "name": name} for ind_id, name in COMMON_INDICATORS[:limit]]

    results = []
    for ind_id, name in COMMON_INDICATORS:
        if search_lower in (ind_id + " " + name).lower():
            results.append({"id": ind_id, "name": name})
            if len(results) >= limit:
                break
    return results


async def get_indicator_data(
    country_code: str,
    indicator_code: str,
    date_start: str = "",
    date_end: str = "",
    limit: int = 50,
) -> list[dict]:
    """Fetch indicator data for a country.

    country_code: 3-letter code (arg, irl).
    indicator_code: e.g. NY.GDP.MKTP.CD (GDP), SP.POP.TOTL (population).
    date_start/date_end: years like 2020 or range 2018:2023.
    """
    url = f"{WB_BASE}/country/{country_code}/indicator/{indicator_code}"
    params = {"format": "json", "per_page": min(max(limit, 1), 1000)}

    if date_start or date_end:
        if date_start and date_end:
            params["date"] = f"{date_start}:{date_end}"
        elif date_start:
            params["date"] = date_start
        else:
            params["date"] = date_end

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()
    except httpx.HTTPError:
        return []

    # Response is [metadata, list_of_data_points]
    records = data[1] if isinstance(data, list) and len(data) > 1 else []
    return [
        {"date": str(r.get("date", "")), "value": str(r.get("value", ""))}
        for r in records
    ]
