from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta

from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.utils import timezone

from chat.exceptions import ChatBlockedError

from .models import (
    ChatMessageFlag,
    ChatMessageReport,
    ChatModerationCase,
    ChatParticipantRestriction,
    ChatRedFlagPattern,
    EscalationDecision,
    StaffActionLog,
)

REPORT_THRESHOLD = 3
SEVERITY_PRIORITY = {
    ChatRedFlagPattern.SEVERITY_LOW: ChatModerationCase.PRIORITY_LOW,
    ChatRedFlagPattern.SEVERITY_MEDIUM: ChatModerationCase.PRIORITY_MEDIUM,
    ChatRedFlagPattern.SEVERITY_HIGH: ChatModerationCase.PRIORITY_HIGH,
}
PRIORITY_SLA_MINUTES = {
    ChatModerationCase.PRIORITY_LOW: 360,
    ChatModerationCase.PRIORITY_MEDIUM: 120,
    ChatModerationCase.PRIORITY_HIGH: 30,
}


@dataclass
class RestrictionState:
    blocked: bool
    shadow_banned: bool
    reason: str = ""


def evaluate_chat_restrictions(*, thread, sender) -> RestrictionState:
    profile = getattr(sender, "profile", None)
    if not profile:
        return RestrictionState(blocked=False, shadow_banned=False)
    restrictions = list(
        ChatParticipantRestriction.objects.active().filter(
            thread=thread,
            profile=profile,
        )
    )
    blocked = False
    reason = ""
    shadow_banned = False
    for restriction in restrictions:
        if restriction.restriction_type == ChatParticipantRestriction.TYPE_SEND_BLOCK:
            blocked = True
            reason = restriction.reason
        elif restriction.restriction_type == ChatParticipantRestriction.TYPE_SHADOW_BAN:
            shadow_banned = True
    return RestrictionState(blocked=blocked, shadow_banned=shadow_banned, reason=reason)


def apply_red_flag_detection(message) -> list[ChatMessageFlag]:
    body = message.body or ""
    if not body:
        return []
    flags: list[ChatMessageFlag] = []
    patterns = ChatRedFlagPattern.objects.filter(is_active=True)
    for pattern in patterns:
        if not pattern.compiled_regex.search(body):
            continue
        flag, _ = ChatMessageFlag.objects.get_or_create(
            message=message,
            category=pattern.category,
            defaults={
                "source": ChatMessageFlag.SOURCE_AUTOMATED,
                "trigger": pattern.label,
            },
        )
        flags.append(flag)
        escalate_case(
            message=message,
            reason=f"Auto-flag: {pattern.label}",
            priority=SEVERITY_PRIORITY.get(pattern.severity, ChatModerationCase.PRIORITY_MEDIUM),
        )
    return flags


def escalate_case(*, message, reason: str, priority: str) -> EscalationDecision:
    defaults = {
        "thread": message.thread,
        "priority": priority,
        "escalation_reason": reason,
        "sla_due_at": timezone.now()
        + timedelta(minutes=PRIORITY_SLA_MINUTES.get(priority, 120)),
    }
    case, created = ChatModerationCase.objects.get_or_create(message=message, defaults=defaults)
    if not created:
        # Refresh metadata for existing cases so SLA reflects the latest severity.
        case.priority = priority
        case.escalation_reason = reason
        case.sla_due_at = defaults["sla_due_at"]
        case.status = ChatMessageFlag.STATUS_IN_REVIEW
        case.save(update_fields=["priority", "escalation_reason", "sla_due_at", "status", "updated_at"])
    log_staff_action(actor=None, target=case, action="case.escalated", payload={"reason": reason, "priority": priority})
    return EscalationDecision(case=case, created=created)


def file_user_report(*, message, reporter, category: str, comment: str = "") -> ChatMessageReport:
    with transaction.atomic():
        report, created = ChatMessageReport.objects.get_or_create(
            message=message,
            reporter=reporter,
            category=category,
            defaults={"comment": comment},
        )
        if not created and comment:
            report.comment = comment
            report.save(update_fields=["comment"])
        total_reports = ChatMessageReport.objects.filter(message=message, category=category).count()
        if total_reports >= REPORT_THRESHOLD:
            ChatMessageFlag.objects.get_or_create(
                message=message,
                category=category,
                defaults={
                    "source": ChatMessageFlag.SOURCE_USER_REPORT,
                    "trigger": f"{total_reports} reports",
                },
            )
            escalate_case(
                message=message,
                reason=f"{total_reports} user reports ({category})",
                priority=ChatModerationCase.PRIORITY_MEDIUM,
            )
    return report


def log_staff_action(*, actor, target, action: str, payload: dict | None = None) -> StaffActionLog:
    if target is None:
        content_type = ContentType.objects.get_for_model(StaffActionLog)
        target_id = 0
    else:
        content_type = ContentType.objects.get_for_model(target)
        target_id = target.pk
    return StaffActionLog.objects.create(
        actor=actor,
        content_type=content_type,
        object_id=target_id,
        action=action,
        payload=payload or {},
    )


def enforce_chat_safety(thread, sender) -> bool:
    """Raise when messaging is blocked and return whether shadow ban is active."""
    state = evaluate_chat_restrictions(thread=thread, sender=sender)
    if state.blocked:
        raise ChatBlockedError(state.reason or "Отправка сообщений недоступна")
    return state.shadow_banned


__all__ = [
    "apply_red_flag_detection",
    "enforce_chat_safety",
    "escalate_case",
    "file_user_report",
    "log_staff_action",
    "RestrictionState",
]
