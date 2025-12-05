# Web Search Tool
# Agent needs research to fix errors & build unfamiliar tasks

from langchain.tools import tool
from langchain_community.tools.ddg_search import DuckDuckGoSearchResults


@tool
def Web_Search(query: str, max_results: int = 5) -> list:
    """
    Perform a free web search using DuckDuckGo.

    Use this tool when the agent needs to:
    - Research errors
    - Look up documentation
    - Find library usage examples
    - Search for installation instructions
    - Explore unknown frameworks or APIs

    Args:
        query: Search query string.
        max_results: Number of results to return (default: 5)

    Returns:
        A list of search result entries (title, snippet, URL).
    """
    try:
        ddg = DuckDuckGoSearchResults()
        results = ddg.run(query)

        # DuckDuckGo returns a string → convert to list if needed
        if isinstance(results, str):
            return [results]

        return results[:max_results]

    except Exception as e:
        return [f"Error while searching: {e}"]


