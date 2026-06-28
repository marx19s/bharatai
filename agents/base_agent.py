"""
=================================================
BharatAI
Base Agent Class
=================================================
"""

import time
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List

from models.manager import manager, ModelResponse
from core.task_category import TaskCategory

class BaseAgent(ABC):
    """
    Abstract base class for all agents in the BharatAI Operating System.
    Provides common infrastructure like logging, model manager invocation,
    response validation, and execution retries.
    """

    def __init__(self, name: str, role: str, model_manager: Optional[Any] = None):
        self.name = name
        self.role = role
        self.model_manager = model_manager or manager
        self.is_active = True
        self.logger = logging.getLogger(f"bharatai.agents.{name}")
        self.logger.info(f"Agent '{self.name}' ({self.role}) initialized.")

    def deactivate(self) -> None:
        """Deactivate the agent from receiving tasks."""
        self.is_active = False
        self.logger.info(f"Agent '{self.name}' deactivated.")

    def activate(self) -> None:
        """Activate the agent to receive tasks."""
        self.is_active = True
        self.logger.info(f"Agent '{self.name}' activated.")

    def health_check(self) -> bool:
        """Perform health check on the agent. By default, verifies provider availability."""
        try:
            status = self.model_manager.health_check()
            is_healthy = any(p["healthy"] for p in status.values())
            self.logger.info(f"Agent '{self.name}' health check: {'healthy' if is_healthy else 'unhealthy'}")
            return is_healthy
        except Exception as e:
            self.logger.error(f"Agent '{self.name}' health check failed: {e}")
            return False

    def _call_model(
        self,
        prompt: str,
        task: str = "general",
        provider: Optional[str] = None,
        model: Optional[str] = None,
        timeout: Optional[float] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> ModelResponse:
        """Helper wrapper around ModelManager.generate with detailed agent-level logging."""
        start_time = time.time()
        self.logger.info(f"Agent '{self.name}' invoking model. Task type: {task}")
        try:
            # Determine appropriate model based on task category
            if not model:
                try:
                    task_category = TaskCategory(task.lower())
                except Exception:
                    task_category = TaskCategory.GENERAL_CHAT
                model = self.model_manager.select_model(task_category)
            
            # Resolve actual timeout from settings based on task type
            if timeout is not None:
                actual_timeout = timeout
            else:
                from config import settings
                if task == "classification":
                    actual_timeout = getattr(settings, "CLASSIFICATION_TIMEOUT", 5.0)
                elif task == "planning":
                    actual_timeout = getattr(settings, "PLANNING_TIMEOUT", 60.0)
                elif task == "research":
                    actual_timeout = getattr(settings, "RESEARCH_TIMEOUT", 60.0)
                elif task == "synthesis":
                    actual_timeout = getattr(settings, "SYNTHESIS_TIMEOUT", 60.0)
                elif task in ("coding", "debugging"):
                    actual_timeout = getattr(settings, "CODING_TIMEOUT", 30.0)
                elif task == "fast":
                    actual_timeout = getattr(settings, "FAST_TIMEOUT", 10.0)
                else:
                    actual_timeout = getattr(settings, "FAST_TIMEOUT", 10.0)

            response = self.model_manager.generate(
                prompt=prompt,
                task=task,
                provider=provider,
                model=model,
                timeout=actual_timeout,
                config=config
            )
            duration = time.time() - start_time
            usage = getattr(response, "usage", {}) or {}
            queue_wait = usage.get("queue_wait_seconds", 0.0)
            model_exec = usage.get("model_execution_seconds", getattr(response, "duration", 0.0))
            fallback_seconds = usage.get("fallback_seconds", 0.0)
            self.logger.info(
                f"Agent '{self.name}' model invocation succeeded in {duration:.2f}s "
                f"using {response.provider}/{response.model} "
                f"(queue_wait={queue_wait:.2f}s model_exec={model_exec:.2f}s "
                f"fallback={fallback_seconds:.2f}s)."
            )
            return response
        except Exception as e:
            duration = time.time() - start_time
            self.logger.error(f"Agent '{self.name}' model invocation failed after {duration:.2f}s: {e}")
            raise

    def _validate_response(self, response_content: str, expectations: List[str]) -> bool:
        """
        Validate that the LLM response contains required sub-elements.
        Can be overridden by subclasses for more complex validations (e.g. JSON schemas).
        """
        if not response_content or not response_content.strip():
            self.logger.warning(f"Agent '{self.name}' validation failed: empty response content.")
            return False
            
        for expectation in expectations:
            if expectation not in response_content:
                self.logger.warning(
                    f"Agent '{self.name}' validation failed: expectation '{expectation}' not found in response."
                )
                return False
                
        return True

    def run_task(
        self,
        task: str,
        context: Optional[Dict[str, Any]] = None,
        expectations: Optional[List[str]] = None,
        max_attempts: int = 3,
    ) -> Any:
        """
        Execute task with retry and validation support.
        If validation fails, retry execution.
        """
        self.logger.info(f"Agent '{self.name}' starting execution of task: {task[:100]}...")
        attempt = 0
        last_error = None
        
        actual_max_attempts = max_attempts
        if context and "category" in context:
            from core.task_category import TaskCategory
            cat = context["category"]
            cat_str = cat.value if isinstance(cat, TaskCategory) else str(cat)
            if cat_str in ("coding", "debugging", "planning", "research", "document_analysis", "general_chat", "other"):
                actual_max_attempts = 1
        
        while attempt < actual_max_attempts:
            attempt += 1
            start_time = time.time()
            self.logger.info(f"Agent '{self.name}' execution attempt {attempt}/{actual_max_attempts}")
            try:
                result = self.execute(task, context)
                duration = time.time() - start_time
                
                if expectations:
                    result_str = str(result)
                    if self._validate_response(result_str, expectations):
                        self.logger.info(
                            f"Agent '{self.name}' task execution succeeded on attempt {attempt} in {duration:.2f}s."
                        )
                        return result
                    else:
                        raise ValueError("Response validation failed: missing expected elements.")
                else:
                    self.logger.info(
                        f"Agent '{self.name}' task execution succeeded on attempt {attempt} in {duration:.2f}s."
                    )
                    return result
            except Exception as e:
                duration = time.time() - start_time
                self.logger.warning(
                    f"Agent '{self.name}' attempt {attempt} failed in {duration:.2f}s: {e}"
                )
                last_error = e
                if attempt < actual_max_attempts:
                    time.sleep(2 ** attempt)
                    
        self.logger.error(f"Agent '{self.name}' execution failed after {actual_max_attempts} attempts: {last_error}")
        raise RuntimeError(f"Agent '{self.name}' failed task: {task}. Details: {last_error}")

    @abstractmethod
    def execute(self, task: str, context: Optional[Dict[str, Any]] = None) -> Any:
        """
        Abstract method to execute a task given context.
        Must be implemented by concrete agent subclasses.
        """
        pass
