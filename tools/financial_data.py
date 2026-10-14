"""ADK tool: financial market data via MCP fetch server + Yahoo Finance."""

from tools.mcp.client import fetch_url_sync, YAHOO_FINANCE_URLS


_CATEGORY_KEYWORDS = {
    "stocks": ["stock", "equity", "share", "nasdaq", "nyse", "s&p", "dow", "most active"],
    "crypto": ["crypto", "bitcoin", "ethereum", "btc", "eth", "blockchain", "coin", "token"],
    "currencies": ["currency", "currencies", "forex", "fx", "exchange rate", "usd", "eur", "gbp"],
}


def _detect_category(query: str) -> str:
    """Detect the financial category from the query text."""
    q = query.lower()
    for category, keywords in _CATEGORY_KEYWORDS.items():
        if any(kw in q for kw in keywords):
            return category
    return "stocks"  # default


def financial_data_tool(query: str, category: str = "auto") -> str:
    """Retrieve live financial market data from Yahoo Finance via the MCP fetch server.

    Use this tool INSTEAD of web_search_tool when the user asks about:
    - Stock market data, most active stocks, equity prices
    - Cryptocurrency prices and rankings
    - Currency exchange rates and forex data

    Args:
        query: The financial data query (e.g., "most active stocks today").
        category: One of 'stocks', 'crypto', 'currencies', or 'auto' to detect automatically.

    Returns:
        Formatted string with the requested financial data.
    """
    if category == "auto":
        category = _detect_category(query)

    if category not in YAHOO_FINANCE_URLS:
        return (
            f"Unknown category '{category}'. "
            f"Valid categories: {', '.join(YAHOO_FINANCE_URLS.keys())}"
        )

    url = YAHOO_FINANCE_URLS[category]
    try:
        content = fetch_url_sync(url)
        return (
            f"Financial Data ({category.upper()}) from Yahoo Finance:\n"
            f"Source: {url}\n\n{content}"
        )
    except Exception as e:
        return (
            f"Could not retrieve financial data for category '{category}'.\n"
            f"Error: {e}\n\n"
            "Make sure the MCP fetch server is running: "
            "docker run -p 8000:8000 mcp/fetch"
        )
