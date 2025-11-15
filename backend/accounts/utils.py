from __future__ import annotations

from typing import Any, Mapping, Sequence

from notifications.models import NotificationEvent
from notifications.services import notification_hub

from .models import Profile


def create_notification(
    profile: Profile,
    *,
    title: str,
    message: str,
    category: str = NotificationEvent.CATEGORY_ACCOUNT,
    event_type: str = NotificationEvent.EventType.ACCOUNT_GENERIC,
    data: Mapping[str, Any] | None = None,
    channels: Sequence[str] | None = None,
) -> NotificationEvent:
    """Bridge helper that proxies legacy calls to the notification hub."""

    emitted = notification_hub.emit(
        recipient=profile.user,
        profile=profile,
        title=title,
        body=message,
        category=category,
        event_type=event_type,
        data=data or {},
        channels=channels,
    )
    return emitted.event
