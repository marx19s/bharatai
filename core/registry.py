"""
=================================================
BharatAI
Agent Registry
=================================================
"""

import logging
import threading
import pkgutil
import importlib
import inspect
from pathlib import Path
from typing import Dict, Any, List

from agents.base_agent import BaseAgent
from config.settings import LOG_FILE, LOG_LEVEL

# Set up logging
logger = logging.getLogger("bharatai.core.registry")


class AgentRegistry:
    """
    Registry for managing life cycle, states, and retrieval of BharatAI agents.
    Supports dynamic auto-discovery from the agents directory.
    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._agents: Dict[str, BaseAgent] = {}
        self._lock = threading.Lock()
        self._discovered = False
        self._initialized = True
        logger.info("AgentRegistry initialized.")

    def _ensure_discovered(self) -> None:
        """Ensure auto-discovery has been executed (lazy load to avoid import loops)."""
        if not self._discovered:
            with self._lock:
                # Double-checked locking pattern
                if not self._discovered:
                    self._discover_agents()
                    self._discovered = True

    def _discover_agents(self) -> None:
        """Scan the agents directory and register subclasses of BaseAgent dynamically."""
        logger.info("Starting automatic agent discovery...")
        agents_dir = Path(__file__).resolve().parent.parent / "agents"
        
        if not agents_dir.exists():
            logger.warning(f"Agents directory does not exist: {agents_dir}")
            return

        for _, module_name, is_pkg in pkgutil.iter_modules([str(agents_dir)]):
            if module_name in ("base_agent", "__init__"):
                continue
                
            try:
                module = importlib.import_module(f"agents.{module_name}")
                
                for attr_name, attr_value in inspect.getmembers(module, inspect.isclass):
                    # Check if the class is a subclass of BaseAgent and is not BaseAgent itself
                    if issubclass(attr_value, BaseAgent) and attr_value is not BaseAgent:
                        try:
                            # Instantiate using default constructor
                            instance = attr_value()
                            self._register_agent_internal(instance.name, instance)
                            logger.info(f"Discovered and registered agent: '{instance.name}' (Class: {attr_name})")
                        except Exception as e:
                            logger.warning(
                                f"Failed to auto-instantiate agent class '{attr_name}' "
                                f"in agents.{module_name}: {e}"
                            )
            except Exception as e:
                logger.error(f"Error loading agent module 'agents.{module_name}': {e}")
        
        logger.info("Automatic agent discovery completed.")

    def register_agent(self, agent_name: str, agent_instance: BaseAgent) -> None:
        """Manually register an agent instance."""
        if not isinstance(agent_instance, BaseAgent):
            raise TypeError("Agent instance must inherit from BaseAgent")
        with self._lock:
            self._register_agent_internal(agent_name, agent_instance)

    def _register_agent_internal(self, agent_name: str, agent_instance: BaseAgent) -> None:
        self._agents[agent_name] = agent_instance
        logger.info(f"Agent '{agent_name}' registered successfully.")

    def unregister_agent(self, agent_name: str) -> None:
        """Unregister an agent by name."""
        self._ensure_discovered()
        with self._lock:
            if agent_name in self._agents:
                del self._agents[agent_name]
                logger.info(f"Agent '{agent_name}' unregistered.")
            else:
                logger.warning(f"Attempted to unregister non-existent agent: '{agent_name}'")

    def get_agent(self, agent_name: str) -> BaseAgent:
        """Retrieve registered agent instance by name."""
        self._ensure_discovered()
        with self._lock:
            agent = self._agents.get(agent_name)
            if not agent:
                raise KeyError(f"Agent '{agent_name}' is not registered.")
            return agent

    def list_agents(self) -> List[str]:
        """List the names of all registered agents."""
        self._ensure_discovered()
        with self._lock:
            return list(self._agents.keys())

    def health_check(self) -> Dict[str, bool]:
        """Run health checks on all registered agents."""
        self._ensure_discovered()
        with self._lock:
            agents_copy = list(self._agents.items())
            
        results = {}
        for name, agent in agents_copy:
            results[name] = agent.health_check()
        return results

    def activate_agent(self, agent_name: str) -> None:
        """Activate a registered agent."""
        self._ensure_discovered()
        with self._lock:
            agent = self._agents.get(agent_name)
            if not agent:
                raise KeyError(f"Agent '{agent_name}' is not registered.")
            agent.activate()

    def deactivate_agent(self, agent_name: str) -> None:
        """Deactivate a registered agent."""
        self._ensure_discovered()
        with self._lock:
            agent = self._agents.get(agent_name)
            if not agent:
                raise KeyError(f"Agent '{agent_name}' is not registered.")
            agent.deactivate()


# Export a global registry instance
registry = AgentRegistry()
