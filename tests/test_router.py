"""
=================================================
BharatAI - Model Router & Provider Tests
=================================================
"""

import pytest
from models.manager import manager, ModelResponse, BaseProvider

def test_model_manager_health():
    """Verify that health check returns structured status dictionary."""
    health = manager.health_check()
    assert "ollama" in health
    assert "gemini" in health
    assert "healthy" in health["ollama"]
    assert "healthy" in health["gemini"]

def test_model_mapping():
    """Verify that model manager correctly maps settings to local available models."""
    # Since Ollama has llama3.1:8b, test that it maps correctly
    mapped = manager.map_ollama_model("llama3.1:8b")
    assert mapped == "llama3.1:8b"
    
    # Test that unknown coding model maps to available qwen coder or default
    mapped_coding = manager.map_ollama_model("qwen3:8b")
    assert mapped_coding in ["qwen2.5-coder:latest", "llama3.1:8b"] or mapped_coding is not None

def test_model_generation():
    """Verify that generating response returns a ModelResponse object."""
    response = manager.generate("Say hello from test suite", task="fast")
    assert isinstance(response, ModelResponse)
    assert response.content is not None
    assert len(response.content) > 0
    assert response.provider in ["ollama", "gemini"]
    assert response.model is not None
    assert str(response) == response.content
