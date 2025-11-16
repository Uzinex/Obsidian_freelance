from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from .copy import get_webpush_template
from .formatting import enrich_context, normalize_locale


@dataclass
class WebPushPayload:
    title: str
    body: str
    url: str | None = None


def render_webpush_payload(
    event_type: str,
    data: Mapping,
    *,
    locale: str | None = None,
) -> WebPushPayload:
    normalized = normalize_locale(locale or data.get('locale'))
    template = get_webpush_template(event_type, normalized)
    context = enrich_context(data, locale=normalized)
    if template:
        title = template.get('title', context.get('title', 'Obsidian'))
        body = template.get('body', context.get('body', ''))
    else:
        title = context.get('title', 'Obsidian')
        body = context.get('body', '')
    return WebPushPayload(title=title.format(**context), body=body.format(**context), url=context.get('url'))
