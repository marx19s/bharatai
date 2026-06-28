from __future__ import annotations

import json
import os
import subprocess
from threading import Thread

import requests

os.environ["BHARATAI_DISABLE_SERVER_AUTOSTART"] = "1"

from app import APIRequestHandler, ThreadedHTTPServer
from core.task_category import TaskCategory
from core.workflow_engine import WorkflowEngine, workflow_engine


def patch_deterministic_workflow(monkeypatch, engine):
    monkeypatch.setattr(engine.classifier, "classify", lambda request: TaskCategory.RESEARCH)
    monkeypatch.setattr(
        engine,
        "_run_agent",
        lambda agent_cls, request: {"agent": agent_cls.__name__, "result": f"{agent_cls.__name__} completed"},
    )
    monkeypatch.setattr(engine.metrics, "record_agent", lambda **kwargs: None)
    monkeypatch.setattr(engine.metrics, "record_workflow", lambda **kwargs: None)


def start_server():
    server = ThreadedHTTPServer(("127.0.0.1", 0), APIRequestHandler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread, server.server_address[1]


def test_workflow_engine_supports_on_progress_callback(monkeypatch):
    engine = WorkflowEngine()
    patch_deterministic_workflow(monkeypatch, engine)
    progress_events: list[tuple[str, dict[str, object]]] = []

    result = engine.execute("Test workflow dispatch", on_progress=lambda event_type, payload: progress_events.append((event_type, payload)))

    assert result is not None
    assert len(progress_events) >= 1
    assert progress_events[0][0] == "classification_complete"
    assert "category" in progress_events[0][1]


def test_dispatch_sse_endpoint_streams_events(monkeypatch):
    patch_deterministic_workflow(monkeypatch, workflow_engine)
    server, thread, port = start_server()
    try:
        with requests.post(
            f"http://127.0.0.1:{port}/api/dispatch",
            json={"goal": "Test the dispatch workflow"},
            stream=True,
            timeout=30,
        ) as response:
            assert response.status_code == 200
            assert response.headers["Content-Type"].startswith("text/event-stream")

            events = []
            current_lines = []
            for line in response.iter_lines(chunk_size=1, decode_unicode=True):
                if line is None:
                    continue
                if line == "":
                    if current_lines:
                        raw = "\n".join(current_lines)
                        if raw.startswith("data: "):
                            event = json.loads(raw[6:])
                            events.append(event)
                            if event["event"] == "formatting_complete":
                                break
                        current_lines = []
                    continue

                current_lines.append(line)

            assert any(event["event"] == "classification_complete" for event in events)
            assert any(event["event"] == "research_complete" for event in events)
            assert any(event["event"] == "formatting_complete" for event in events)
    finally:
        server.shutdown()
        thread.join(timeout=5)


def test_dispatch_json_endpoint_returns_json_and_closes(monkeypatch):
    patch_deterministic_workflow(monkeypatch, workflow_engine)
    server, thread, port = start_server()
    try:
        response = requests.post(
            f"http://127.0.0.1:{port}/api/dispatch-json",
            json={"goal": "Test the JSON dispatch endpoint"},
            timeout=30,
        )

        assert response.status_code == 200
        assert response.headers["Content-Type"].startswith("application/json")

        payload = response.json()
        assert payload["success"] is True
        assert payload["goal"] == "Test the JSON dispatch endpoint"
        assert isinstance(payload["result"], str)
        assert payload["elapsed"] >= 0
        assert "workflow" in payload
    finally:
        server.shutdown()
        thread.join(timeout=5)


def test_invoke_rest_method_completes_against_dispatch_json(monkeypatch):
    patch_deterministic_workflow(monkeypatch, workflow_engine)
    server, thread, port = start_server()
    try:
        script = (
            f"$body = '{{\"goal\":\"Test the JSON dispatch endpoint\"}}'; "
            f"$result = Invoke-RestMethod -Uri 'http://127.0.0.1:{port}/api/dispatch-json' "
            "-Method Post -ContentType 'application/json' -Body $body; "
            "if (-not $result.success) { exit 2 }; "
            "if ([string]::IsNullOrWhiteSpace($result.result)) { exit 3 }; "
            "$result | ConvertTo-Json -Compress"
        )

        completed = subprocess.run(
            ["powershell", "-NoProfile", "-Command", script],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )

        assert completed.returncode == 0, completed.stderr
        assert '"success":true' in completed.stdout
        assert '"goal":"Test the JSON dispatch endpoint"' in completed.stdout
    finally:
        server.shutdown()
        thread.join(timeout=5)
