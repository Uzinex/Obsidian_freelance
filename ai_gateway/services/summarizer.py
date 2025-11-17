"""Heuristic TL;DR generator aligned with tone guidelines."""

from __future__ import annotations

from textwrap import shorten

from ..core.cache import TTLCache


class TldrSummarizer:
    def __init__(self) -> None:
        self._cache = TTLCache(ttl_seconds=60 * 60 * 6)

    def _format(self, title: str, body: str, locale: str) -> str:
        base = f"{title.strip()}: {body.strip()}"
        if locale.startswith("uz"):
            prefix = "Qisqa sharh"
        else:
            prefix = "Кратко"
        return f"{prefix}: {base}"

    def summarize(self, *, title: str, body: str, locale: str) -> str:
        cache_key = f"tldr:{locale}:{hash(title + body)}"
        cached = self._cache.get(cache_key)
        if cached:
            return cached
        normalized = body.replace("\n", " ")
        truncated = shorten(normalized, width=200, placeholder="…")
        summary = self._format(title, truncated, locale)
        self._cache[cache_key] = summary
        return summary
