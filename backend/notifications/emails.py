from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

EMAIL_TEMPLATES: dict[str, dict[str, str]] = {
    "contract.created": {
        "subject": "Новый контракт создан",
        "body": "Контракт {contract_id} создан и ожидает подписи.",
    },
    "contract.signed": {
        "subject": "Контракт подписан",
        "body": "Контракт {contract_id} подписан обеими сторонами.",
    },
    "contract.dispute_opened": {
        "subject": "Открыт спор",
        "body": "По контракту {contract_id} открыт спор №{case_id}.",
    },
    "payments.payout": {
        "subject": "Перевод выполнен",
        "body": "Выплата {amount} {currency} отправлена.",
    },
    "account.login": {
        "subject": "Новый вход",
        "body": "В ваш аккаунт выполнен вход из {location}.",
    },
}


@dataclass
class EmailPayload:
    subject: str
    body: str
    recipient: str


def render_transactional_email(event_type: str, data: Mapping) -> EmailPayload:
    template = EMAIL_TEMPLATES.get(event_type) or {
        "subject": "Уведомление Obsidian",
        "body": "{title}\n\n{body}",
    }
    subject = template["subject"].format(**data)
    body = template["body"].format(**data)
    return EmailPayload(subject=subject, body=body, recipient=data.get("email", ""))
