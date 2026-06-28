import json
import os
import time
from threading import Lock
from config.settings import LOG_LEVEL, LOG_FILE
import logging

_logger = logging.getLogger(__name__)

class MetricsCollector:
    """Collects and records execution metrics for workflows and agents.

    Writes a JSON line per request to `logs/metrics/<timestamp>.json`.
    """
    _lock = Lock()

    def __init__(self, metrics_dir: str = os.path.join(os.path.dirname(__file__), "../logs/metrics")):
        self.metrics_dir = os.path.abspath(metrics_dir)
        os.makedirs(self.metrics_dir, exist_ok=True)
        _logger.info(f"MetricsCollector initialized, directory: {self.metrics_dir}")

    def _write_entry(self, entry: dict):
        timestamp = int(time.time() * 1000)
        filename = os.path.join(self.metrics_dir, f"{timestamp}.json")
        with self._lock, open(filename, "w", encoding="utf-8") as f:
            json.dump(entry, f, indent=2)
        _logger.debug(f"Metrics entry written to {filename}")

    def record_workflow(self, category: str, agents: list):
        entry = {
            "type": "workflow",
            "category": category,
            "agents": agents,
            "timestamp": time.time(),
        }
        self._write_entry(entry)

    def record_agent(self, agent_name: str, latency: float):
        entry = {
            "type": "agent",
            "agent": agent_name,
            "latency": latency,
            "timestamp": time.time(),
        }
        self._write_entry(entry)
