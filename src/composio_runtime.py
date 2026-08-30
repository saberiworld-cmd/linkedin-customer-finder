import os
import requests

BASE = "https://backend.composio.dev/api/v3"


def _headers() -> dict[str, str]:
    key = os.getenv("COMPOSIO_API_KEY")
    if not key:
        raise RuntimeError("COMPOSIO_API_KEY is required")
    return {"x-api-key": key, "content-type": "application/json"}


def discover_tools(toolkit: str, query: str) -> list[dict]:
    """Discover currently available tools; do not hard-code stale action slugs."""
    response = requests.get(
        f"{BASE}/tools",
        headers=_headers(),
        params={"toolkit_slug": toolkit, "toolkit_versions": "latest", "limit": 100, "search": query},
        timeout=45,
    )
    response.raise_for_status()
    data = response.json()
    return data.get("items", data.get("data", []))


def require_supported_search(toolkit: str, query: str) -> dict:
    tools = discover_tools(toolkit, query)
    if not tools:
        raise RuntimeError(f"No current Composio search tool found for {toolkit}: {query}")
    return tools[0]
