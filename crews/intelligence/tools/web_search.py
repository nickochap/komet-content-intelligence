import os
import requests
from crewai.tools import BaseTool


class WebSearchTool(BaseTool):
    name: str = "Web Search"
    description: str = """
    Search the web using Serper API. Use for competitor research, trend identification,
    and market intelligence. Input: search query string.
    Returns: top search results with titles, snippets, and URLs.
    """

    def _run(self, query: str) -> str:
        api_key = os.getenv("SERPER_API_KEY")

        response = requests.post(
            "https://google.serper.dev/search",
            headers={"X-API-KEY": api_key, "Content-Type": "application/json"},
            json={"q": query, "num": 10}
        )

        if response.status_code != 200:
            return f"Search error {response.status_code}: {response.text[:200]}"

        data = response.json()
        results = []

        for item in data.get("organic", []):
            results.append(
                f"Title: {item.get('title', '')}\n"
                f"URL: {item.get('link', '')}\n"
                f"Snippet: {item.get('snippet', '')}\n"
                "---"
            )

        return "\n".join(results) if results else "No results found."
