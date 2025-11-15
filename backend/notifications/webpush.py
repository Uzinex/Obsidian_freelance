from __future__ import annotations

from dataclasses import dataclass


@dataclass
class WebPushPayload:
    title: str
    body: str
    url: str | None = None


def render_webpush_payload(title: str, body: str, data: dict) -> WebPushPayload:
    return WebPushPayload(title=title, body=body, url=data.get("url"))
