from __future__ import annotations

import re
from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter(prefix="/scam-filter")

TELEGRAM_RE = re.compile(r"(?:t\.me|@\w{4,}|telegram)", re.IGNORECASE)
WHATSAPP_RE = re.compile(r"(?:wa\.me|whatsapp|\+?\d{9,})", re.IGNORECASE)
OFF_PLATFORM_PAYMENT_RE = re.compile(r"(без\s+эскроу|перевод\s+на\s+карту|оплата\s+напрямую)", re.IGNORECASE)
CRYPTO_SCAM_RE = re.compile(r"(usdt|airdrop|double profit|staking|без\s+риска)", re.IGNORECASE)
SUSPICIOUS_LINK_RE = re.compile(r"(bit\.ly|tinyurl|crypto|token)", re.IGNORECASE)


class Attachment(BaseModel):
    type: str
    value: str


class ScamFilterRequest(BaseModel):
    content_id: str
    content_type: str = Field(pattern=r"^(chat|post|file)$")
    text: str
    attachments: list[Attachment] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class DetectedSignal(BaseModel):
    type: str
    weight: float
    snippet: str


class ScamFilterResponse(BaseModel):
    content_id: str
    risk_score: float
    labels: list[str]
    detected_signals: list[DetectedSignal]
    recommended_action: str
    escalate_to_moderation: bool
    user_warning: str | None = None
    logging_flags: list[str]


def _add_signal(signals: list[DetectedSignal], signal_type: str, weight: float, snippet: str) -> None:
    signals.append(DetectedSignal(type=signal_type, weight=weight, snippet=snippet[:120]))


def _collect_signals(request: ScamFilterRequest) -> list[DetectedSignal]:
    signals: list[DetectedSignal] = []
    text = request.text
    if TELEGRAM_RE.search(text):
        _add_signal(signals, "off_platform_contact", 0.4, TELEGRAM_RE.search(text).group())
    if WHATSAPP_RE.search(text):
        _add_signal(signals, "off_platform_contact", 0.35, WHATSAPP_RE.search(text).group())
    if OFF_PLATFORM_PAYMENT_RE.search(text):
        _add_signal(signals, "off_platform_payment", 0.35, OFF_PLATFORM_PAYMENT_RE.search(text).group())
    if CRYPTO_SCAM_RE.search(text):
        _add_signal(signals, "crypto_scam", 0.45, CRYPTO_SCAM_RE.search(text).group())
    if SUSPICIOUS_LINK_RE.search(text):
        _add_signal(signals, "suspicious_link", 0.3, SUSPICIOUS_LINK_RE.search(text).group())

    for attachment in request.attachments:
        if attachment.type == "link" and SUSPICIOUS_LINK_RE.search(attachment.value):
            _add_signal(signals, "suspicious_link", 0.3, attachment.value)

    duplicate_count = int(request.metadata.get("duplicate_count", 0))
    if duplicate_count >= 5:
        _add_signal(signals, "spam_duplicate", 0.2, f"duplicates:{duplicate_count}")

    author_trust = float(request.metadata.get("author_trust", 1.0))
    if author_trust < 0.2:
        _add_signal(signals, "low_trust_author", 0.15, str(author_trust))

    return signals


def _score(signals: list[DetectedSignal]) -> float:
    raw = sum(signal.weight for signal in signals)
    return min(1.0, round(raw, 2))


def _labels(signals: list[DetectedSignal]) -> list[str]:
    label_map = {
        "off_platform_contact": "policy",
        "off_platform_payment": "scam",
        "crypto_scam": "scam",
        "suspicious_link": "spam",
        "spam_duplicate": "spam",
    }
    labels = {label_map.get(signal.type, "policy") for signal in signals}
    return sorted(labels)


def _action_for_score(score: float) -> tuple[str, bool, str | None]:
    if score >= 0.85:
        return "auto_hide", True, "Контент скрыт и отправлен модераторам"
    if score >= 0.6:
        return "hold_for_moderation", True, "Контент отправлен на проверку модератору"
    if score >= 0.3:
        return "soft_warning", False, "Пожалуйста, не используйте контакты вне платформы"
    return "allow", False, None


@router.post("/score", response_model=ScamFilterResponse)
def score_content(request: ScamFilterRequest) -> ScamFilterResponse:
    signals = _collect_signals(request)
    risk_score = _score(signals)
    action, escalate, warning = _action_for_score(risk_score)
    logging_flags = ["scam_filter.scored"]
    if action in {"auto_hide", "hold_for_moderation"}:
        logging_flags.append("scam_filter.high_risk")

    return ScamFilterResponse(
        content_id=request.content_id,
        risk_score=risk_score,
        labels=_labels(signals) if signals else ["safe"],
        detected_signals=signals,
        recommended_action=action,
        escalate_to_moderation=escalate,
        user_warning=warning,
        logging_flags=logging_flags,
    )
