import logging
import os
from threading import Lock

from config.settings import LOG_LEVEL

_logger = logging.getLogger(__name__)
if not _logger.handlers:
    _logger.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))


class DeveloperMode:
    """Singleton to manage developer mode flag across the application.

    The flag can be set via the environment variable ``DEV_MODE`` ("1" or "true")
    or programmatically at runtime (e.g., via a query parameter in the UI).
    When enabled, agents include detailed execution plans, timings, and internal
    logs in their responses.
    """

    _instance = None
    _lock = Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance.enabled = os.getenv("DEV_MODE", "0") in ("1", "true", "True")
        return cls._instance

    @classmethod
    def get_instance(cls):
        return cls()

    def enable(self):
        self.enabled = True
        _logger.info("Developer mode enabled")

    def disable(self):
        self.enabled = False
        _logger.info("Developer mode disabled")

    def is_enabled(self) -> bool:
        return self.enabled
