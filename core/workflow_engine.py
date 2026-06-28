import logging
import time
from time import perf_counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Any

from core.task_category import TaskCategory
from core.task_classifier import TaskClassifier
from core.developer_mode import DeveloperMode
from core.metrics import MetricsCollector
from models.manager import ModelManager, manager
from services.request_timing import log_timing

# Import agent classes (assuming they exist in agents package)
from agents.orion import ORIONAgent
from agents.atlas import ATLASAgent
from agents.neo import NEOAgent

logger = logging.getLogger(__name__)
if not logger.handlers:
    logger.setLevel(logging.INFO)


class WorkflowResult:
    """Container for the overall result of a workflow execution."""

    def __init__(self, category: TaskCategory, payload: Dict[str, Any]):
        self.category = category
        self.payload = payload
        self.timestamp = time.time()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "category": self.category.value,
            "payload": self.payload,
            "timestamp": self.timestamp,
        }


class WorkflowEngine:
    """Orchestrates agents based on task classification.

    The engine selects agents required for the given request, runs them (in
    parallel where independent), gathers their outputs, and returns a structured
    ``WorkflowResult``.
    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    # Mapping from category to required agents (order matters for dependencies)
    _pipeline_map: Dict[TaskCategory, List[Any]] = {
        TaskCategory.CODING: [NEOAgent],
        TaskCategory.RESEARCH: [ORIONAgent],
        TaskCategory.DEBUGGING: [NEOAgent],
        TaskCategory.PLANNING: [NEOAgent],
        TaskCategory.DOCUMENT_ANALYSIS: [ORIONAgent],
        TaskCategory.GENERAL_CHAT: [NEOAgent],
        TaskCategory.OTHER: [NEOAgent],
    }

    _agent_dependencies = {
        "NEOAgent": ["ATLASAgent"],
    }

    def __init__(self):
        if self._initialized:
            return
        self.classifier = TaskClassifier()
        self.dev_mode = DeveloperMode.get_instance()
        self.metrics = MetricsCollector()
        self.model_manager = manager
        self._initialized = True

    def _run_agent(self, agent_cls, request: str, category: TaskCategory) -> Dict[str, Any]:
        """Instantiate and run a single agent, returning its raw output dict."""
        agent_name = agent_cls.__name__
        logger.info(f"[LOG] {agent_name} started execution")
        agent_stage_start = perf_counter()
        log_timing(logger, "agent_start", agent_stage_start, message=agent_name)
        print("Agent")
        import sys; sys.stdout.buffer.write(b"\xe2\x86\x93\n"); sys.stdout.flush()
        try:
            # Instantiate agent correctly (no constructor arguments)
            agent = agent_cls()
            start = time.time()
            
            # Run task with base_agent's retry/validation infrastructure
            result = agent.run_task(request, context={"category": category})
            
            elapsed = time.time() - start
            self.metrics.record_agent(agent_name=agent_name, latency=elapsed)
            logger.info(f"[LOG] {agent_name} finished execution in {elapsed:.2f}s")
            log_timing(logger, "agent_end", agent_stage_start, message=agent_name)
            return {"agent": agent_name, "result": result}
        except Exception as e:
            logger.error(f"[LOG] {agent_name} execution failed: {e}")
            log_timing(logger, "agent_end", agent_stage_start, message=f"{agent_name} failed", error=str(e))
            return {"agent": agent_name, "result": f"Execution failed: {str(e)}"}

    def execute(self, request: str, on_progress=None) -> WorkflowResult:
        """Classify the request, run the appropriate pipeline, and return result."""
        print("WorkflowEngine")
        import sys; sys.stdout.buffer.write(b"\xe2\x86\x93\n"); sys.stdout.flush()
        workflow_start = perf_counter()
        logger.info(f"[LOG] Request received: '{request[:100]}'")
        
        # 1. Classification
        classification_start = perf_counter()
        log_timing(logger, "task_classification_start", classification_start, message=request[:100])
        category = self.classifier.classify(request)
        logger.info(f"[LOG] Task classified: {category.value}")
        log_timing(logger, "task_classification_end", classification_start, message=category.value)
        if on_progress:
            on_progress("classification_complete", {"category": category.value})
        
        # 2. Pipeline mapping
        workflow_construction_start = perf_counter()
        agents = self._pipeline_map.get(category, [])
        agents_seq = [a.__name__ for a in agents]
        print(f"\n[DIAGNOSTIC] Request Goal: '{request}'")
        print(f"[DIAGNOSTIC] Task Category: {category.value}")
        print(f"[DIAGNOSTIC] Agent Sequence: {agents_seq}")
        logger.info(f"[LOG] Workflow created with agents: {agents_seq}")
        log_timing(
            logger,
            "workflow_construction",
            workflow_construction_start,
            message=f"agents={agents_seq}",
        )
        
        results: List[Dict[str, Any]] = []
        if agents:
            # Build topological dependency graph for executing agents in parallel
            completed_agents: Dict[str, Any] = {}
            pending_agents = {a.__name__: a for a in agents}
            dependencies = {
                a.__name__: [dep for dep in self._agent_dependencies.get(a.__name__, []) if dep in pending_agents]
                for a in agents
            }
            
            # Run agents sequentially to respect dependencies and prevent VRAM/CPU thrashing on local Ollama
            completed_agents: Dict[str, Any] = {}
            pending_agents = {a.__name__: a for a in agents}
            dependencies = {
                a.__name__: [dep for dep in self._agent_dependencies.get(a.__name__, []) if dep in pending_agents]
                for a in agents
            }
            
            try:
                start_time = time.time()
                while pending_agents and (time.time() - start_time < 180.0):
                    # Find all agents with no remaining dependencies
                    runnable_names = [name for name, deps in dependencies.items() if not deps and name in pending_agents]
                    if not runnable_names:
                        break
                    
                    # Execute the first runnable agent synchronously
                    name = runnable_names[0]
                    agent_cls = pending_agents.pop(name)
                    if name == "NEOAgent":
                        logger.info("[LOG] NEO started")
                    
                    try:
                        import inspect
                        sig = inspect.signature(self._run_agent)
                        num_params = len(sig.parameters)
                        has_var_positional = any(p.kind == inspect.Parameter.VAR_POSITIONAL for p in sig.parameters.values())
                        if num_params >= 3 or has_var_positional:
                            res = self._run_agent(agent_cls, request, category)
                        else:
                            res = self._run_agent(agent_cls, request)
                        results.append(res)
                        completed_agents[name] = res
                        
                        # Log agent milestones and trigger progress callbacks
                        if name == "ATLASAgent":
                            logger.info("[LOG] ATLAS finished")
                            if on_progress:
                                on_progress("planning_complete", {"result": res.get("result")})
                        elif name == "ORIONAgent":
                            logger.info("[LOG] ORION finished")
                            if on_progress:
                                on_progress("research_complete", {"result": res.get("result")})
                    except Exception as e:
                        logger.error(f"Agent {name} failed: {e}")
                        results.append({"agent": name, "result": f"Exception: {e}"})
                    
                    # Remove this completed agent from all dependencies
                    for dep_name in dependencies:
                        if name in dependencies[dep_name]:
                            dependencies[dep_name].remove(name)
                            
                if time.time() - start_time >= 180.0:
                    raise TimeoutError("Execution timed out after 180 seconds.")
            except TimeoutError as te:
                logger.error(f"[LOG] Workflow execution timed out: {te}")
                results.append({"agent": "engine", "result": "Workflow execution timed out."})
        else:
            results.append({"agent": "none", "result": "No specialized agents required."})

        payload = {"category": category.value, "agents": results}
        self.metrics.record_workflow(category=category.value, agents=[a.__name__ for a in agents])
        workflow_result = WorkflowResult(category, payload)
        total_elapsed = perf_counter() - workflow_start
        logger.info(f"[LOG] Workflow total time: {total_elapsed:.2f}s")
        log_timing(logger, "workflow_total", workflow_start, message=f"category={category.value}")
        return workflow_result


# Export global workflow engine instance
workflow_engine = WorkflowEngine()
