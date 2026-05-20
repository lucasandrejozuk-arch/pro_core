from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from threading import Lock


@dataclass
class SlidingWindowRateLimiter:
    _attempts: dict[str, deque[datetime]] = field(default_factory=dict)
    _lock: Lock = field(default_factory=Lock)

    def is_limited(self, key: str, max_attempts: int, window_seconds: int) -> bool:
        with self._lock:
            self._prune(key, window_seconds)
            return len(self._attempts.get(key, ())) >= max_attempts

    def record_failure(self, key: str, window_seconds: int) -> None:
        with self._lock:
            self._prune(key, window_seconds)
            self._attempts.setdefault(key, deque()).append(datetime.now(UTC))

    def clear(self, key: str) -> None:
        with self._lock:
            self._attempts.pop(key, None)

    def reset(self) -> None:
        with self._lock:
            self._attempts.clear()

    def _prune(self, key: str, window_seconds: int) -> None:
        attempts = self._attempts.get(key)
        if attempts is None:
            return

        threshold = datetime.now(UTC) - timedelta(seconds=window_seconds)
        while attempts and attempts[0] <= threshold:
            attempts.popleft()

        if not attempts:
            self._attempts.pop(key, None)


login_rate_limiter = SlidingWindowRateLimiter()
