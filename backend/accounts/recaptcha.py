from __future__ import annotations

from dataclasses import dataclass
from dataclasses import dataclass
from typing import Any

import httpx
from django.conf import settings


class RecaptchaVerificationError(Exception):
    """Raised when Google reCAPTCHA validation fails."""


@dataclass
class RecaptchaResult:
    success: bool
    score: float | None = None
    action: str | None = None
    raw: dict[str, Any] | None = None


_VERIFY_ENDPOINT = "https://www.google.com/recaptcha/api/siteverify"


def verify_recaptcha(*, token: str, remote_ip: str | None = None) -> RecaptchaResult:
    secret = getattr(settings, "RECAPTCHA_SECRET_KEY", "")
    if not secret:
        # Development environments might not provide a secret. We treat the
        # challenge as successful to avoid blocking local testers.
        return RecaptchaResult(success=True, score=1.0, action="dev-bypass")
    if not token:
        raise RecaptchaVerificationError("Captcha token is required")
    payload = {"secret": secret, "response": token}
    if remote_ip:
        payload["remoteip"] = remote_ip
    try:
        response = httpx.post(_VERIFY_ENDPOINT, data=payload, timeout=5.0)
        response.raise_for_status()
    except httpx.HTTPError as exc:  # pragma: no cover - network failures are rare
        raise RecaptchaVerificationError("Captcha verification unavailable") from exc
    data = response.json()
    success = bool(data.get("success"))
    score = data.get("score")
    action = data.get("action")
    min_score = getattr(settings, "RECAPTCHA_MIN_SCORE", 0.7)
    if not success or (score is not None and score < min_score):
        raise RecaptchaVerificationError("Captcha verification failed")
    return RecaptchaResult(success=True, score=score, action=action, raw=data)
