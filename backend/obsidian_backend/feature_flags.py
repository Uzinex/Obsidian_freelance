"""Feature flags for communications and notifications.

The module follows the same ENV-driven approach as the JWT feature flags
introduced on Stage 1: boolean environment variables are parsed once at
import time and exposed both as a mapping and helper function.
"""
from __future__ import annotations

import os
from typing import Mapping

__all__ = ["FEATURE_FLAGS", "is_feature_enabled"]


def _get_bool_env(var_name: str, default: bool = False) -> bool:
    value = os.getenv(var_name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


FEATURE_FLAGS: Mapping[str, bool] = {
    "chat.enabled": _get_bool_env("FEATURE_CHAT_ENABLED", default=True),
    "chat.attachments": _get_bool_env("FEATURE_CHAT_ATTACHMENTS", default=True),
    "chat.presence": _get_bool_env("FEATURE_CHAT_PRESENCE", default=False),
    "dispute.enabled": _get_bool_env("FEATURE_DISPUTE_ENABLED", default=False),
    "notify.email": _get_bool_env("FEATURE_NOTIFY_EMAIL", default=True),
    "notify.webpush": _get_bool_env("FEATURE_NOTIFY_WEBPUSH", default=False),
}


def is_feature_enabled(flag_name: str, *, default: bool = False) -> bool:
    """Return the resolved value for the requested feature flag."""

    return bool(FEATURE_FLAGS.get(flag_name, default))
