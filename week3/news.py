import httpx

import timeline


def _url_slug_to_title(url: str) -> str:
    """Extract a readable title from URL path slug."""
    path = url.rstrip("/").split("/")[-1] or "News article"
    return path.replace("-", " ").replace("_", " ")[:80]


def _format_gdelt_date(raw: str) -> str:
    """Convert GDELT timestamp (YYYYMMDDHHMMSS) to YYYY-MM-DD."""
    if not raw or len(raw) < 8:
        return ""
    return f"{raw[:4]}-{raw[4:6]}-{raw[6:8]}"


async def _search_news_by_countries(
    topic: str, countries: list[str], timeline_filter: str = ""
) -> list[dict]:
    """Search GDELT for news articles about given countries and topic.

    Args:
        topic: Economics topic to search for (e.g. inflation, debt).
        countries: List of country names (e.g. ["Argentina", "Ireland"]).
        timeline_filter: Optional. E.g. last 1 year, last month. (GDELT supports last X only.)

    Returns:
        List of dicts, each with: title, summary, publication_date, link.
    """
    topic = (topic or "").strip()
    if not topic:
        return []

    maxrows = 10 if len(countries) == 1 else 5
    all_results = []

    for country in countries:
        query = f"{country} {topic}"
        minutes = timeline.timeline_to_minutes(timeline_filter)
        if minutes is not None:
            query = f"{query} lastminutes:{minutes}"
        url    = "https://api.gdeltproject.org/api/v1/search_ftxtsearch/search_ftxtsearch"
        params = {
            "query": query,
            "output": "urllist",
            "maxrows": maxrows,
            "dropdup": "true",
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.get(url, params=params)
                resp.raise_for_status()
                text = resp.text
        except httpx.HTTPError:
            continue

        for line in text.strip().split("\n"):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split(",", 2)
            if len(parts) < 3:
                continue
            date_raw, _lang, link = parts[0], parts[1], parts[2]
            all_results.append({
                "title": _url_slug_to_title(link),
                "summary": "No summary available",
                "publication_date": _format_gdelt_date(date_raw),
                "link": link.strip(),
            })

    return all_results
