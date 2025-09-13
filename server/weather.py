from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP


mcp = FastMCP("weather")

NWS_API_BASE = "https://api.weather.gov"
USER_AGENT = "weather-app/1.0"


async def make_nws_request(url: str) -> dict[str, Any] | None:
    """Make a request to NWS API with proper error handling."""
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/geo+json"
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception:
            return None
        
def format_alert(feature: dict) -> str:
    """Format an alert feature into readable string."""
    props = feature["properties"]

    return f"""
            Event: {props.get('event', 'Unknown')}
            Area: {props.get('areaDesc', 'Unknown')}
            Severitr: {props.get('severity', 'Unknown')}
            Description: {props.get('description', 'Unknown')}
            Instructions: {props.get('instructions', 'Unknown')}
            """

@mcp.tool()
async def get_alerts(state: str) -> str:
    """Get weather alerts from a US state.

    Args:
        state: Two-letter US state code (e.g. CA, NY)
    """
    url = f"{NWS_API_BASE}/alerts/active/area/{state}"
    data = await make_nws_request(url)

    if not data or "features" not in data:
        return "unable to fetch alerts"
    
    if not data["features"]:
        return "NO active alerts for this state"
    
    alerts = [format_alert(feature) for feature in data['features']]
    return "\n---\n".join(alerts)