"""Утилиты для хранения TL;DR в кеше и моделях."""

from __future__ import annotations

from typing import Callable

from django.core.cache import cache

_CACHE_KEY = "ai:tldr:{entity}:{pk}:{locale}"
_CACHE_TTL = 60 * 60 * 6  # 6 часов — достаточно для списков


def _build_key(entity: str, pk: int | str, locale: str) -> str:
    return _CACHE_KEY.format(entity=entity, pk=pk, locale=locale.lower())


def get_tldr(
    *,
    entity: str,
    pk: int | str,
    locale: str,
    fetcher: Callable[[str], str | None],
) -> str | None:
    """Получить TL;DR из кэша либо из модели."""

    key = _build_key(entity, pk, locale)
    cached = cache.get(key)
    if cached is not None:
        return cached
    value = fetcher(locale)
    if value:
        cache.set(key, value, _CACHE_TTL)
    return value


def set_tldr(*, entity: str, pk: int | str, locale: str, value: str) -> None:
    """Обновить кеш после записи в базу."""

    key = _build_key(entity, pk, locale)
    cache.set(key, value, _CACHE_TTL)
