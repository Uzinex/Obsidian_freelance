from __future__ import annotations

from typing import Any, Mapping, MutableMapping

from .models import Notification, Profile


def create_notification(
    profile: Profile,
    *,
    title: str,
    message: str,
    category: str = Notification.CATEGORY_GENERAL,
    data: Mapping[str, Any] | None = None,
) -> Notification:
    """Helper to create and persist notifications in a consistent way."""

    payload: MutableMapping[str, Any] = {"profile": profile, "title": title, "message": message}
    if category:
        payload["category"] = category
    if data:
        payload["data"] = dict(data)
    return Notification.objects.create(**payload)
