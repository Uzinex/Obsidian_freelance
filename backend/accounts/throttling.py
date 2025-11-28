from __future__ import annotations

from typing import Any

import re

from rest_framework.throttling import SimpleRateThrottle


class EndpointRateThrottle(SimpleRateThrottle):
    """Base class for throttles that respect per-endpoint scopes."""

    category_suffix = "generic"

    def __init__(self):
        # ``SimpleRateThrottle`` tries to resolve the rate during ``__init__``
        # which requires the ``scope`` attribute to be set. Our throttles
        # determine the scope dynamically per view, so we defer rate
        # resolution until the request cycle.
        self.history = None
        self.now = None
        self.num_requests = None
        self.duration = None

    def allow_request(self, request, view):  # pragma: no cover - framework hook
        scope = getattr(view, "throttle_scope", None)
        if not scope:
            return True

        self.scope = f"{scope}_{self.category_suffix}"
        rate = self.get_rate()
        # ``SimpleRateThrottle.allow_request`` expects ``self.rate`` to be set.
        # ``get_rate`` defers to the scope we've just constructed, so store the
        # resolved value before delegating to the parent implementation.
        self.rate = rate
        self.num_requests, self.duration = self.parse_rate(rate)

        return super().allow_request(request, view)

    def get_cache_key(self, request, view):  # pragma: no cover - framework hook
        scope = getattr(view, "throttle_scope", None)
        if not scope:
            return None
        ident = self._get_ident(request, view)
        if not ident:
            return None
        self.scope = f"{scope}_{self.category_suffix}"
        return self.cache_format % {"scope": self.scope, "ident": ident}

    def _get_ident(self, request, view) -> str | None:
        raise NotImplementedError


class EndpointIPRateThrottle(EndpointRateThrottle):
    category_suffix = "ip"

    def _get_ident(self, request, view) -> str | None:  # pragma: no cover - simple helper
        return self.get_ident(request)


class EndpointUserRateThrottle(EndpointRateThrottle):
    category_suffix = "user"

    def _get_ident(self, request, view) -> str | None:
        user = getattr(request, "user", None)
        if getattr(user, "is_authenticated", False):
            return f"user:{user.pk}"
        candidate: str | None = None
        data_sources: list[Any] = []
        if hasattr(request, "data"):
            data_sources.append(request.data)
        if hasattr(request, "query_params"):
            data_sources.append(request.query_params)
        for source in data_sources:
            if not source:
                continue
            for key in ("credential", "email", "nickname", "username", "user"):
                value = source.get(key)
                if value:
                    candidate = str(value).lower()
                    break
            if candidate:
                break
        if candidate:
            sanitized = re.sub(r"[^a-z0-9:._-]", "_", candidate)
            return f"anon:{sanitized}"
        return None


__all__ = [
    "EndpointIPRateThrottle",
    "EndpointUserRateThrottle",
]
