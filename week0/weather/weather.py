from __future__ import annotations

from typing import Any

import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("weather")

NWS_API_BASE = "https://api.weather.gov"
USER_AGENT = "week0/weather/1.0"


async def make_nws_request(url: str) -> dict[str, Any] | None:
    """Make a request to the NWS API with basic error handling."""
    headers = {"User-Agent": USER_AGENT, "Accept": "application/geo+json"}

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None


def format_alert(feature: dict[str, Any]) -> str:
    """Format an NWS alert feature into a readable string."""
    props = feature.get("properties", {}) or {}
    return "\n".join(
        [
            f'Event: {props.get("event", "Unknown")}',
            f'Area: {props.get("areaDesc", "Unknown")}',
            f'Severity: {props.get("severity", "Unknown")}',
            f'Description: {props.get("description", "Unknown")}',
            f'Instructions: {props.get("instruction", "Unknown")}',
        ]
    )


@mcp.tool()
async def get_alerts(state: str) -> str:
    """Get weather alerts for a given US state (two-letter code)."""
    state = (state or "").strip().upper()
    if len(state) != 2 or not state.isalpha():
        return "Please provide a two-letter US state code (e.g., 'CA')."

    url = f"{NWS_API_BASE}/alerts/active/area/{state}"
    data = await make_nws_request(url)

    features = (data or {}).get("features") or []
    if not features:
        return "No active alerts for this state (or unable to fetch alerts)."

    alerts = [format_alert(feature) for feature in features]
    return "\n---\n".join(alerts)


@mcp.tool()
async def get_forecast(latitude: float, longitude: float) -> str:
    """Get weather forecast for a given latitude and longitude."""
    points_url = f"{NWS_API_BASE}/points/{latitude},{longitude}"
    points_data = await make_nws_request(points_url)
    if not points_data:
        return "Unable to fetch forecast endpoint for that location."

    forecast_url = ((points_data.get("properties") or {}).get("forecast")) or ""
    if not forecast_url:
        return "Forecast endpoint not found for that location."

    forecast_data = await make_nws_request(forecast_url)
    if not forecast_data:
        return "Unable to fetch forecast."

    periods = ((forecast_data.get("properties") or {}).get("periods")) or []
    if not periods:
        return "No forecast periods returned."

    forecasts: list[str] = []
    for period in periods[:5]:
        forecasts.append(
            "\n".join(
                [
                    f'{period.get("name", "Period")}:',
                    f'Temperature: {period.get("temperature", "Unknown")}°{period.get("temperatureUnit", "")}',
                    f'Wind: {period.get("windSpeed", "Unknown")} {period.get("windDirection", "")}'.strip(),
                    f'Forecast: {period.get("detailedForecast", "Unknown")}',
                ]
            )
        )

    return "\n---\n".join(forecasts)