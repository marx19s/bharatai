from __future__ import annotations

import json
import threading
import time
from types import SimpleNamespace

import pytest

from agents.atlas import ATLASAgent
from agents.neo import NEOAgent
from agents.orion import ORIONAgent
from config.settings import (
    CLASSIFICATION_TIMEOUT,
    DEFAULT_MODEL,
    FAST_MODEL,
    FAST_TIMEOUT,
    PLANNING_TIMEOUT,
    RESEARCH_TIMEOUT,
    SYNTHESIS_TIMEOUT,
)
from core.task_category import TaskCategory
from core.task_classifier import TaskClassifier
from memory.memory_manager import memory_manager
from models.manager import ModelResponse, manager


def test_classifier_uses_small_model_and_short_timeout(monkeypatch):
    captured: dict[str, object] = {}

    def fake_generate(**kwargs):
        captured.update(kwargs)
        return SimpleNamespace(content="research")

    monkeypatch.setattr(manager, "generate", fake_generate)

    classifier = TaskClassifier(model_manager=manager)
    result = classifier.classify("find the latest docs")

    assert result == TaskCategory.RESEARCH
    assert captured["provider"] == "ollama"
    assert captured["model"] == "phi3:medium"
    assert captured["task"] == "classification"
    assert captured["timeout"] == CLASSIFICATION_TIMEOUT


def test_atlas_uses_fast_model_and_planning_timeout(monkeypatch):
    captured: dict[str, object] = {}
    atlas = ATLASAgent()
    monkeypatch.setattr(memory_manager.session, "get", lambda key: None)
    monkeypatch.setattr(memory_manager.session, "set", lambda *args, **kwargs: None)

    def fake_call_model(**kwargs):
        captured.update(kwargs)
        return SimpleNamespace(
            content=json.dumps(
                [
                    {
                        "id": "task_1",
                        "description": "Research the project",
                        "priority": 1,
                        "dependencies": [],
                        "assigned_agent": "orion",
                    }
                ]
            )
        )

    monkeypatch.setattr(atlas, "_call_model", fake_call_model)

    plan = atlas.execute("Build a launch plan")

    assert json.loads(plan)[0]["assigned_agent"] == "orion"
    assert captured["provider"] == "ollama"
    assert captured["model"] == FAST_MODEL
    assert captured["task"] == "planning"
    assert captured["timeout"] == PLANNING_TIMEOUT


def test_orion_uses_fast_model_and_research_timeout(monkeypatch):
    captured: dict[str, object] = {}
    orion = ORIONAgent()
    monkeypatch.setattr(memory_manager.session, "get", lambda key: None)
    monkeypatch.setattr(memory_manager.session, "set", lambda *args, **kwargs: None)

    def fake_call_model(**kwargs):
        captured.update(kwargs)
        return SimpleNamespace(content="Synthesis complete")

    monkeypatch.setattr(orion, "_call_model", fake_call_model)

    report = orion.execute("research local docs for the project")

    assert "Synthesis complete" in report
    assert captured["provider"] == "ollama"
    assert captured["model"] == FAST_MODEL
    assert captured["task"] == "research"
    assert captured["timeout"] == RESEARCH_TIMEOUT


def test_neo_uses_default_model_only_for_final_synthesis(monkeypatch):
    neo = NEOAgent()
    plan = json.dumps(
        [
            {
                "id": "task_1",
                "description": "Draft the status note",
                "priority": 1,
                "dependencies": [],
                "assigned_agent": "default",
            }
        ]
    )

    monkeypatch.setattr(
        memory_manager.session,
        "get",
        lambda key: plan if key.startswith("plan_") else None,
    )
    monkeypatch.setattr(memory_manager.session, "set", lambda *args, **kwargs: None)

    calls: list[dict[str, object]] = []

    def fake_call_model(**kwargs):
        calls.append(kwargs)
        if len(calls) == 1:
            return SimpleNamespace(content="task result")
        return SimpleNamespace(content="final synthesis")

    monkeypatch.setattr(neo, "_call_model", fake_call_model)

    report = neo.execute("Need an executive summary")

    assert "final synthesis" in report
    assert calls[0]["model"] == FAST_MODEL
    assert calls[0]["task"] == "fast"
    assert calls[0]["timeout"] == FAST_TIMEOUT
    assert calls[1]["model"] == DEFAULT_MODEL
    assert calls[1]["task"] == "synthesis"
    assert calls[1]["timeout"] == SYNTHESIS_TIMEOUT


@pytest.mark.parametrize("task_name", ["planning", "research"])
def test_timeout_skips_gemini_fallback(monkeypatch, task_name):
    ollama_provider = manager.providers["ollama"]
    gemini_provider = manager.providers["gemini"]
    gemini_called = {"value": False}

    def fake_ollama_generate(*args, **kwargs):
        raise TimeoutError("ollama timed out")

    def fake_gemini_generate(*args, **kwargs):
        gemini_called["value"] = True
        raise AssertionError("Gemini fallback should not be used for timeouts")

    monkeypatch.setattr(ollama_provider, "generate", fake_ollama_generate)
    monkeypatch.setattr(gemini_provider, "generate", fake_gemini_generate)

    with pytest.raises(TimeoutError):
        manager.generate(
            "performance-sensitive request",
            task=task_name,
            provider="ollama",
            model=FAST_MODEL,
            timeout=15.0,
        )

    assert gemini_called["value"] is False


def test_default_model_requests_are_serialized(monkeypatch):
    ollama_provider = manager.providers["ollama"]
    state = {"active": 0, "max": 0}
    lock = threading.Lock()
    monkeypatch.setattr(manager, "map_ollama_model", lambda requested_model: requested_model)

    def fake_generate(prompt, model, timeout=None, config=None):
        with lock:
            state["active"] += 1
            state["max"] = max(state["max"], state["active"])
        time.sleep(0.15)
        with lock:
            state["active"] -= 1
        return ModelResponse(content="ok", model=model, provider="ollama")

    monkeypatch.setattr(ollama_provider, "generate", fake_generate)

    responses: list[ModelResponse] = []

    def run_request():
        responses.append(
            manager.generate(
                "final synthesis request",
                task="synthesis",
                provider="ollama",
                model=DEFAULT_MODEL,
                timeout=30.0,
            )
        )

    t1 = threading.Thread(target=run_request)
    t2 = threading.Thread(target=run_request)
    t1.start()
    t2.start()
    t1.join(timeout=5)
    t2.join(timeout=5)

    assert len(responses) == 2
    assert state["max"] == 1
    assert "queue_wait_seconds" in responses[0].usage
    assert "model_execution_seconds" in responses[0].usage
    assert "total_generation_seconds" in responses[0].usage
