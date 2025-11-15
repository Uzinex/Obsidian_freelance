from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo

from django.utils import timezone

from accounts.utils import create_notification
from chat.models import ChatThread
from disputes.models import DisputeCase
from marketplace.models import Contract
from notifications.models import NotificationEvent, SlaActionLog
from notifications.services import notification_hub

WORK_TZ = ZoneInfo("Asia/Tashkent")
WORK_START = time(9, 0)
WORK_END = time(18, 0)

CHAT_RESPONSE_THRESHOLD = timedelta(hours=4)
DISPUTE_ESCALATION_THRESHOLD = timedelta(hours=12)
CLIENT_SILENCE_THRESHOLD = timedelta(days=5)


@dataclass
class SlaResult:
    reminders: int
    escalations: int
    auto_releases: int


def process_sla_timers(*, now: datetime | None = None) -> SlaResult:
    now = now or timezone.now()
    reminders = _send_chat_response_reminders(now)
    escalations = _escalate_overdue_disputes(now)
    auto_releases = _auto_release_silent_contracts(now)
    notification_hub.flush_due_digests(now=now)
    notification_hub.dispatch_pending_deliveries()
    return SlaResult(reminders=reminders, escalations=escalations, auto_releases=auto_releases)


def _within_working_hours(dt: datetime) -> bool:
    local = dt.astimezone(WORK_TZ)
    current = local.time()
    if WORK_START <= WORK_END:
        return WORK_START <= current <= WORK_END
    return current >= WORK_START or current <= WORK_END


def _send_chat_response_reminders(now: datetime) -> int:
    if not _within_working_hours(now):
        return 0
    threshold = now - CHAT_RESPONSE_THRESHOLD
    threads = (
        ChatThread.objects.filter(last_message_at__lte=threshold)
        .select_related(
            "client",
            "client__user",
            "freelancer",
            "freelancer__user",
        )
        .order_by("-last_message_at")
    )
    sent = 0
    for thread in threads:
        last_message = thread.messages.order_by("-sent_at").first()
        if not last_message:
            continue
        recipient = None
        if last_message.sender_id == thread.client.user_id:
            recipient = thread.freelancer.user
            actor = thread.client.user
        else:
            recipient = thread.client.user
            actor = thread.freelancer.user
        if not recipient:
            continue
        if SlaActionLog.objects.filter(
            rule_code="chat.response",
            chat_thread=thread,
            metadata__message_id=last_message.id,
        ).exists():
            continue
        notification_hub.emit(
            recipient=recipient,
            actor=actor,
            profile=getattr(recipient, "profile", None),
            title="Нет ответа в чате",
            body="Ответьте на последнее сообщение, чтобы не нарушить SLA.",
            category=NotificationEvent.CATEGORY_CHAT,
            event_type=NotificationEvent.EventType.CHAT_NEW_MESSAGE,
            data={
                "thread_id": thread.id,
                "contract_id": thread.contract_id,
                "last_message_id": last_message.id,
            },
        )
        SlaActionLog.objects.create(
            rule_code="chat.response",
            chat_thread=thread,
            metadata={"message_id": last_message.id},
        )
        sent += 1
    return sent


def _escalate_overdue_disputes(now: datetime) -> int:
    overdue = DisputeCase.objects.filter(
        sla_due_at__lte=now - DISPUTE_ESCALATION_THRESHOLD,
        status__in=[
            DisputeCase.STATUS_OPENED,
            DisputeCase.STATUS_EVIDENCE,
            DisputeCase.STATUS_IN_REVIEW,
        ],
    ).select_related("contract", "contract__client__user")
    escalated = 0
    for case in overdue:
        if SlaActionLog.objects.filter(rule_code="dispute.escalation", dispute=case).exists():
            continue
        case.priority = DisputeCase.PRIORITY_HIGH
        case.save(update_fields=["priority"])
        recipient = case.contract.client.user
        notification_hub.emit(
            recipient=recipient,
            title="Эскалация спора",
            body=f"Спор по контракту #{case.contract_id} эскалирован к лид-модератору.",
            category=NotificationEvent.CATEGORY_CONTRACT,
            event_type=NotificationEvent.EventType.CONTRACT_DISPUTE_OPENED,
            data={"case_id": case.id, "contract_id": case.contract_id},
        )
        SlaActionLog.objects.create(
            rule_code="dispute.escalation",
            dispute=case,
            metadata={"case_id": case.id},
        )
        escalated += 1
    return escalated


def _auto_release_silent_contracts(now: datetime) -> int:
    cutoff = now - CLIENT_SILENCE_THRESHOLD
    contracts = Contract.objects.filter(
        status=Contract.STATUS_ACTIVE,
        updated_at__lte=cutoff,
        escrow_release_frozen=False,
    ).select_related("client__user", "freelancer__user")
    released = 0
    for contract in contracts:
        if SlaActionLog.objects.filter(rule_code="contract.auto_release", contract=contract).exists():
            continue
        try:
            contract.complete()
        except ValueError:
            continue
        create_notification(
            contract.freelancer,
            title="Автовыплата",
            message=f"Контракт '{contract.order.title}' автоматически закрыт из-за отсутствия ответа заказчика.",
            category=NotificationEvent.CATEGORY_PAYMENTS,
            event_type=NotificationEvent.EventType.PAYMENTS_PAYOUT,
            data={"contract_id": contract.id},
        )
        create_notification(
            contract.client,
            title="Контракт закрыт автоматически",
            message=f"Контракт '{contract.order.title}' закрыт после {CLIENT_SILENCE_THRESHOLD.days} дней тишины.",
            category=NotificationEvent.CATEGORY_CONTRACT,
            event_type=NotificationEvent.EventType.CONTRACT_COMPLETED,
            data={"contract_id": contract.id},
        )
        SlaActionLog.objects.create(
            rule_code="contract.auto_release",
            contract=contract,
            metadata={"threshold_days": CLIENT_SILENCE_THRESHOLD.days},
        )
        released += 1
    return released
