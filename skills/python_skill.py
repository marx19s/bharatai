"""
=================================================
BharatAI
Python Skill (Execution utility)
=================================================
"""

import sys
import math
from typing import Any
from skills.base_skill import BaseSkill

class PythonSkill(BaseSkill):
    """Python scripting and math utilities."""

    @property
    def name(self) -> str:
        return "python_exec"

    @property
    def description(self) -> str:
        return "Execute mathematical computations and simple Python code analysis."

    def execute(self, expression: str = "", code: str = "") -> Any:
        """Safe calculation/execution of mathematical statements or parsing code."""
        if expression:
            try:
                # Restrict eval context for basic math expressions safely
                allowed_names = {k: v for k, v in math.__dict__.items() if not k.startswith("__")}
                allowed_names.update({"abs": abs, "round": round, "pow": pow})
                result = eval(expression, {"__builtins__": {}}, allowed_names)
                return f"Math expression '{expression}' computed to: {result}"
            except Exception as e:
                return f"Failed to compute expression: {e}"
        elif code:
            # Code analysis/compilation mock
            try:
                compiled = compile(code, "<string>", "exec")
                return "Python code compilation check succeeded. Syntax is valid."
            except SyntaxError as se:
                return f"Python syntax check failed: {se}"
            except Exception as e:
                return f"Error analyzing python code: {e}"
        return "Please provide either an 'expression' or 'code' parameter."
