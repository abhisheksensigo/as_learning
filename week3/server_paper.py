"""MCP server for searching research papers (OpenAlex)."""

import httpx
from mcp.server.fastmcp import FastMCP

import common
import timeline

mcp = FastMCP("country_research_paper")


def _uninvert_abstract(idx: dict) -> str:
    """Convert OpenAlex abstract_inverted_index to plain text."""
    if not idx or not isinstance(idx, dict):
        return ""
    pairs = [(pos, word) for word, positions in idx.items() for pos in positions]
    pairs.sort(key=lambda x: x[0])
    return " ".join(p[1] for p in pairs)


async def _search_research_by_countries(
    topic: str, countries: list[str], timeline_filter: str = ""
) -> list[dict]:
    """Search OpenAlex for research about given countries and topic."""
    topic = (topic or "").strip()
    if not topic:
        return []

    per_page = 10 if len(countries) == 1 else 5
    all_results = []

    for country in countries:
        query = f"{country} {topic}"
        url = "https://api.openalex.org/works"
        params = {"search": query, "per_page": per_page}

        date_range = timeline.parse_timeline(timeline_filter)
        if date_range:
            from_d, to_d = date_range
            params["filter"] = f"from_publication_date:{from_d},to_publication_date:{to_d}"

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.get(url, params=params)
                resp.raise_for_status()
                data = resp.json()
        except httpx.HTTPError:
            continue

        for work in data.get("results") or []:
            title = work.get("display_name") or work.get("title") or "Unknown"
            abstract_idx = work.get("abstract_inverted_index")
            summary = _uninvert_abstract(abstract_idx) if abstract_idx else "No abstract available"
            pub_date = work.get("publication_date") or ""
            doi = work.get("doi") or ""
            link = f"https://doi.org/{doi}" if doi else work.get("id") or ""

            all_results.append({
                "title": title,
                "summary": summary[:500] if summary else "No abstract available",
                "publication_date": pub_date,
                "link": link,
            })

    return all_results


@mcp.tool()
async def search_research(topic: str, country: str = "", timeline_filter: str = "") -> str:
    """Search research papers about a topic.

    Args:
        topic: The economics topic (e.g. inflation, debt, trade).
        country: Optional. Argentina or Ireland. If empty, searches both.
        timeline_filter: Optional. E.g. last 1 year, last month, in 2024, January 2023.
    """
    countries = common.countries_to_search(country)
    if isinstance(countries, str):
        return countries
    results = await _search_research_by_countries(topic, countries, timeline_filter)
    return common.format_paper_news_results(results)
