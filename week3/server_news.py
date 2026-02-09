"""MCP server for searching news articles (GDELT)."""

import httpx
from mcp.server.fastmcp import FastMCP

import common
import news

mcp = FastMCP("country_research_news")


@mcp.tool()
async def search_news(topic: str, country: str = "", timeline_filter: str = "") -> str:
    """Search news articles about a topic.

    Args:
        topic: The economics topic (e.g. inflation, debt, trade).
        country: Optional. Argentina or Ireland. If empty, searches both.
        timeline_filter: Optional. E.g. last 1 year, last month, in 2024, January 2023.
    """
    countries = common.countries_to_search(country)
    if isinstance(countries, str):
        return countries
    results = await news._search_news_by_countries(topic, countries, timeline_filter)
    return common.format_paper_news_results(results)
