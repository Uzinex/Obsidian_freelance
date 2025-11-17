"""Utilities for writing audit log events."""
from __future__ import annotations

from typing import Any, Mapping, MutableMapping, Tuple

from django.http import HttpRequest

from .models import AuditEvent, AuthSession, User


def _get_client_ip(request: HttpRequest) -> str | None:
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded:
        candidate = forwarded.split(",")[0].strip()
        if candidate:
            return candidate
    remote = request.META.get("REMOTE_ADDR", "").strip()
    return remote or None


def _extract_trace_context(request: HttpRequest | None) -> Tuple[str, str]:
    if request is None:
        return "", ""
    meta = request.META
    trace_id = ""
    span_id = ""
    sentry_trace = meta.get("HTTP_SENTRY_TRACE", "").strip()
    if sentry_trace:
        parts = sentry_trace.split("-")
        if len(parts) >= 2:
            trace_id = parts[0]
            span_id = parts[1]
    if not trace_id:
        traceparent = meta.get("HTTP_TRACEPARENT", "").strip()
        if traceparent:
            parts = traceparent.split("-")
            if len(parts) >= 3:
                trace_id = parts[1]
                span_id = parts[2]
    if not trace_id:
        trace_id = meta.get("HTTP_X_TRACE_ID", meta.get("HTTP_X_REQUEST_ID", "")).strip()
    if not span_id:
        span_id = meta.get("HTTP_X_SPAN_ID", "").strip()
    return trace_id, span_id

SENSITIVE_KEYWORDS = {
    "email",
    "phone",
    "card",
    "iban",
    "passport",
    "ssn",
    "tax",
    "document",
    "account",
    "address",
    "full_name",
}


def _is_sensitive_key(key: str) -> bool:
    lowered = key.lower()
    return any(token in lowered for token in SENSITIVE_KEYWORDS)


def _sanitize_value(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {k: _sanitize_value(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_sanitize_value(item) for item in value]
    if isinstance(value, str) and len(value) > 256:
        return f"{value[:253]}..."
    return value


def _sanitize_metadata(payload: MutableMapping[str, Any]) -> MutableMapping[str, Any]:
    sanitized: MutableMapping[str, Any] = {}
    for key, value in payload.items():
        if _is_sensitive_key(key):
            sanitized[key] = "[REDACTED]"
            continue
        sanitized[key] = _sanitize_value(value)
    return sanitized


class AuditLogger:
    """Collect contextual information and persist audit events."""

    def log_event(
        self,
        *,
        event_type: str,
        user: User | None = None,
        request: HttpRequest | None = None,
        session: AuthSession | None = None,
        metadata: Mapping[str, Any] | None = None,
        status_code: int | None = None,
        device_id: str | None = None,
    ) -> AuditEvent:
        metadata_payload: MutableMapping[str, Any]
        if metadata:
            metadata_payload = dict(metadata)
        else:
            metadata_payload = {}
        ip_address = None
        user_agent = ""
        if request is not None:
            ip_address = _get_client_ip(request)
            user_agent = request.META.get("HTTP_USER_AGENT", "")
            metadata_payload.setdefault("path", request.path)
            metadata_payload.setdefault("method", request.method)
            if session is None:
                session = getattr(request, "auth_session", None)
        if session is not None and not device_id:
            device_id = getattr(session, "device_id", "")
        trace_id, span_id = _extract_trace_context(request)
        actor = None
        if user is not None:
            if getattr(user, "is_authenticated", False):
                actor = user
            else:  # pragma: no cover - defensive fallback
                actor = None
        metadata_payload = _sanitize_metadata(metadata_payload)
        return AuditEvent.objects.create(
            user=actor,
            session=session,
            device_id=device_id or "",
            event_type=event_type,
            ip_address=ip_address,
            user_agent=user_agent,
            metadata=metadata_payload,
            trace_id=trace_id,
            span_id=span_id,
            status_code=status_code,
        )


audit_logger = AuditLogger()

__all__ = ["audit_logger"]
