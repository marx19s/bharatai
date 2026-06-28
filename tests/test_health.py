import json
import pytest
import requests
from unittest.mock import MagicMock, patch
from app import APIRequestHandler, ThreadedHTTPServer
from core.workflow_engine import WorkflowEngine
from core.registry import AgentRegistry
from models.manager import ModelManager, OllamaProvider, GeminiProvider

def start_server():
    server = ThreadedHTTPServer(("127.0.0.1", 0), APIRequestHandler)
    import threading
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread, server.server_address[1]

def test_health_endpoint_healthy(monkeypatch):
    # Mock WorkflowEngine, AgentRegistry, ModelManager and providers to represent a healthy state
    
    # 1. Mock workflow engine initialization
    mock_engine = MagicMock()
    mock_engine._initialized = True
    monkeypatch.setattr("core.workflow_engine.workflow_engine", mock_engine)
    
    # 2. Mock registry initialization
    mock_registry = MagicMock()
    mock_registry._initialized = True
    mock_registry.list_agents.return_value = ["agent1", "agent2"]
    monkeypatch.setattr("core.registry.registry", mock_registry)
    
    # 3. Mock model manager initialization and providers
    mock_manager = MagicMock()
    mock_manager._initialized = True
    
    mock_ollama_prov = MagicMock(spec=OllamaProvider)
    mock_ollama_prov.host = "http://localhost:11434"
    
    mock_gemini_prov = MagicMock(spec=GeminiProvider)
    mock_gemini_prov.client = MagicMock()
    mock_gemini_prov.api_key = "fake_key"
    
    mock_manager.providers = {
        "ollama": mock_ollama_prov,
        "gemini": mock_gemini_prov
    }
    monkeypatch.setattr("models.manager.manager", mock_manager)
    
    # Mock the actual ollama.Client and genai.Client calls inside the endpoint handler
    mock_ollama_client = MagicMock()
    mock_ollama_client.list.return_value = MagicMock(models=[MagicMock(model="llama3.1:8b")])
    
    mock_gemini_client = MagicMock()
    
    with patch("ollama.Client", return_value=mock_ollama_client), \
         patch("google.genai.Client", return_value=mock_gemini_client):
         
        server, thread, port = start_server()
        try:
            response = requests.get(f"http://127.0.0.1:{port}/api/health", timeout=5)
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["ready"] is True
            assert data["components"]["api"]["healthy"] is True
            assert data["components"]["workflow_engine"]["healthy"] is True
            assert data["components"]["agent_registry"]["healthy"] is True
            assert data["components"]["agent_registry"]["registered_agents"] == 2
            assert data["components"]["ollama"]["healthy"] is True
            assert data["components"]["ollama"]["reachable"] is True
            assert "llama3.1:8b" in data["components"]["ollama"]["available_models"]
            assert data["components"]["gemini"]["healthy"] is True
            assert data["components"]["gemini"]["configured"] is True
        finally:
            server.shutdown()
            thread.join(timeout=5)

def test_health_endpoint_degraded(monkeypatch):
    # Mock workflow engine, registry, manager to be healthy, but Ollama is offline and Gemini is unconfigured.
    
    mock_engine = MagicMock()
    mock_engine._initialized = True
    monkeypatch.setattr("core.workflow_engine.workflow_engine", mock_engine)
    
    mock_registry = MagicMock()
    mock_registry._initialized = True
    mock_registry.list_agents.return_value = []
    monkeypatch.setattr("core.registry.registry", mock_registry)
    
    mock_manager = MagicMock()
    mock_manager._initialized = True
    
    mock_ollama_prov = MagicMock(spec=OllamaProvider)
    mock_ollama_prov.host = "http://localhost:11434"
    
    mock_gemini_prov = MagicMock(spec=GeminiProvider)
    mock_gemini_prov.client = None # Unconfigured
    
    mock_manager.providers = {
        "ollama": mock_ollama_prov,
        "gemini": mock_gemini_prov
    }
    monkeypatch.setattr("models.manager.manager", mock_manager)
    
    # Mock ollama.Client.list to raise connection error
    mock_ollama_client = MagicMock()
    mock_ollama_client.list.side_effect = Exception("Connection refused")
    
    with patch("ollama.Client", return_value=mock_ollama_client):
        server, thread, port = start_server()
        try:
            response = requests.get(f"http://127.0.0.1:{port}/api/health", timeout=5)
            assert response.status_code == 200 # Must return 200 even if degraded!
            data = response.json()
            assert data["success"] is True
            assert data["ready"] is False # Not ready because no healthy providers
            assert data["components"]["ollama"]["healthy"] is False
            assert data["components"]["ollama"]["reachable"] is False
            assert data["components"]["gemini"]["healthy"] is False
            assert data["components"]["gemini"]["configured"] is False
        finally:
            server.shutdown()
            thread.join(timeout=5)
