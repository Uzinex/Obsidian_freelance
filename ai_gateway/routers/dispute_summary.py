from __future__ import annotations

from datetime import datetime
from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter(prefix="/disputes")


class MilestoneInput(BaseModel):
    name: str
    due_date: datetime
    delivered_at: datetime | None = None
    notes: str | None = None


class PaymentInput(BaseModel):
    payment_id: str
    amount: float
    currency: str
    status: str
    paid_at: datetime | None = None


class MessageInput(BaseModel):
    message_id: str
    sender_role: str = Field(pattern=r"^(client|freelancer|system)$")
    timestamp: datetime
    body: str
    attachments: list[str] = Field(default_factory=list)


class FileInput(BaseModel):
    file_id: str
    url: str
    kind: str
    uploaded_at: datetime


class DisputeTriageRequest(BaseModel):
    dispute_id: str
    order_id: str
    promises: list[str] = Field(default_factory=list)
    deliveries: list[str] = Field(default_factory=list)
    milestones: list[MilestoneInput] = Field(default_factory=list)
    payments: list[PaymentInput] = Field(default_factory=list)
    messages: list[MessageInput] = Field(default_factory=list)
    files: list[FileInput] = Field(default_factory=list)
    reported_issue: str | None = None


class TimelineEntry(BaseModel):
    milestone: str
    due_date: datetime
    delivered_at: datetime | None = None
    delta_days: int | None = None
    notes: str | None = None


class PaymentEntry(BaseModel):
    payment_id: str
    amount: float
    currency: str
    status: str
    paid_at: datetime | None = None


class CaseSummary(BaseModel):
    promised_scope: list[str]
    delivered_scope: list[str]
    timeline: list[TimelineEntry]
    payments: list[PaymentEntry]
    category_hint: str
    confidence: float
    checklist: list[str]
    relevant_messages: list[dict[str, Any]]
    relevant_files: list[dict[str, Any]]
    auto_resolution_allowed: bool = False
    logging_flags: list[str]


class DisputeSummaryResponse(BaseModel):
    dispute_id: str
    order_id: str
    summary: CaseSummary


def _timeline(milestones: list[MilestoneInput]) -> list[TimelineEntry]:
    timeline: list[TimelineEntry] = []
    for item in milestones:
        delta_days = None
        if item.delivered_at:
            delta_days = (item.delivered_at.date() - item.due_date.date()).days
        timeline.append(
            TimelineEntry(
                milestone=item.name,
                due_date=item.due_date,
                delivered_at=item.delivered_at,
                delta_days=delta_days,
                notes=item.notes,
            )
        )
    return timeline


def _payments(payments: list[PaymentInput]) -> list[PaymentEntry]:
    return [
        PaymentEntry(
            payment_id=item.payment_id,
            amount=item.amount,
            currency=item.currency,
            status=item.status,
            paid_at=item.paid_at,
        )
        for item in payments
    ]


def _category_hint(request: DisputeTriageRequest) -> tuple[str, float]:
    if not request.deliveries:
        return "non_delivery", 0.85
    overdue = any(m.delivered_at is None and m.due_date < datetime.utcnow() for m in request.milestones)
    if overdue:
        return "late_delivery", 0.7
    quality_claim = request.reported_issue and "quality" in request.reported_issue.lower()
    if quality_claim:
        return "quality_issue", 0.65
    payment_issue = any(payment.status.lower() != "paid" for payment in request.payments)
    if payment_issue:
        return "payment_issue", 0.75
    return "scope_creep", 0.5


def _relevant_messages(messages: list[MessageInput]) -> list[dict[str, Any]]:
    top_messages = sorted(messages, key=lambda m: m.timestamp, reverse=True)[:5]
    return [
        {
            "message_id": msg.message_id,
            "sender_role": msg.sender_role,
            "timestamp": msg.timestamp,
            "summary": msg.body[:200],
            "attachments": msg.attachments,
        }
        for msg in top_messages
    ]


def _relevant_files(files: list[FileInput]) -> list[dict[str, Any]]:
    return [
        {
            "file_id": file.file_id,
            "kind": file.kind,
            "uploaded_at": file.uploaded_at,
            "url": file.url,
        }
        for file in files[:5]
    ]


def _checklist(category: str) -> list[str]:
    base = [
        "Сверить обещанный и фактический объём работ",
        "Проверить соответствующие Terms и политику",
        "Зафиксировать комментарии сторон в карточке спора",
    ]
    if category == "non_delivery":
        base.append("Подтвердить отсутствие файлов и апдейтов на платформе")
    elif category == "late_delivery":
        base.append("Проверить согласованные переносы дедлайнов")
    elif category == "quality_issue":
        base.append("Сопоставить замечания клиента с acceptance criteria")
    elif category == "payment_issue":
        base.append("Сверить статусы escrow и транзакций")
    return base


@router.post("/summary", response_model=DisputeSummaryResponse)
def build_dispute_summary(request: DisputeTriageRequest) -> DisputeSummaryResponse:
    category, confidence = _category_hint(request)
    checklist = _checklist(category)

    summary = CaseSummary(
        promised_scope=request.promises,
        delivered_scope=request.deliveries,
        timeline=_timeline(request.milestones),
        payments=_payments(request.payments),
        category_hint=category,
        confidence=confidence,
        checklist=checklist,
        relevant_messages=_relevant_messages(request.messages),
        relevant_files=_relevant_files(request.files),
        logging_flags=["dispute.summary_generated"],
    )
    if confidence < 0.6:
        summary.logging_flags.append("dispute.low_confidence")

    return DisputeSummaryResponse(
        dispute_id=request.dispute_id,
        order_id=request.order_id,
        summary=summary,
    )
