from __future__ import annotations

import hashlib
import secrets
from dataclasses import dataclass
from datetime import timedelta

from django.conf import settings
from django.utils import timezone


@dataclass
class OTPPayload:
    code: str
    salt: str
    hash: str
    expires_at: "timezone.datetime"


def _pepper() -> str:
    value = getattr(settings, "ACCOUNTS_OTP_PEPPER", None)
    if value:
        return value
    return settings.SECRET_KEY


def hash_otp(*, code: str, salt: str) -> str:
    payload = f"{salt}:{code}:{_pepper()}".encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def generate_otp(*, ttl_seconds: int | None = None) -> OTPPayload:
    length = 6
    code = f"{secrets.randbelow(10**length):0{length}d}"
    salt = secrets.token_hex(8)
    ttl = ttl_seconds or getattr(settings, "ACCOUNTS_OTP_TTL_SECONDS", 600)
    expires_at = timezone.now() + timedelta(seconds=ttl)
    return OTPPayload(
        code=code,
        salt=salt,
        hash=hash_otp(code=code, salt=salt),
        expires_at=expires_at,
    )


def verify_otp(*, code: str, salt: str, expected_hash: str) -> bool:
    if not code or not salt or not expected_hash:
        return False
    return hash_otp(code=code, salt=salt) == expected_hash
