"""
=================================================
BharatAI
Research Agent - ORION
=================================================
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional

from agents.base_agent import BaseAgent
from skills.skill_manager import skill_manager
from core.event_bus import event_bus
from config.settings import ROOT_DIR, FAST_MODEL, RESEARCH_TIMEOUT
from memory.memory_manager import memory_manager

class ORIONAgent(BaseAgent):
    """
    Research Agent (ORION). Handles documentation scans, local workspace queries,
    and leverages WebSkill/GitSkill for search operations.
    """

    def __init__(self, model_manager: Optional[Any] = None):
        super().__init__(
            name="orion",
            role="Research Specialist (Local documentation and workspace query routing)",
            model_manager=model_manager
        )

    def execute(self, task: str, context: Optional[Dict[str, Any]] = None) -> Any:
        # Check cache to prevent redundant execution
        cache_key = f"research_{task.strip().lower()}"
        cached = memory_manager.session.get(cache_key)
        if cached:
            self.logger.info("Using cached research results from session memory.")
            return cached
            
        self.logger.info(f"ORION executing research task: '{task}'")
        
        # Publish event
        event_bus.publish("TaskStarted", self.name, {"task": task})

        task_lower = task.lower()
        research_data = ""

        # 1. GitHub / Repo search logic (GitHub-ready)
        if "github" in task_lower or "repo" in task_lower or "git" in task_lower:
            self.logger.info("ORION directing task to GitSkill...")
            git_res = skill_manager.execute_skill("git_ops", action="issues")
            research_data += f"\n[Git/GitHub Operations Result]:\n{git_res}\n"

        # 2. Web search logic (Web-search-ready)
        if "web" in task_lower or "search" in task_lower or "online" in task_lower or "latest" in task_lower:
            self.logger.info("ORION directing task to WebSkill...")
            web_res = skill_manager.execute_skill("web_search", query=task)
            research_data += f"\n[Web Search Result]:\n{web_res}\n"

        # 3. Local codebase/documentation search logic
        if "local" in task_lower or "doc" in task_lower or "file" in task_lower or "system" in task_lower:
            self.logger.info("ORION scanning local documentation folder...")
            docs_dir = ROOT_DIR / "docs"
            found_docs = []
            if docs_dir.exists():
                for root, _, files in os.walk(docs_dir):
                    for file in files:
                        if file.endswith((".md", ".txt")):
                            found_docs.append(file)
            
            if found_docs:
                doc_list = ", ".join(found_docs)
                research_data += f"\n[Local Documentation Files Found]:\n{doc_list}\n"
            else:
                research_data += "\n[Local Documentation]: No local documentation files found in docs/ folder.\n"

        # If no specialized search matched, run default web and local mock
        if not research_data:
            self.logger.info("No specialized research targets matched. Running general search mock...")
            web_res = skill_manager.execute_skill("web_search", query=task)
            research_data = f"\n[General Search Summary]:\n{web_res}\n"

        # 4. Use LLM to synthesize research findings
        synthesis_prompt = f"""
You are ORION, the Research Agent of BharatAI. Your task is to analyze research data gathered for a query, synthesize findings, and provide a clear report.

User Query: {task}

Raw Research Data:
{research_data}

Write a comprehensive, professional research summary answering the user's query based on the findings.
"""
        self.logger.info("Synthesizing research data via ModelManager...")
        try:
            res = self._call_model(
                prompt=synthesis_prompt,
                task="research",
                provider="ollama",
                model=FAST_MODEL,
                timeout=RESEARCH_TIMEOUT,
            )
            report = res.content
        except Exception as e:
            self.logger.error(f"Failed to synthesize research report: {e}")
            report = f"Research Report for: '{task}'\nFindings:\n{research_data}"

        # Save to session memory cache
        memory_manager.session.set(cache_key, report)

        # Publish completion event
        event_bus.publish("TaskCompleted", self.name, {"task": task, "result": report})

        return report
