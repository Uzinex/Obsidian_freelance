from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Mapping

from .copy import DEFAULT_LIST_ID, DEFAULT_LIST_UNSUBSCRIBE, get_email_template
from .formatting import enrich_context, normalize_locale

logger = logging.getLogger(__name__)

DEFAULT_TEMPLATE = {
    'subject': 'Уведомление Obsidian',
    'body': '{title}\n\n{body}',
}


@dataclass
class EmailPayload:
    subject: str
    body: str
    recipient: str
    headers: dict[str, str]


def _build_headers(meta: Mapping[str, str] | None) -> dict[str, str]:
    meta = meta or {}
    headers = {
        'List-Unsubscribe': meta.get('list_unsubscribe', DEFAULT_LIST_UNSUBSCRIBE),
        'List-Unsubscribe-Post': 'List-Unsubscribe=One-Click',
        'List-ID': meta.get('list_id', DEFAULT_LIST_ID),
    }
    category = meta.get('category', 'transactional')
    headers['Precedence'] = 'bulk' if category == 'digest' else 'list'
    headers.update(meta.get('headers', {}))
    return headers


def render_transactional_email(
    event_type: str,
    data: Mapping,
    *,
    locale: str | None = None,
) -> EmailPayload:
    normalized = normalize_locale(locale or data.get('locale'))
    template, meta = get_email_template(event_type, normalized)
    if not template:
        logger.warning('missing email template for %s', event_type)
        template = DEFAULT_TEMPLATE
    context = enrich_context(data, locale=normalized)
    subject = template.get('subject', DEFAULT_TEMPLATE['subject']).format(**context)
    body = template.get('body', DEFAULT_TEMPLATE['body']).format(**context)
    headers = _build_headers(meta)
    return EmailPayload(subject=subject, body=body, recipient=context.get('email', ''), headers=headers)
