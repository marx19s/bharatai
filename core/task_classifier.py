import logging
from typing import List

from config.settings import SMALL_MODEL, CLASSIFICATION_TIMEOUT
from config.settings import LOG_LEVEL
from core.task_category import TaskCategory
from models.manager import ModelManager, manager

logger = logging.getLogger(__name__)
if not logger.handlers:
    logger.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))


class TaskClassifier:
    """Classify incoming user requests into high‑level task categories.

    Primary implementation uses a lightweight Ollama model via ``ModelManager``.
    Falls back to simple keyword matching on failure.
    """

    def __init__(self, model_manager: ModelManager | None = None):
        self.model_manager = model_manager or manager
        self._cache = {}

    def _prompt(self, request: str) -> str:
        """Prompt for LLM to classify the request; expects only enum value."""
        categories = ", ".join([c.value for c in TaskCategory])
        return (
            f"Classify the following user request into one of these categories: {categories}.\n"
            f"Return only the enum value.\n"
            f"User request: \"{request}\""
        )

    def _llm_classify(self, request: str) -> TaskCategory | None:
        logger.info(f"TaskClassifier: Attempting LLM classification for: '{request[:50]}'")
        try:
            # Route to model manager with timeout of 3 seconds to prevent hangs
            response = self.model_manager.generate(
                prompt=self._prompt(request),
                task="classification",
                provider="ollama",
                model=SMALL_MODEL,
                timeout=CLASSIFICATION_TIMEOUT,
                config={"temperature": 0.0, "max_tokens": 10}
            )
            text = response.content.strip().lower()
            logger.info(f"TaskClassifier: LLM response: '{text}'")
            for cat in TaskCategory:
                if cat.value == text:
                    logger.info(f"TaskClassifier: Successfully classified as '{cat.value}' via LLM")
                    return cat
        except Exception as e:
            logger.error(f"TaskClassifier: LLM classification failed: {e}")
        return None

    def _keyword_classify(self, request: str) -> TaskCategory | None:
        lowered = request.lower().strip()
        
        # 1. Check for GENERAL_CHAT direct matches
        if lowered in ("hello", "hello!", "hi", "hi!", "hey", "hey!", "who are you", "who are you?", "hello!") or any(k in lowered for k in ["greeting", "greet"]):
            return TaskCategory.GENERAL_CHAT
            
        # 2. Check for debugging
        if any(k in lowered for k in ["debug", "traceback", "exception", "infinite loop", "never terminate", "bug"]):
            return TaskCategory.DEBUGGING
            
        # 3. Check for planning
        if any(k in lowered for k in ["plan", "roadmap", "planning", "milestone", "ecommerce", "strategy"]):
            return TaskCategory.PLANNING
            
        # 4. Check for research
        if any(k in lowered for k in ["explain", "research", "search", "lookup"]):
            return TaskCategory.RESEARCH
            
        # 5. Check for coding
        if any(k in lowered for k in ["code", "reverse a linked list", "quicksort", "python", "function", "class", "script"]):
            return TaskCategory.CODING
            
        # 6. Check for document analysis
        if any(k in lowered for k in ["pdf", "document", "summarize", "analysis"]):
            return TaskCategory.DOCUMENT_ANALYSIS
            
        return None  # Represents UNKNOWN, triggers LLM fallback

    def classify(self, request: str) -> TaskCategory:
        if request in self._cache:
            logger.info(f"TaskClassifier: Cache hit for request '{request[:50]}'")
            return self._cache[request]

        # First attempt keyword classification as a prefilter
        cat = self._keyword_classify(request)
        if cat is not None:
            logger.info(f"TaskClassifier: Classified as '{cat.value}' via keywords.")
            self._cache[request] = cat
            return cat
            
        # Second attempt LLM classification if prefilter yields nothing
        cat = self._llm_classify(request)
        if cat is not None:
            self._cache[request] = cat
            return cat
            
        # Final fallback
        logger.info("TaskClassifier: Fallback to GENERAL_CHAT classification.")
        cat = TaskCategory.GENERAL_CHAT
        self._cache[request] = cat
        return cat
