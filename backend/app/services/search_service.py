from duckduckgo_search import DDGS
import logging

logger = logging.getLogger(__name__)

class SearchService:
    def search(self, query: str, max_results: int = 5) -> list[dict]:
        """Searches DuckDuckGo and returns list of results with title, link, and snippet."""
        try:
            with DDGS() as ddgs:
                ddgs_generator = ddgs.text(query, max_results=max_results)
                results = []
                for r in ddgs_generator:
                    results.append({
                        "title": r.get("title", ""),
                        "link": r.get("href", ""),
                        "snippet": r.get("body", "")
                    })
                return results
        except Exception as e:
            logger.error(f"DuckDuckGo search error for query '{query}': {e}")
            return []

    def format_search_results(self, results: list[dict]) -> str:
        """Formats search results as a text context block for LLM prompt."""
        if not results:
            return "No web search results found."
            
        formatted = "Web Search Results:\n"
        for i, r in enumerate(results, 1):
            formatted += f"[{i}] Title: {r['title']}\n    Link: {r['link']}\n    Snippet: {r['snippet']}\n\n"
        return formatted

search_service = SearchService()
