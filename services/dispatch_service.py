from __future__ import annotations

import logging
import time
from time import perf_counter
from dataclasses import dataclass
from typing import Any, Callable

from agents.lumina import LUMINAAgent
from core.developer_mode import DeveloperMode
from core.task_category import TaskCategory
from core.workflow_engine import WorkflowResult, workflow_engine
from services.request_timing import log_timing

ProgressCallback = Callable[[str, dict[str, Any]], None]
logger = logging.getLogger("bharatai.dispatch")


@dataclass(slots=True)
class DispatchExecution:
    workflow_result: WorkflowResult
    formatted_output: str
    elapsed: float


def execute_dispatch_workflow(
    goal: str,
    on_progress: ProgressCallback | None = None,
) -> DispatchExecution:
    """Run the workflow and format the final result with LUMINA."""

    start_time = perf_counter()

    try:
        workflow_start = perf_counter()
        workflow_result = workflow_engine.execute(
            goal,
            on_progress=on_progress,
        )
        log_timing(
            logger,
            "workflow_result_ready",
            workflow_start,
            message="workflow execution completed",
        )
    except Exception as exc:
        logger.error(f"Workflow execution failed: {exc}")
        workflow_result = None

    try:
        formatting_start = perf_counter()
        log_timing(
            logger,
            "lumina_formatting_start",
            formatting_start,
            message="starting formatting",
        )

        lumina = LUMINAAgent()
        dev_mode = DeveloperMode.get_instance().is_enabled()

        if workflow_result is not None:
            formatted_output = lumina.format(
                workflow_result,
                developer_mode=dev_mode,
            )
        else:
            formatted_output = "Workflow execution failed."

        if not isinstance(formatted_output, str):
            formatted_output = str(formatted_output)

        log_timing(
            logger,
            "lumina_formatting_end",
            formatting_start,
            message="formatting complete",
        )

    except Exception as exc:
        formatted_output = f"Execution completed, but formatting failed: {exc}"

    elapsed = perf_counter() - start_time

    log_timing(
        logger,
        "dispatch_total",
        start_time,
        message="dispatch workflow complete",
    )

    return DispatchExecution(
        workflow_result=workflow_result,
        formatted_output=formatted_output,
        elapsed=elapsed,
    )