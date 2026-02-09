"""Shared utilities for country research MCP servers."""

SUPPORTED_COUNTRIES = {"argentina", "ireland"}
UNSUPPORTED_MSG     = "I am not trained to handle that country."

# Map country names to API-specific codes
COUNTRY_CODES = {
    "argentina": {"world_bank": "arg", "imf": "ARG"},
    "ireland": {"world_bank": "irl", "imf": "IRL"},
}


def countries_to_search(country: str) -> list[str] | str:
    """Return list of countries to search, or error message if unsupported."""
    c = (country or "").strip().lower()
    if not c:
        return ["Argentina", "Ireland"]
    if c in SUPPORTED_COUNTRIES:
        return [c.title()]
    return UNSUPPORTED_MSG


def _cell(s: str, max_len: int = 60) -> str:
    s = (s or "").replace("|", " ").replace("\n", " ").strip()
    return (s[:max_len] + "…") if len(s) > max_len else s


def format_paper_news_results(results: list[dict]) -> str:
    """Format research/news results as markdown table."""
    if not results:
        return "No results found."
    rows = ["| # | Title | Date | Summary | Link |", "|---|-------|------|---------|------|"]
    for i, r in enumerate(results, 1):
        title = _cell(r.get("title", "Unknown"), 50)
        summary = _cell(r.get("summary", "No abstract available"), 80)
        date = _cell(r.get("publication_date", ""), 10)
        link = _cell(r.get("link", ""), 40)
        rows.append(f"| {i} | {title} | {date} | {summary} | {link} |")
    return "\n".join(rows)
