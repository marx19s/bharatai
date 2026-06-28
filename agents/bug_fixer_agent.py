"""
=================================================
BharatAI - Bug Fixer Specialist (BugFixerAgent)
=================================================
"""

import re
import time
import logging
from typing import Dict, Any, List, Optional

from agents.base_agent import BaseAgent
from memory.memory_manager import memory_manager


class BugFixerAgent(BaseAgent):
    """
    BugFixerAgent is responsible for analyzing error stacktraces,
    searching lessons learned, suggesting fixes, and compiling bug reports.
    """

    def __init__(self):
        super().__init__(
            name="bug_fixer",
            role="Bug Fixer Specialist. Analyzes compile/runtime errors, suggests fixes, and updates Lessons learned."
        )

    def analyze_error(self, error_text: str) -> str:
        """Detect the specific error type from the given error stacktrace."""
        self.logger.info("BugFixerAgent: Analyzing error text...")
        error_types = [
            "ModuleNotFoundError",
            "ImportError",
            "SyntaxError",
            "IndentationError",
            "TimeoutError",
            "AssertionError",
            "RuntimeError"
        ]
        for etype in error_types:
            if etype in error_text:
                self.logger.info(f"BugFixerAgent: Detected error type: {etype}")
                return etype
        
        # Check case-insensitive fallback or regex matching for common class names
        for etype in error_types:
            if re.search(r'\b' + etype + r'\b', error_text, re.IGNORECASE):
                self.logger.info(f"BugFixerAgent: Detected error type (fallback): {etype}")
                return etype

        self.logger.info("BugFixerAgent: Error type undetected, returning UnknownError")
        return "UnknownError"

    def search_lessons(self, error_text: str) -> List[Dict[str, Any]]:
        """Search Lessons Memory for similar fixes."""
        self.logger.info("BugFixerAgent: Searching Lessons memory...")
        return memory_manager.find_similar_lessons(error_text)

    def suggest_fix(self, error_text: str) -> Dict[str, Any]:
        """Ask model to suggest a fix, returning cause, fix, and confidence score."""
        self.logger.info("BugFixerAgent: Requesting model suggestion for fix...")
        
        # Retrieve similar lessons to provide context to the LLM
        from services.engineering_learning import EngineeringLearningService
        recs = EngineeringLearningService.query_lessons(error_text)
        lessons_context = ""
        if recs:
            lessons_context = "\nUse the following relevant lessons learned as reference:\n"
            if recs.get("previous_fix"):
                lessons_context += f"- Previous Fix: {recs['previous_fix']}\n"
            if recs.get("previous_implementation"):
                lessons_context += f"- Previous Implementation: {recs['previous_implementation']}\n"
            if recs.get("previous_review"):
                lessons_context += f"- Previous Review: {recs['previous_review']}\n"

        prompt = f"""You are the BugFixerAgent of BharatAI. Suggest a fix for the following error:
{error_text}
{lessons_context}

Provide your response in this exact format:
PROBABLE_CAUSE: <description of root cause>
RECOMMENDED_FIX: <code change or step to fix>
CONFIDENCE_SCORE: <float value between 0.0 and 1.0>
"""
        response = self._call_model(prompt=prompt, task="debugging")
        content = response.content

        probable_cause = "Unknown cause"
        recommended_fix = "No fix suggested"
        confidence_score = 0.5

        for line in content.splitlines():
            line_stripped = line.strip()
            if line_stripped.startswith("PROBABLE_CAUSE:"):
                probable_cause = line_stripped.replace("PROBABLE_CAUSE:", "").strip()
            elif line_stripped.startswith("RECOMMENDED_FIX:"):
                recommended_fix = line_stripped.replace("RECOMMENDED_FIX:", "").strip()
            elif line_stripped.startswith("CONFIDENCE_SCORE:"):
                try:
                    confidence_score = float(line_stripped.replace("CONFIDENCE_SCORE:", "").strip())
                except ValueError:
                    pass

        return {
            "probable_cause": probable_cause,
            "recommended_fix": recommended_fix,
            "confidence_score": confidence_score
        }

    def create_bug_report(self, error_text: str) -> Dict[str, Any]:
        """Compile a complete bug report, save it to Lessons memory, and return it."""
        self.logger.info("BugFixerAgent: Compiling bug report...")
        
        # 1. Analyze error
        error_type = self.analyze_error(error_text)
        
        # 2. Get suggestion
        suggestion = self.suggest_fix(error_text)
        
        # 3. Create report dictionary
        report = {
            "error": error_type,
            "root_cause": suggestion["probable_cause"],
            "suggested_fix": suggestion["recommended_fix"],
            "confidence": suggestion["confidence_score"]
        }

        # 4. Save report to Lessons Memory
        from services.engineering_learning import EngineeringLearningService
        EngineeringLearningService.capture_bug_fix_result(
            error_type=error_type,
            probable_cause=suggestion["probable_cause"],
            recommended_fix=suggestion["recommended_fix"]
        )

        return report

    def execute(self, task: str, context: Optional[Dict[str, Any]] = None) -> Any:
        """Route BugFixer actions."""
        from services.engineering_learning import EngineeringLearningService
        
        # Lessons Engine hook
        recs = EngineeringLearningService.query_lessons(task)
        if recs:
            if context is None:
                context = {}
            context["lessons_recommendations"] = recs
            self.logger.info(f"BugFixerAgent: Recommended previous lessons: {recs}")

        self._current_context = context
        error_text = task
        if context and "error_text" in context:
            error_text = context["error_text"]

        if context:
            op = context.get("operation")
            if op == "analyze_error":
                return self.analyze_error(error_text)
            elif op == "search_lessons":
                return self.search_lessons(error_text)
            elif op == "suggest_fix":
                return self.suggest_fix(error_text)
            elif op == "create_bug_report":
                return self.create_bug_report(error_text)

        # Default action: create bug report
        return self.create_bug_report(error_text)
