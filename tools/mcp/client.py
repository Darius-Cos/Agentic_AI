"""Real MCP client for the Anthropic fetch server using mcp.ClientSession over SSE."""

from __future__ import annotations

from mcp import ClientSession
from mcp.client.sse import sse_client

from utils.config import MCP_FETCH_URL

YAHOO_FINANCE_URLS = {
    "stocks": "https://finance.yahoo.com/markets/stocks/most-active/",
    "crypto": "https://finance.yahoo.com/markets/crypto/all/",
    "currencies": "https://finance.yahoo.com/markets/currencies/",
}


async def fetch_via_mcp(url: str, max_length: int = 5000) -> str:
    """Fetch a URL via the MCP fetch server using a real MCP ClientSession over SSE."""
    sse_url = f"{MCP_FETCH_URL}/sse"
    async with sse_client(url=sse_url) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool(
                "fetch",
                arguments={"url": url, "max_length": max_length},
            )
            text_parts = [c.text for c in result.content if hasattr(c, "text")]
            return "\n".join(text_parts)


def fetch_url_sync(url: str, max_length: int = 5000) -> str:
    """Synchronous wrapper around fetch_via_mcp."""
    import asyncio
    import concurrent.futures

    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(fetch_via_mcp(url, max_length))

    # Already inside a running loop (e.g. Streamlit / ADK async context):
    # run in a separate thread to avoid event-loop conflicts.
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
        future = pool.submit(asyncio.run, fetch_via_mcp(url, max_length))
        return future.result()


def get_yahoo_finance_url(category: str) -> str | None:
    return YAHOO_FINANCE_URLS.get(category.lower())
