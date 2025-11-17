"""Utilities for removing personally identifiable information from texts."""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable, Pattern

_REPLACEMENT = "[redacted]"

_PHONE_PATTERN = re.compile(
    r"(?:(?:\+?998|\+?7|8)\s?[\(\-]?\s?\d{2,3}[\)\-]?\s?\d{3}[\s\-]?\d{2}[\s\-]?\d{2})"
)
_EMAIL_PATTERN = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
_HANDLE_PATTERN = re.compile(
    r"(?:@|(?:telegram|whatsapp|tg|wa)[:]?\s?)([A-Za-z0-9_]{3,})",
    flags=re.IGNORECASE,
)
_URL_PATTERN = re.compile(r"https?://[^\s]+|www\.[^\s]+")


@dataclass
class _ScrubRule:
    pattern: Pattern[str]
    replacement: str = _REPLACEMENT

    def apply(self, text: str) -> str:
        return self.pattern.sub(self.replacement, text)


_SCRUB_RULES: tuple[_ScrubRule, ...] = (
    _ScrubRule(_PHONE_PATTERN),
    _ScrubRule(_EMAIL_PATTERN),
    _ScrubRule(_HANDLE_PATTERN, replacement="@hidden"),
    _ScrubRule(_URL_PATTERN),
)


def scrub_text(text: str, *, extra_rules: Iterable[_ScrubRule] | None = None) -> str:
    """Remove PII markers from the supplied text."""

    cleaned = text
    rules: tuple[_ScrubRule, ...]
    if extra_rules:
        rules = (*_SCRUB_RULES, *tuple(extra_rules))
    else:
        rules = _SCRUB_RULES

    for rule in rules:
        cleaned = rule.apply(cleaned)
    return cleaned


__all__ = ["scrub_text", "_ScrubRule"]
