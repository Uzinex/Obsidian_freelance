"""Простейший in-memory TTL cache для эмбеддингов и подсказок."""

from __future__ import annotations

import time
from collections.abc import MutableMapping
from threading import Lock
from typing import Any


class TTLCache(MutableMapping[str, Any]):
    def __init__(self, ttl_seconds: float = 3600) -> None:
        self._ttl = ttl_seconds
        self._store: dict[str, tuple[float, Any]] = {}
        self._lock = Lock()

    def __getitem__(self, key: str) -> Any:  # pragma: no cover - trivial
        value = self._store[key][1]
        return value

    def __setitem__(self, key: str, value: Any) -> None:
        with self._lock:
            self._store[key] = (time.time() + self._ttl, value)

    def __delitem__(self, key: str) -> None:  # pragma: no cover - unused
        with self._lock:
            del self._store[key]

    def __iter__(self):  # pragma: no cover - not used
        return iter(self._store)

    def __len__(self) -> int:  # pragma: no cover - not used
        return len(self._store)

    def get(self, key: str) -> Any | None:
        record = self._store.get(key)
        if not record:
            return None
        expires_at, value = record
        if expires_at < time.time():
            with self._lock:
                self._store.pop(key, None)
            return None
        return value
