from collections import defaultdict, deque
from datetime import datetime, timedelta, timezone
from threading import Lock


class InMemoryRateLimiter:
    """Small dev-friendly limiter. Replace with Redis before multi-instance deploys."""

    def __init__(self):
        self._hits: dict[str, deque[datetime]] = defaultdict(deque)
        self._lock = Lock()

    def allow(self, key: str, limit: int, window_seconds: int) -> tuple[bool, int]:
        now = datetime.now(timezone.utc)
        window_start = now - timedelta(seconds=window_seconds)

        with self._lock:
            hits = self._hits[key]
            while hits and hits[0] < window_start:
                hits.popleft()

            remaining = max(limit - len(hits), 0)
            if remaining <= 0:
                return False, 0

            hits.append(now)
            return True, remaining - 1


rate_limiter = InMemoryRateLimiter()
