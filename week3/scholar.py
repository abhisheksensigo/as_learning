import httpx
from mcp.server.fastmcp import FastMCP

import news
import timeline

mcp = FastMCP("argentina-research")

SUPPORTED_COUNTRIES = {"argentina", "ireland"}
UNSUPPORTED_MSG = "I am not trained to handle that country."


def _countries_to_search(country: str) -> list[str] | str:
    """Return list of countries to search, or error message if unsupported."""
    c = (country or "").strip().lower()
    if not c:
        return ["Argentina", "Ireland"]
    if c in SUPPORTED_COUNTRIES:
        return [c.title()]
    return UNSUPPORTED_MSG


@mcp.tool()
def hello() -> str:
    """Say hello. Use this to verify the server is connected."""
    return "Hello from Havier Millei!"


def _format_results(results: list[dict]) -> str:
    """Format search results as a markdown table."""
    if not results:
        return "No results found."

    def cell(s: str, max_len: int = 60) -> str:
        s = (s or "").replace("|", " ").replace("\n", " ").strip()
        return (s[:max_len] + "…") if len(s) > max_len else s

    rows = ["| # | Title | Date | Summary | Link |", "|---|-------|------|---------|------|"]
    for i, r in enumerate(results, 1):
        title   = cell(r.get("title", "Unknown"), 50)
        summary = cell(r.get("summary", "No abstract available"), 80)
        date    = cell(r.get("publication_date", ""), 10)
        link    = cell(r.get("link", ""), 40)
        rows.append(f"| {i} | {title} | {date} | {summary} | {link} |")
    return "\n".join(rows)


@mcp.tool()
async def search_research(topic: str, country: str = "", timeline_filter: str = "") -> str:
    """Search research papers about a topic.

    Args:
        topic: The economics topic (e.g. inflation, debt, trade).
        country: Optional. Argentina or Ireland. If empty, searches both.
        timeline_filter: Optional. E.g. last 1 year, last month, in 2024, January 2023.
    """
    countries = _countries_to_search(country)
    if isinstance(countries, str):
        return countries
    results = await _search_research_by_countries(topic, countries, timeline_filter)
    return _format_results(results)


@mcp.tool()
async def search_news(topic: str, country: str = "", timeline_filter: str = "") -> str:
    """Search news articles about a topic.

    Args:
        topic: The economics topic (e.g. inflation, debt, trade).
        country: Optional. Argentina or Ireland. If empty, searches both.
        timeline_filter: Optional. E.g. last 1 year, last month, in 2024, January 2023.
    """
    countries = _countries_to_search(country)
    if isinstance(countries, str):
        return countries
    results = await news._search_news_by_countries(topic, countries, timeline_filter)
    return _format_results(results)


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
        query  = f"{country} {topic}"
        url    = "https://api.openalex.org/works"
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
            title        = work.get("display_name") or work.get("title") or "Unknown"
            abstract_idx = work.get("abstract_inverted_index")
            summary      = _uninvert_abstract(abstract_idx) if abstract_idx else "No abstract available"
            pub_date     = work.get("publication_date") or ""
            doi          = work.get("doi") or ""
            link         = f"https://doi.org/{doi}" if doi else work.get("id") or ""

            all_results.append({
                "title": title,
                "summary": summary[:500] if summary else "No abstract available",
                "publication_date": pub_date,
                "link": link,
            })

    return all_results
