from __future__ import annotations

import json
import logging
import time
import uuid
from contextvars import ContextVar
from dataclasses import dataclass
from typing import Any


_request_id_var: ContextVar[str] = ContextVar("bharatai_request_id", default="-")
_request_start_var: ContextVar[float | None] = ContextVar("bharatai_request_start_perf", default=None)


@dataclass(frozen=True, slots=True)
class RequestTimingContext:
    request_id: str
    start_perf: float


class RequestTimingFilter(logging.Filter):
    """Inject request timing fields into every log record."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = getattr(record, "request_id", _request_id_var.get())
        record.stage = getattr(record, "stage", "-")
        record.elapsed_ms = getattr(record, "elapsed_ms", 0.0)
        record.cumulative_ms = getattr(record, "cumulative_ms", 0.0)
        return True


def create_request_context(request_id: str | None = None, start_perf: float | None = None) -> RequestTimingContext:
    request_id = request_id or uuid.uuid4().hex
    start_perf = time.perf_counter() if start_perf is None else start_perf
    _request_id_var.set(request_id)
    _request_start_var.set(start_perf)
    return RequestTimingContext(request_id=request_id, start_perf=start_perf)


def clear_request_context(token_id, token_start) -> None:
    _request_id_var.reset(token_id)
    _request_start_var.reset(token_start)


def get_request_context() -> RequestTimingContext | None:
    request_id = _request_id_var.get()
    start_perf = _request_start_var.get()
    if start_perf is None:
        return None
    return RequestTimingContext(request_id=request_id, start_perf=start_perf)


def log_timing(
    logger: logging.Logger,
    stage: str,
    stage_start_perf: float | None = None,
    message: str = "",
    **fields: Any,
) -> None:
    now = time.perf_counter()
    context = get_request_context()
    if context is None:
        context = RequestTimingContext(request_id=_request_id_var.get(), start_perf=now)

    stage_start_perf = stage_start_perf if stage_start_perf is not None else now
    elapsed_ms = (now - stage_start_perf) * 1000.0
    cumulative_ms = (now - context.start_perf) * 1000.0

    payload: dict[str, Any] = {
        "request_id": context.request_id,
        "stage": stage,
        "elapsed_ms": round(elapsed_ms, 3),
        "cumulative_ms": round(cumulative_ms, 3),
    }
    if message:
        payload["message"] = message
    if fields:
        payload.update(fields)

    logger.info("TIMING %s", json.dumps(payload, ensure_ascii=False, separators=(",", ":")))
