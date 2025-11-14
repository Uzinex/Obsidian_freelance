from __future__ import annotations

import math
from typing import Optional

from django.core.cache import cache

from obsidian_backend import jwt_settings as jwt_conf

_FAILURE_CACHE_KEY = "auth:login_failures:{ident}"
_CAPTCHA_FEATURE_FLAG = "auth.login_captcha"


def _cache_key(ident: str) -> str:
    return _FAILURE_CACHE_KEY.format(ident=ident)


def register_login_failure(*, identifier: str, max_delay: int = 30) -> int:
    """Record a failed login attempt and return the required delay in seconds."""

    key = _cache_key(identifier)
    count = cache.get(key, 0) + 1
    cache.set(key, count, timeout=3600)
    delay = min(max_delay, int(math.pow(2, max(0, count - 1))))
    return delay


def reset_login_failures(*, identifier: str) -> None:
    cache.delete(_cache_key(identifier))


def captcha_required() -> bool:
    return jwt_conf.FEATURE_FLAGS.get(_CAPTCHA_FEATURE_FLAG, False)


def captcha_hook(payload: Optional[dict] = None) -> None:
    """Integration hook for CAPTCHA providers."""

    if not captcha_required():
        return
    # Placeholder for CAPTCHA verification; integration should be provided by ops team.
    # Raise an exception to block authentication if verification fails.
    raise RuntimeError("CAPTCHA verification required but not implemented")
