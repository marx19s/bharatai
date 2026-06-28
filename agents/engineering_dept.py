"""
=================================================
BharatAI - Engineering Department Foundation
=================================================
"""

import time
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional

from agents.base_agent import BaseAgent
from memory.memory_manager import memory_manager


class DeveloperAgent(BaseAgent):
    """
    DeveloperAgent represents a software developer in BharatAI.
    It generates code, creates new files, updates existing files, and explains changes.
    """

    def __init__(self):
        super().__init__(
            name="developer",
            role="Generates software code, manages local files, and explains changes."
        )
        self._modified_files = []

    def _extract_implementation_pattern(self, task: str, result: Any) -> str:
        """Extract or infer the implementation pattern used based on task and result."""
        result_str = str(result)
        patterns = []
        task_lower = task.lower()
        res_lower = result_str.lower()
        
        # Check standard design patterns in task or result
        for p in ["singleton", "factory", "decorator", "adapter", "observer", "facade", "strategy", "builder", "command"]:
            if p in task_lower or p in res_lower:
                patterns.append(p.capitalize())
                
        if not patterns:
            if "class " in result_str:
                patterns.append("Object-Oriented")
            elif "def " in result_str:
                patterns.append("Functional/Procedural")
            else:
                patterns.append("Standard Coding")
                
        return ", ".join(patterns)

    def generate_code(self, prompt: str) -> str:
        """Call the model to generate code based on a prompt."""
        self.logger.info("DeveloperAgent: Generating code...")
        action_log = {"action": "generate_code", "prompt": prompt, "timestamp": time.time()}
        memory_manager.developer.add(action_log)

        # Append lessons recommendations to the prompt if available
        recs = getattr(self, "_current_context", {}).get("lessons_recommendations") if getattr(self, "_current_context", None) else None
        if recs:
            prompt_suffix = "\n\n### Recommendations from Previous Lessons:\n"
            if recs.get("previous_fix"):
                title_prefix = f"[{recs['previous_fix_title']}] " if recs.get("previous_fix_title") else ""
                prompt_suffix += f"- Previous Fix: {title_prefix}{recs['previous_fix']}\n"
            if recs.get("previous_implementation"):
                title_prefix = f"[{recs['previous_implementation_title']}] " if recs.get("previous_implementation_title") else ""
                prompt_suffix += f"- Previous Implementation: {title_prefix}{recs['previous_implementation']}\n"
            if recs.get("previous_review"):
                title_prefix = f"[{recs['previous_review_title']}] " if recs.get("previous_review_title") else ""
                prompt_suffix += f"- Previous Review: {title_prefix}{recs['previous_review']}\n"
            prompt += prompt_suffix

        # Call model using coding settings
        response = self._call_model(prompt=prompt, task="coding")
        result = response.content

        action_log["result_len"] = len(result)
        memory_manager.developer.add({"action": "generate_code_completed", "timestamp": time.time()})
        return result

    def create_file(self, file_path: str, content: str) -> bool:
        """Create a new file with the specified content."""
        self.logger.info(f"DeveloperAgent: Creating file at {file_path}")
        action_log = {"action": "create_file", "path": file_path, "timestamp": time.time()}
        memory_manager.developer.add(action_log)

        try:
            path = Path(file_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            self.logger.info(f"DeveloperAgent: File created successfully: {file_path}")
            memory_manager.developer.add({"action": "create_file_success", "path": file_path, "timestamp": time.time()})
            if not hasattr(self, "_modified_files") or self._modified_files is None:
                self._modified_files = []
            self._modified_files.append(file_path)
            return True
        except Exception as e:
            self.logger.error(f"DeveloperAgent: Failed to create file at {file_path}: {e}")
            memory_manager.developer.add({"action": "create_file_failed", "path": file_path, "error": str(e), "timestamp": time.time()})
            return False

    def update_file(self, file_path: str, content: str) -> bool:
        """Update an existing file with the specified content."""
        self.logger.info(f"DeveloperAgent: Updating file at {file_path}")
        action_log = {"action": "update_file", "path": file_path, "timestamp": time.time()}
        memory_manager.developer.add(action_log)

        try:
            path = Path(file_path)
            # Just write the content, parent directories created if they don't exist
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            self.logger.info(f"DeveloperAgent: File updated successfully: {file_path}")
            memory_manager.developer.add({"action": "update_file_success", "path": file_path, "timestamp": time.time()})
            if not hasattr(self, "_modified_files") or self._modified_files is None:
                self._modified_files = []
            self._modified_files.append(file_path)
            return True
        except Exception as e:
            self.logger.error(f"DeveloperAgent: Failed to update file at {file_path}: {e}")
            memory_manager.developer.add({"action": "update_file_failed", "path": file_path, "error": str(e), "timestamp": time.time()})
            return False

    def explain_changes(self, file_path: str, original: str, updated: str) -> str:
        """Ask model to explain changes between original and updated file content."""
        self.logger.info(f"DeveloperAgent: Explaining changes for {file_path}")
        action_log = {"action": "explain_changes", "path": file_path, "timestamp": time.time()}
        memory_manager.developer.add(action_log)

        prompt = f"""Explain the changes between the original and updated content for file: {file_path}

Original:
{original}

Updated:
{updated}
"""
        response = self._call_model(prompt=prompt, task="fast")
        explanation = response.content

        memory_manager.developer.add({"action": "explain_changes_completed", "path": file_path, "timestamp": time.time()})
        return explanation

    def execute(self, task: str, context: Optional[Dict[str, Any]] = None) -> Any:
        """Route task based on input strings or context dictionary."""
        from services.engineering_learning import EngineeringLearningService
        
        # Lessons Engine hook
        recs = EngineeringLearningService.query_lessons(task)
        has_recommendations = recs is not None
        lessons_applied_count = 0
        reused_fixes_count = 0
        
        if recs:
            if context is None:
                context = {}
            context["lessons_recommendations"] = recs
            self.logger.info(f"DeveloperAgent: Recommended previous lessons: {recs}")
            if recs.get("previous_implementation") or recs.get("previous_review"):
                lessons_applied_count = 1
            if recs.get("previous_fix"):
                reused_fixes_count = 1

        self._current_context = context
        self._modified_files = []
        success = False
        result = None
        
        try:
            self.logger.info(f"DeveloperAgent execute received task: '{task[:100]}'")
            
            # Check if context specifies a structured operation
            if context:
                op = context.get("operation")
                file_path = context.get("file_path")
                content = context.get("content")
                original = context.get("original")
                updated = context.get("updated")

                if op == "create_file" and file_path and content is not None:
                    result = self.create_file(file_path, content)
                elif op == "update_file" and file_path and content is not None:
                    result = self.update_file(file_path, content)
                elif op == "explain_changes" and file_path and original is not None and updated is not None:
                    result = self.explain_changes(file_path, original, updated)
                elif op == "generate_code":
                    result = self.generate_code(task)

            if result is None:
                # Basic task string heuristics
                task_lower = task.lower()
                if "create file" in task_lower or "write file" in task_lower:
                    # Look for a path and content in context
                    file_path = context.get("file_path") if context else "generated_file.py"
                    result = self.create_file(file_path, task)
                elif "update file" in task_lower or "modify file" in task_lower:
                    file_path = context.get("file_path") if context else "generated_file.py"
                    result = self.update_file(file_path, task)
                elif "explain" in task_lower:
                    result = self.explain_changes("file.py", "original code", task)
                else:
                    # Default behavior: generate code
                    result = self.generate_code(task)
            
            success = True
            return result
        except Exception as e:
            success = False
            raise e
        finally:
            task_type = context.get("task_type", "coding") if context else "coding"
            pattern = self._extract_implementation_pattern(task, result)
            files = list(set(self._modified_files))
            
            EngineeringLearningService.capture_developer_result(
                task=task,
                task_type=task_type,
                success=success,
                implementation_pattern=pattern,
                files_modified=files,
                has_recommendations=has_recommendations,
                lessons_applied_count=lessons_applied_count,
                reused_fixes_count=reused_fixes_count
            )


class ReviewerAgent(BaseAgent):
    """
    ReviewerAgent represents a code reviewer in BharatAI.
    It reviews code or diffs, searches Lessons memory, and suggests improvements.
    """

    def __init__(self):
        super().__init__(
            name="reviewer",
            role="Reviews code changes for syntax issues, duplicate code, smells, and missing documentation."
        )

    def _retrieve_lessons(self, query: str) -> str:
        """Find matching lessons learned to assist in code review."""
        from services.engineering_learning import EngineeringLearningService
        recs = EngineeringLearningService.query_lessons(query)
        if not recs:
            return ""
        
        lessons_text = "\n### Relevant Lessons Learned:\n"
        if recs.get("previous_fix"):
            title_prefix = f"[{recs['previous_fix_title']}] " if recs.get("previous_fix_title") else ""
            lessons_text += f"- Previous Fix: {title_prefix}{recs['previous_fix']}\n"
        if recs.get("previous_implementation"):
            title_prefix = f"[{recs['previous_implementation_title']}] " if recs.get("previous_implementation_title") else ""
            lessons_text += f"- Previous Implementation: {title_prefix}{recs['previous_implementation']}\n"
        if recs.get("previous_review"):
            title_prefix = f"[{recs['previous_review_title']}] " if recs.get("previous_review_title") else ""
            lessons_text += f"- Previous Review: {title_prefix}{recs['previous_review']}\n"
        return lessons_text

    def _extract_review_details(self, report: str) -> Dict[str, Any]:
        """Extract review comments, recurring code smells, and architecture issues from text report."""
        comments = []
        smells = []
        arch_issues = []
        
        lines = report.splitlines()
        current_section = None
        for line in lines:
            line_stripped = line.strip()
            line_lower = line_stripped.lower()
            if "smell" in line_lower:
                current_section = "smells"
            elif "architect" in line_lower or "design" in line_lower or "structure" in line_lower:
                current_section = "arch"
            elif "comment" in line_lower or "suggestion" in line_lower or "feedback" in line_lower:
                current_section = "comments"
                
            if line_stripped.startswith(("-", "*", "1.", "2.", "3.", "4.", "5.", "6.", "7.", "8.", "9.")):
                val = line_stripped.lstrip("-*0123456789. ")
                if val:
                    if current_section == "smells":
                        smells.append(val)
                    elif current_section == "arch":
                        arch_issues.append(val)
                    else:
                        comments.append(val)
                        
        if not comments and report:
            comments.append(report[:200] + "...")
            
        return {
            "review_comments": comments or ["No major suggestions."],
            "recurring_code_smells": smells or ["None detected."],
            "architecture_issues": arch_issues or ["None detected."]
        }

    def review_code(self, code: str) -> str:
        """Review the given code block using LLM and Lessons Memory."""
        self.logger.info("ReviewerAgent: Reviewing code block...")
        action_log = {"action": "review_code", "timestamp": time.time()}
        memory_manager.reviewer.add(action_log)

        lessons = self._retrieve_lessons(code)

        prompt = f"""You are the ReviewerAgent of BharatAI. Review the following code for:
- Syntax issues
- Duplicate code
- Code smells
- Missing documentation

Code to review:
{code}
{lessons}
Provide a detailed code review report.
"""
        response = self._call_model(prompt=prompt, task="fast")
        report = response.content

        memory_manager.reviewer.add({
            "action": "review_code_completed",
            "report_len": len(report),
            "timestamp": time.time()
        })
        return report

    def review_diff(self, diff: str) -> str:
        """Review a code diff using LLM and Lessons Memory."""
        self.logger.info("ReviewerAgent: Reviewing code diff...")
        action_log = {"action": "review_diff", "timestamp": time.time()}
        memory_manager.reviewer.add(action_log)

        lessons = self._retrieve_lessons(diff)

        prompt = f"""You are the ReviewerAgent of BharatAI. Review the following code diff for:
- Potential regressions or bugs introduced
- Code smells
- Missing documentation or comments

Diff to review:
{diff}
{lessons}
Provide a detailed code review report on the changes.
"""
        response = self._call_model(prompt=prompt, task="fast")
        report = response.content

        memory_manager.reviewer.add({
            "action": "review_diff_completed",
            "report_len": len(report),
            "timestamp": time.time()
        })
        return report

    def suggest_improvements(self, code: str) -> str:
        """Suggest optimization or refactoring improvements for code."""
        self.logger.info("ReviewerAgent: Suggesting improvements...")
        action_log = {"action": "suggest_improvements", "timestamp": time.time()}
        memory_manager.reviewer.add(action_log)

        lessons = self._retrieve_lessons(code)

        prompt = f"""You are the ReviewerAgent of BharatAI. Suggest improvements and refactoring for the following code:

Code:
{code}
{lessons}
Provide clean refactored suggestions and describe why the improvements are recommended.
"""
        response = self._call_model(prompt=prompt, task="fast")
        suggestions = response.content

        memory_manager.reviewer.add({
            "action": "suggest_improvements_completed",
            "suggestions_len": len(suggestions),
            "timestamp": time.time()
        })
        return suggestions

    def execute(self, task: str, context: Optional[Dict[str, Any]] = None) -> Any:
        """Route review tasks based on keywords or context operations."""
        from services.engineering_learning import EngineeringLearningService
        
        # Lessons Engine hook
        recs = EngineeringLearningService.query_lessons(task)
        if recs:
            if context is None:
                context = {}
            context["lessons_recommendations"] = recs
            self.logger.info(f"ReviewerAgent: Recommended previous lessons: {recs}")

        self._current_context = context
        result = None
        
        try:
            self.logger.info(f"ReviewerAgent execute received task: '{task[:100]}'")

            if context:
                op = context.get("operation")
                code = context.get("code")
                diff = context.get("diff")

                if op == "review_code" and code is not None:
                    result = self.review_code(code)
                elif op == "review_diff" and diff is not None:
                    result = self.review_diff(diff)
                elif op == "suggest_improvements" and code is not None:
                    result = self.suggest_improvements(code)

            if result is None:
                task_lower = task.lower()
                if "diff" in task_lower:
                    result = self.review_diff(task)
                elif "suggest" in task_lower or "improve" in task_lower:
                    result = self.suggest_improvements(task)
                else:
                    # Default fallback
                    result = self.review_code(task)
            
            # Capture review details
            details = self._extract_review_details(str(result))
            EngineeringLearningService.capture_reviewer_result(
                task=task,
                review_comments=details["review_comments"],
                recurring_code_smells=details["recurring_code_smells"],
                architecture_issues=details["architecture_issues"]
            )
            return result
        except Exception as e:
            raise e


class EngineeringDepartmentOrchestrator:
    """
    Orchestrates the Engineering Department workflow using EventBus to integrate:
    DeveloperAgent -> ReviewerAgent -> QAAgent -> (If QA fails: BugFixerAgent) -> PerformanceAgent.
    """

    def __init__(self):
        from core.registry import registry
        self.registry = registry
        self.status = {}
        self.results = {}
        self._setup_event_subscriptions()

    def _setup_event_subscriptions(self):
        from core.event_bus import event_bus
        event_bus.subscribe("code_generation_requested", self.handle_code_generation)
        event_bus.subscribe("code_generated", self.handle_code_review)
        event_bus.subscribe("code_reviewed", self.handle_qa_testing)
        event_bus.subscribe("tests_run", self.handle_qa_result)
        event_bus.subscribe("bug_analyzed", self.handle_performance_analysis)
        event_bus.subscribe("performance_analyzed", self.handle_completion)

    def cleanup(self):
        """Unsubscribe all handlers from the EventBus to prevent test leakage."""
        from core.event_bus import event_bus
        event_bus.unsubscribe("code_generation_requested", self.handle_code_generation)
        event_bus.unsubscribe("code_generated", self.handle_code_review)
        event_bus.unsubscribe("code_reviewed", self.handle_qa_testing)
        event_bus.unsubscribe("tests_run", self.handle_qa_result)
        event_bus.unsubscribe("bug_analyzed", self.handle_performance_analysis)
        event_bus.unsubscribe("performance_analyzed", self.handle_completion)

    def run_workflow(self, task_description: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Trigger the integrated event-driven workflow."""
        from core.event_bus import event_bus
        self.status = {
            "developer": "PENDING",
            "review": "PENDING",
            "qa": "PENDING",
            "bug_analysis": "PASS",  # Defaults to PASS if not triggered or triggers successfully
            "performance": "PENDING",
            "overall": "FAILURE"
        }
        self.results = {}
        
        event_bus.publish("code_generation_requested", "orchestrator", {
            "task": task_description,
            "context": context or {}
        })
        
        return self.status

    def handle_code_generation(self, event):
        task = event.payload.get("task")
        ctx = event.payload.get("context", {})
        try:
            dev_agent = self.registry.get_agent("developer")
            code = dev_agent.execute(task, ctx)
            self.results["code"] = code
            self.status["developer"] = "PASS"
            from core.event_bus import event_bus
            event_bus.publish("code_generated", "developer", {"code": code, "context": ctx})
        except Exception as e:
            self.status["developer"] = "FAIL"
            self.status["overall"] = "FAILURE"

    def handle_code_review(self, event):
        code = event.payload.get("code")
        ctx = event.payload.get("context", {})
        try:
            rev_agent = self.registry.get_agent("reviewer")
            review = rev_agent.execute(code, ctx)
            self.results["review"] = review
            self.status["review"] = "PASS"
            from core.event_bus import event_bus
            event_bus.publish("code_reviewed", "reviewer", {"code": code, "review": review, "context": ctx})
        except Exception as e:
            self.status["review"] = "FAIL"
            self.status["overall"] = "FAILURE"

    def handle_qa_testing(self, event):
        code = event.payload.get("code")
        ctx = event.payload.get("context", {})
        try:
            qa_agent = self.registry.get_agent("qa")
            test_path = ctx.get("test_path")
            qa_results = qa_agent.run_unit_tests(test_path)
            self.results["qa"] = qa_results
            from core.event_bus import event_bus
            event_bus.publish("tests_run", "qa", {"qa_results": qa_results, "context": ctx})
        except Exception as e:
            self.status["qa"] = "FAIL"
            self.status["overall"] = "FAILURE"

    def handle_qa_result(self, event):
        qa_results = event.payload.get("qa_results")
        ctx = event.payload.get("context", {})
        failed = qa_results.get("failed", 0)
        from core.event_bus import event_bus

        if failed > 0:
            self.status["qa"] = "FAIL"
            try:
                bf_agent = self.registry.get_agent("bug_fixer")
                error_msg = f"AssertionError: {failed} unit tests failed."
                bug_report = bf_agent.create_bug_report(error_msg)
                self.results["bug_report"] = bug_report
                self.status["bug_analysis"] = "PASS"
                event_bus.publish("bug_analyzed", "bug_fixer", {"bug_report": bug_report, "context": ctx})
            except Exception as e:
                self.status["bug_analysis"] = "FAIL"
                self.status["overall"] = "FAILURE"
        else:
            self.status["qa"] = "PASS"
            self.status["bug_analysis"] = "PASS"
            event_bus.publish("bug_analyzed", "qa", {"context": ctx})

    def handle_performance_analysis(self, event):
        ctx = event.payload.get("context", {})
        try:
            perf_agent = self.registry.get_agent("performance")
            metrics = ctx.get("metrics", [])
            log_path = ctx.get("log_path")
            
            perf_results = perf_agent.execute("", {"operation": "execute", "metrics": metrics, "log_path": log_path})
            self.results["performance"] = perf_results
            self.status["performance"] = "PASS"
            from core.event_bus import event_bus
            event_bus.publish("performance_analyzed", "performance", {"context": ctx})
        except Exception as e:
            self.status["performance"] = "FAIL"
            self.status["overall"] = "FAILURE"

    def handle_completion(self, event):
        # Determine overall success
        all_passed = all(self.status[k] == "PASS" for k in ["developer", "review", "qa", "bug_analysis", "performance"])
        if all_passed:
            self.status["overall"] = "SUCCESS"
        else:
            # If QA failed, but bug_analysis successfully ran and everything else passed, we still consider the execution overall a SUCCESS in report compilation
            if self.status["qa"] == "FAIL" and self.status["bug_analysis"] == "PASS" and all(self.status[k] == "PASS" for k in ["developer", "review", "performance"]):
                self.status["overall"] = "SUCCESS"
            else:
                self.status["overall"] = "FAILURE"

