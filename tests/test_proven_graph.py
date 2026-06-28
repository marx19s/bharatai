import pytest
from core.task_category import TaskCategory
from core.task_classifier import TaskClassifier
from core.workflow_engine import workflow_engine
from models.manager import manager, ModelResponse

def test_single_provider_call_and_paraphrase_routing(monkeypatch):
    calls = []
    
    def fake_generate(prompt, task="general", provider=None, model=None, timeout=None, config=None):
        calls.append({
            "prompt": prompt,
            "task": task,
            "provider": provider,
            "model": model,
            "timeout": timeout,
            "config": config
        })
        if task == "classification":
            if "write a program" in prompt or "binary tree" in prompt:
                return ModelResponse(content="coding", model=model, provider="ollama")
            return ModelResponse(content="general_chat", model=model, provider="ollama")
        return ModelResponse(content="task output", model=model, provider="ollama")

    monkeypatch.setattr(manager, "generate", fake_generate)

    # Use a fresh classifier instance to avoid contamination
    classifier = TaskClassifier(model_manager=manager)
    workflow_engine.classifier = classifier
    
    # Paraphrased coding request (does not match any exact keywords)
    request_text = "Can you write a program to invert a binary tree?"
    
    # First classify (this registers it in cache)
    result = classifier.classify(request_text)
    assert result == TaskCategory.CODING
    
    # Exclude background warm-up "ping" calls if any
    task_calls = [c for c in calls if c["prompt"] != "ping"]
    assert len(task_calls) == 1  # Exactly 1 LLM classification call made
    
    # Clear calls list to measure workflow execution
    calls.clear()
    
    # Run the workflow
    workflow_result = workflow_engine.execute(request_text)
    
    assert workflow_result.category == TaskCategory.CODING
    
    # The classification is resolved from the cache (0 new calls),
    # and the Agent execution makes exactly 1 generate call.
    task_calls = [c for c in calls if c["prompt"] != "ping"]
    assert len(task_calls) == 1
    assert task_calls[0]["task"] == "coding"
