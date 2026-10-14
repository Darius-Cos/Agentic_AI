"""ADK tool: web search via Tavily API."""

from tavily import TavilyClient

from utils.config import TAVILY_API_KEY

_client: TavilyClient | None = None


def _get_client() -> TavilyClient:
    global _client
    if _client is None:
        if not TAVILY_API_KEY:
            raise EnvironmentError(
                "TAVILY_API_KEY is not set. Get a free key at https://tavily.com"
            )
        _client = TavilyClient(api_key=TAVILY_API_KEY)
    return _client


def web_search_tool(query: str, max_results: int = 5) -> str:
    """Search the public web for current information on a topic.

    Use this tool for recent events, news, or information not covered by the
    internal knowledge base. Do NOT use for financial market data (use
    financial_data_tool instead).

    Args:
        query: The search query.
        max_results: Maximum number of results to return (default 5).

    Returns:
        Formatted string with web search results including titles, URLs, and snippets.
    """
    client = _get_client()
    response = client.search(
        query=query,
        search_depth="advanced",
        max_results=max_results,
        include_answer=True,
    )

    parts = []
    if response.get("answer"):
        parts.append(f"Summary: {response['answer']}\n")

    for i, result in enumerate(response.get("results", []), 1):
        title = result.get("title", "No title")
        url = result.get("url", "")
        content = result.get("content", "")
        parts.append(f"[{i}] {title}\nURL: {url}\n{content}")

    return f"Web Search Results for '{query}':\n\n" + "\n\n---\n\n".join(parts)
