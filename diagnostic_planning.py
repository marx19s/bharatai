import time
import json
from config.settings import PLANNING_MODEL, PLANNING_TIMEOUT
from models.manager import manager

def run_diagnostic():
    agents_list_str = "- No agents available."
    task = "Plan a simple e‑commerce website backend in Python"
    planning_prompt = f"""
You are ATLAS, the Planner Agent of BharatAI. Your role is to decompose a user's high-level goal into logical, prioritized subtasks.
You must construct a plan where tasks can depend on other tasks (Directed Acyclic Graph).

User Goal: {task}

Available Agents in Registry:
{agents_list_str}

Please plan the tasks, specifying priorities and dependencies. Assign each subtask to the most appropriate agent.
Available agents you can assign:
- \"orion\" (for docs search, web research, git research)
- \"echo\" (for mock repeats or simple tests)
- \"neo\" (for executive summaries or CEO guidance)
- \"default\" (for general text generation steps)
- Or any other agent name listed in the registry above.

Format your response as a valid JSON array of objects. Each object must have:
- \"id\": A unique task ID string (e.g., \"task_1\", \"task_2\")
- \"description\": Description of what the task should accomplish
- \"priority\": Integer priority (1 is highest priority)
- \"dependencies\": A JSON list of task IDs that this task depends on (e.g. [\"task_1\"] or [])
- \"assigned_agent\": The recommended agent name to execute the task

Your response must contain ONLY the raw JSON array. Do not include markdown code block styling or conversational text.
"""
    prompt_len = len(planning_prompt)
    est_tokens = prompt_len // 4  # rough estimate 4 chars per token
    print('[DIAG] Prompt length (chars):', prompt_len)
    print('[DIAG] Estimated tokens:', est_tokens)
    start = time.time()
    resp = manager.generate(
        prompt=planning_prompt,
        task='planning',
        provider='ollama',
        model=PLANNING_MODEL,
        timeout=PLANNING_TIMEOUT,
        config=None,
    )
    total_elapsed = time.time() - start
    usage = resp.usage
    print('[DIAG] Generation total duration (s):', total_elapsed)
    print('[DIAG] Queue wait seconds:', usage.get('queue_wait_seconds'))
    print('[DIAG] Model execution seconds:', usage.get('model_execution_seconds'))
    print('[DIAG] Prompt tokens:', usage.get('prompt_tokens'))
    print('[DIAG] Completion tokens:', usage.get('completion_tokens'))
    print('[DIAG] Total tokens:', usage.get('total_tokens'))
    print('[DIAG] Response length (chars):', len(resp.content))
    print('[DIAG] Response snippet:', resp.content[:200])

if __name__ == '__main__':
    run_diagnostic()
