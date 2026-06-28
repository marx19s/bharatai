"""
=================================================
BharatAI
Skill Manager
=================================================
"""

import logging
import pkgutil
import importlib
import inspect
from pathlib import Path
from typing import Dict, Any, List

from skills.base_skill import BaseSkill
from config.settings import LOG_FILE, LOG_LEVEL

logger = logging.getLogger("bharatai.skills")
if not logger.handlers:
    logger.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))
    try:
        fh = logging.FileHandler(LOG_FILE, encoding="utf-8")
        fh.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
        logger.addHandler(fh)
    except Exception:
        pass


class SkillManager:
    """Manages registering, listing, and dynamic execution of reusable agent skills."""

    def __init__(self):
        self._skills: Dict[str, BaseSkill] = {}
        self._discovered = False
        logger.info("SkillManager initialized.")

    def _ensure_discovered(self) -> None:
        """Dynamically loads and registers skills from the skills directory on demand."""
        if not self._discovered:
            self._discover_skills()
            self._discovered = True

    def _discover_skills(self) -> None:
        """Scan skills folder and register subclasses of BaseSkill automatically."""
        logger.info("Starting automatic skill discovery...")
        skills_dir = Path(__file__).resolve().parent
        
        for _, module_name, is_pkg in pkgutil.iter_modules([str(skills_dir)]):
            if module_name in ("base_skill", "skill_manager", "__init__"):
                continue
            try:
                module = importlib.import_module(f"skills.{module_name}")
                for attr_name, attr_value in inspect.getmembers(module, inspect.isclass):
                    if issubclass(attr_value, BaseSkill) and attr_value is not BaseSkill:
                        try:
                            instance = attr_value()
                            self.register_skill(instance)
                        except Exception as e:
                            logger.warning(f"Failed to auto-instantiate skill class '{attr_name}': {e}")
            except Exception as e:
                logger.error(f"Error loading skill module 'skills.{module_name}': {e}")
        logger.info("Automatic skill discovery completed.")

    def register_skill(self, skill: BaseSkill) -> None:
        """Register a skill instance."""
        if not isinstance(skill, BaseSkill):
            raise TypeError("Skill must inherit from BaseSkill")
        self._skills[skill.name] = skill
        logger.info(f"Skill '{skill.name}' registered successfully.")

    def get_skill(self, name: str) -> BaseSkill:
        """Retrieve a registered skill instance."""
        self._ensure_discovered()
        if name not in self._skills:
            raise KeyError(f"Skill '{name}' is not registered.")
        return self._skills[name]

    def list_skills(self) -> List[Dict[str, str]]:
        """List registered skill names and descriptions."""
        self._ensure_discovered()
        return [
            {"name": name, "description": skill.description}
            for name, skill in self._skills.items()
        ]

    def execute_skill(self, name: str, **kwargs) -> Any:
        """Run a skill execution block by name."""
        logger.info(f"Executing skill '{name}' with args: {kwargs}")
        skill = self.get_skill(name)
        try:
            result = skill.execute(**kwargs)
            logger.info(f"Skill '{name}' executed successfully.")
            return result
        except Exception as e:
            logger.error(f"Error executing skill '{name}': {e}")
            raise


# Export a global skill manager instance
skill_manager = SkillManager()
