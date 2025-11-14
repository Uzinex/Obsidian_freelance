from __future__ import annotations

import secrets
from datetime import timedelta
from typing import Dict

from django.core import signing
from django.utils import timezone

from .models import OneTimeToken, generate_token_hash


def create_one_time_token(*, user, purpose: str, payload: Dict | None = None, lifetime_seconds: int = 900, metadata: Dict | None = None) -> str:
    raw_token = secrets.token_urlsafe(32)
    signed = signing.dumps(
        {"token": raw_token, "purpose": purpose, "user": str(user.pk), "payload": payload or {}},
        salt=f"accounts:{purpose}",
    )
    OneTimeToken.objects.filter(user=user, purpose=purpose, used_at__isnull=True).delete()
    OneTimeToken.objects.create(
        user=user,
        purpose=purpose,
        token_hash=generate_token_hash(raw_token),
        payload=payload or {},
        expires_at=timezone.now() + timedelta(seconds=lifetime_seconds),
        request_metadata=metadata or {},
    )
    return signed


def consume_one_time_token(*, token: str, purpose: str) -> OneTimeToken:
    try:
        payload = signing.loads(token, salt=f"accounts:{purpose}")
    except signing.BadSignature as exc:
        raise ValueError("Invalid token signature") from exc
    raw_token = payload.get("token")
    if not raw_token:
        raise ValueError("Malformed token payload")
    token_hash = generate_token_hash(raw_token)
    try:
        record = OneTimeToken.objects.select_for_update().get(
            purpose=purpose,
            token_hash=token_hash,
        )
    except OneTimeToken.DoesNotExist as exc:
        raise ValueError("Token not found or already used") from exc
    if not record.is_valid:
        raise ValueError("Token expired or already used")
    record.mark_used()
    return record
