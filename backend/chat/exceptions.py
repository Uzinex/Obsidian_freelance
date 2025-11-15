from __future__ import annotations


class ChatRateLimitError(RuntimeError):
    """Raised when a sender exceeds chat rate limits."""


class ChatBlockedError(PermissionError):
    """Raised when a chat or participant is temporarily blocked."""
