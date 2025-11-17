"""Семантический поиск по заказам, профилям и портфолио."""

from __future__ import annotations

import math
from typing import Iterable

from ..core.cache import TTLCache

_SYNONYMS = {
    "dizayn": "design",
    "dizayner": "design",
    "ishlab chiqish": "development",
    "mobil": "mobile",
    "veb": "web",
}


class SemanticSearchService:
    def __init__(self) -> None:
        self._cache = TTLCache(ttl_seconds=3600)

    @staticmethod
    def _normalize(text: str) -> list[str]:
        lowered = text.lower()
        for src, target in _SYNONYMS.items():
            lowered = lowered.replace(src, target)
        tokens = lowered.replace("'", " ").split()
        return [token.strip() for token in tokens if token.strip()]

    @staticmethod
    def _vectorize(tokens: Iterable[str], dim: int = 64) -> list[float]:
        vector = [0.0] * dim
        for token in tokens:
            idx = hash(token) % dim
            vector[idx] += 1.0
        norm = math.sqrt(sum(x * x for x in vector)) or 1.0
        return [x / norm for x in vector]

    def _embedding(self, text: str) -> list[float]:
        cache_key = f"emb:{hash(text)}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached
        tokens = self._normalize(text)
        vector = self._vectorize(tokens)
        self._cache[cache_key] = vector
        return vector

    @staticmethod
    def _cosine(a: list[float], b: list[float]) -> float:
        return sum(x * y for x, y in zip(a, b))

    def search(self, *, query: str, documents: list[dict], limit: int) -> dict:
        q_vector = self._embedding(query)
        ranked: list[tuple[float, dict]] = []
        for document in documents:
            doc_text = " ".join(
                filter(
                    None,
                    [
                        document.get("title"),
                        document.get("tldr"),
                        document.get("body"),
                    ],
                )
            )
            vector = self._embedding(doc_text)
            score = self._cosine(q_vector, vector)
            ranked.append((score, document))
        ranked.sort(key=lambda item: item[0], reverse=True)
        results = [
            {
                "id": doc.get("id"),
                "score": round(score, 4),
                "snippet": (doc.get("tldr") or doc.get("body", ""))[:280],
            }
            for score, doc in ranked[:limit]
        ]
        fallback_needed = not results or results[0]["score"] < 0.1
        return {"results": results, "fallback_triggered": fallback_needed}
