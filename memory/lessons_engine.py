"""
=================================================
BharatAI - Lessons Engine
=================================================
"""

import logging
import threading
from typing import Dict, Any, Optional

logger = logging.getLogger("bharatai.memory.lessons_engine")


class LessonsEngine:
    """
    Manages background storage and retrieval of lessons learned from Company Memory.
    """

    @staticmethod
    def get_recommendations(task_query: str) -> Optional[Dict[str, Any]]:
        """
        Search for similar lessons in memory and build recommendation mapping.
        """
        try:
            from memory.memory_manager import memory_manager
            similar = memory_manager.find_similar_lessons(task_query)
        except Exception as e:
            logger.error(f"Failed to query lessons memory: {e}")
            return None

        if not similar:
            return None

        previous_fix = None
        previous_fix_title = None
        previous_implementation = None
        previous_implementation_title = None
        previous_review = None
        previous_review_title = None

        for lesson in similar:
            category = lesson.get("category", "")
            title = lesson.get("title", "")
            
            # Check debug/reusable fix
            if not previous_fix and category == "debugging":
                previous_fix = lesson.get("reusable_fix") or lesson.get("solution")
                previous_fix_title = title
            
            # Check developer implementation pattern
            if not previous_implementation and category == "developer":
                previous_implementation = lesson.get("implementation_pattern") or lesson.get("solution")
                previous_implementation_title = title
            
            # Check reviewer comments or any other general/unclassified category
            if not previous_review and category not in ("debugging", "developer", "qa", "performance"):
                comments = lesson.get("review_comments")
                if comments:
                    if isinstance(comments, list):
                        previous_review = "; ".join(comments)
                    else:
                        previous_review = str(comments)
                else:
                    previous_review = lesson.get("solution")
                previous_review_title = title

            if previous_fix and previous_implementation and previous_review:
                break

        # Only return recommendations dict if we found at least one recommendation type
        if not (previous_fix or previous_implementation or previous_review):
            return None

        return {
            "previous_fix": previous_fix,
            "previous_fix_title": previous_fix_title,
            "previous_implementation": previous_implementation,
            "previous_implementation_title": previous_implementation_title,
            "previous_review": previous_review,
            "previous_review_title": previous_review_title
        }

    @staticmethod
    def save_lesson_async(lesson: Dict[str, Any]) -> None:
        """
        Asynchronously write a lesson learned to Company Memory.
        """
        def run():
            try:
                from memory.memory_manager import memory_manager
                memory_manager.lessons.add_lesson(lesson)
                logger.info(f"Asynchronously saved lesson of category '{lesson.get('category')}' to memory.")
            except Exception as e:
                logger.error(f"Failed to save lesson asynchronously: {e}")

        # Start a daemon thread to avoid blocking execution
        thread = threading.Thread(target=run, daemon=True)
        thread.start()
