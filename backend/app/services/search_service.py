from duckduckgo_search import DDGS
import logging

logger = logging.getLogger(__name__)

class SearchService:
    def search(self, query: str, max_results: int = 5) -> list[dict]:
        """Searches DuckDuckGo and returns list of results with title, link, and snippet."""
        try:
            # Localized search augmentation for Indian queries
            query_lower = query.lower()
            augmented_query = query
            if "college" in query_lower or "admission" in query_lower or "fees" in query_lower:
                if "punjab" not in query_lower and "india" not in query_lower:
                    augmented_query = f"{query} Punjab India"
            elif "scheme" in query_lower or "government" in query_lower:
                if "india" not in query_lower:
                    augmented_query = f"{query} India"
                    
            with DDGS() as ddgs:
                ddgs_generator = ddgs.text(augmented_query, max_results=max_results)
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
            raise Exception("Live search is temporarily unavailable.")

    def format_search_results(self, results: list[dict]) -> str:
        """Formats search results as a text context block for LLM prompt."""
        if not results:
            return "No web search results found."
            
        formatted = "Web Search Results:\n"
        for i, r in enumerate(results, 1):
            formatted += f"[{i}] Title: {r['title']}\n    Link: {r['link']}\n    Snippet: {r['snippet']}\n\n"
        return formatted

search_service = SearchService()
