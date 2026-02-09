"""MCP server for economic data (FRED, World Bank, IMF)."""

from mcp.server.fastmcp import FastMCP

import common
import fred
import imf
import world_bank

mcp = FastMCP("country_research_data")


def _format_data_table(rows: list[dict], columns: list[str]) -> str:
    """Format data rows as markdown table."""
    if not rows:
        return "No data found."
    header = "| " + " | ".join(columns) + " |"
    sep = "|" + "|".join("---" for _ in columns) + "|"
    lines = [header, sep]
    for r in rows:
        line = "| " + " | ".join(str(r.get(c, "")) for c in columns) + " |"
        lines.append(line)
    return "\n".join(lines)


@mcp.tool()
async def fred_data(
    search_text: str = "",
    series_id: str = "",
    observation_start: str = "",
    observation_end: str = "",
    limit: int = 50,
) -> str:
    """Look up FRED (Federal Reserve Economic Data) series and observations.

    Use search_text to find series by keyword (e.g. GDP, inflation, Ireland).
    Use series_id to fetch data for a known series (e.g. GNPCA, GDPC1).
    Set FRED_API_KEY in the environment. Get a free key at https://fred.stlouisfed.org/docs/api/api_key.html

    Args:
        search_text: Keywords to search for matching series.
        series_id: FRED series ID to fetch observations for.
        observation_start: Start date YYYY-MM-DD (optional).
        observation_end: End date YYYY-MM-DD (optional).
        limit: Max results (default 50).
    """
    if not search_text and not series_id:
        return "Provide either search_text (to find series) or series_id (to get data)."

    if series_id:
        obs = await fred.get_observations(
            series_id, observation_start, observation_end, limit
        )
        if not obs:
            return f"No observations found for series {series_id}. Check the ID or date range."
        return _format_data_table(obs, ["date", "value"])

    series_list = await fred.search_series(search_text, limit)
    if not series_list:
        return f"No FRED series found for '{search_text}'."
    return _format_data_table(
        [
            {
                "id": s.get("id", ""),
                "title": (s.get("title", "") or "")[:60],
                "frequency": s.get("frequency", ""),
                "units": (s.get("units", "") or "")[:15],
                "start": s.get("observation_start", ""),
                "end": s.get("observation_end", ""),
            }
            for s in series_list
        ],
        ["id", "title", "frequency", "units", "start", "end"],
    )


@mcp.tool()
async def world_bank_data(
    country: str,
    indicator_code: str = "",
    search_indicator: str = "",
    date_start: str = "",
    date_end: str = "",
    limit: int = 50,
) -> str:
    """Look up World Bank economic data for a country.

    Use search_indicator to find indicators by keyword (e.g. GDP, inflation, population).
    Use indicator_code to fetch data for a known code (e.g. NY.GDP.MKTP.CD, SP.POP.TOTL).
    Country: Argentina or Ireland.

    Args:
        country: Argentina or Ireland.
        indicator_code: World Bank indicator code (e.g. NY.GDP.MKTP.CD).
        search_indicator: Keywords to search for indicators.
        date_start: Start year (e.g. 2020).
        date_end: End year (e.g. 2023). Use with date_start for range.
        limit: Max results (default 50).
    """
    countries = common.countries_to_search(country)
    if isinstance(countries, str):
        return countries
    country_code = common.COUNTRY_CODES.get(countries[0].lower(), {}).get("world_bank", "")
    if not country_code:
        return common.UNSUPPORTED_MSG

    if not indicator_code and not search_indicator:
        return "Provide either indicator_code or search_indicator."

    if search_indicator and not indicator_code:
        indicators = await world_bank.search_indicators(search_indicator, limit=10)
        if not indicators:
            return f"No World Bank indicators found for '{search_indicator}'."
        return _format_data_table(
            [{"id": i["id"], "name": i["name"]} for i in indicators],
            ["id", "name"],
        ) + "\n\nUse indicator_code with one of the IDs above to fetch data."

    data = await world_bank.get_indicator_data(
        country_code, indicator_code, date_start, date_end, limit
    )
    if not data:
        return f"No data found for {indicator_code} in {country}. Check the indicator code and date range."
    return _format_data_table(data, ["date", "value"])


@mcp.tool()
async def imf_data(
    country: str,
    indicator_id: str = "NGDP_RPCH",
    periods: str = "",
    limit: int = 50,
) -> str:
    """Look up IMF economic data for a country.

    Common indicators: NGDP_RPCH (Real GDP growth), PCPIPCH (Inflation),
    GXWDG_NGDP (Debt), etc. Country: Argentina or Ireland.

    Args:
        country: Argentina or Ireland.
        indicator_id: IMF indicator ID (default NGDP_RPCH = Real GDP growth).
        periods: Comma-separated years (e.g. 2019,2020,2021). Empty = all available.
        limit: Max results (default 50).
    """
    countries = common.countries_to_search(country)
    if isinstance(countries, str):
        return countries
    country_code = common.COUNTRY_CODES.get(countries[0].lower(), {}).get("imf", "")
    if not country_code:
        return common.UNSUPPORTED_MSG

    data = await imf.get_indicator_data(
        indicator_id, [country_code], periods, limit
    )
    if not data:
        return f"No IMF data found for {indicator_id} in {country}. Try a different indicator."
    return _format_data_table(data, ["country", "date", "value"])
