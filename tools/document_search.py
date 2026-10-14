"""ADK tool: search the private document corpus via FAISS."""

from rag.retriever import retrieve, format_context


def document_search_tool(query: str, top_k: int = 5) -> str:
    """Search the private knowledge base for information relevant to the query.

    Use this tool for questions about AI, machine learning, RAG, agentic systems,
    Google Cloud, or any topic likely covered in the internal document corpus.

    Args:
        query: The search query to look up in the knowledge base.
        top_k: Number of document chunks to retrieve (default 5).

    Returns:
        Formatted string with the most relevant document excerpts and their sources.
    """
    results = retrieve(query, top_k=top_k)
    if not results:
        return f"No documents found in the knowledge base for query: '{query}'"
    context = format_context(results)
    return f"Document Search Results for '{query}':\n\n{context}"
