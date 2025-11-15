from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Optional

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils import timezone


class ChatRedFlagPattern(models.Model):
    CATEGORY_FRAUD = "fraud"
    CATEGORY_PAYMENT = "banned_payment"
    CATEGORY_ABUSE = "abuse"
    CATEGORY_SPAM = "spam"

    CATEGORY_CHOICES = [
        (CATEGORY_FRAUD, "Fraud / social engineering"),
        (CATEGORY_PAYMENT, "Banned payment details"),
        (CATEGORY_ABUSE, "Harassment or hate speech"),
        (CATEGORY_SPAM, "Spam or off-platform solicitation"),
    ]

    SEVERITY_LOW = "low"
    SEVERITY_MEDIUM = "medium"
    SEVERITY_HIGH = "high"
    SEVERITY_CHOICES = [
        (SEVERITY_LOW, "Low"),
        (SEVERITY_MEDIUM, "Medium"),
        (SEVERITY_HIGH, "High"),
    ]

    code = models.CharField(max_length=64, unique=True)
    label = models.CharField(max_length=128)
    category = models.CharField(max_length=32, choices=CATEGORY_CHOICES)
    pattern = models.CharField(
        max_length=255,
        help_text="Python regular expression that matches the dangerous phrase",
    )
    description = models.TextField(blank=True)
    severity = models.CharField(max_length=16, choices=SEVERITY_CHOICES)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["code"]

    def __str__(self) -> str:  # pragma: no cover - debug helper
        return f"ChatRedFlagPattern<{self.code}>"

    @property
    def compiled_regex(self):
        if not hasattr(self, "_compiled_regex"):
            self._compiled_regex = re.compile(self.pattern, re.IGNORECASE)
        return self._compiled_regex


class ChatParticipantRestrictionQuerySet(models.QuerySet):
    def active(self):
        now = timezone.now()
        return self.filter(models.Q(expires_at__isnull=True) | models.Q(expires_at__gt=now))


class ChatParticipantRestriction(models.Model):
    TYPE_SEND_BLOCK = "send_block"
    TYPE_SHADOW_BAN = "shadow_ban"

    TYPE_CHOICES = [
        (TYPE_SEND_BLOCK, "Messaging blocked"),
        (TYPE_SHADOW_BAN, "Shadow ban"),
    ]

    thread = models.ForeignKey(
        "chat.ChatThread",
        on_delete=models.CASCADE,
        related_name="participant_restrictions",
    )
    profile = models.ForeignKey(
        "accounts.Profile",
        on_delete=models.CASCADE,
        related_name="chat_restrictions",
    )
    restriction_type = models.CharField(max_length=32, choices=TYPE_CHOICES)
    reason = models.CharField(max_length=255)
    applied_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="applied_chat_restrictions",
        null=True,
        blank=True,
    )
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = ChatParticipantRestrictionQuerySet.as_manager()

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["thread", "profile", "restriction_type"]),
        ]

    def __str__(self) -> str:  # pragma: no cover - debug helper
        return f"Restriction<{self.profile_id}:{self.restriction_type}>"

    @property
    def is_active(self) -> bool:
        if self.expires_at is None:
            return True
        return self.expires_at > timezone.now()


class ChatMessageFlag(models.Model):
    CATEGORY_CHOICES = ChatRedFlagPattern.CATEGORY_CHOICES
    SOURCE_AUTOMATED = "automated"
    SOURCE_USER_REPORT = "user_report"
    SOURCE_STAFF = "staff"

    SOURCE_CHOICES = [
        (SOURCE_AUTOMATED, "Automated"),
        (SOURCE_USER_REPORT, "User reports"),
        (SOURCE_STAFF, "Staff"),
    ]

    STATUS_OPEN = "open"
    STATUS_IN_REVIEW = "in_review"
    STATUS_RESOLVED = "resolved"

    STATUS_CHOICES = [
        (STATUS_OPEN, "Open"),
        (STATUS_IN_REVIEW, "In review"),
        (STATUS_RESOLVED, "Resolved"),
    ]

    message = models.ForeignKey(
        "chat.ChatMessage",
        on_delete=models.CASCADE,
        related_name="moderation_flags",
    )
    category = models.CharField(max_length=32, choices=ChatRedFlagPattern.CATEGORY_CHOICES)
    source = models.CharField(max_length=16, choices=SOURCE_CHOICES)
    trigger = models.CharField(max_length=255, blank=True)
    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="chat_flags",
    )
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=STATUS_OPEN)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="resolved_chat_flags",
    )
    resolution_notes = models.TextField(blank=True)

    class Meta:
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=["category", "status"]),
            models.Index(fields=["message"]),
        ]

    def __str__(self) -> str:  # pragma: no cover - debug helper
        return f"ChatMessageFlag<{self.id}:{self.category}>"


class ChatMessageReport(models.Model):
    CATEGORY_CHOICES = ChatRedFlagPattern.CATEGORY_CHOICES

    message = models.ForeignKey(
        "chat.ChatMessage",
        on_delete=models.CASCADE,
        related_name="reports",
    )
    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="chat_reports",
    )
    category = models.CharField(max_length=32, choices=CATEGORY_CHOICES)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=["message", "category"]),
            models.Index(fields=["reporter", "message"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["message", "reporter", "category"],
                name="unique_report_per_category",
            )
        ]

    def __str__(self) -> str:  # pragma: no cover - debug helper
        return f"ChatMessageReport<{self.id}:{self.category}>"


class ChatModerationCaseQuerySet(models.QuerySet):
    def open(self):
        return self.exclude(status=ChatMessageFlag.STATUS_RESOLVED)

    def overdue(self):
        now = timezone.now()
        return self.filter(sla_due_at__lt=now, status__in=[ChatMessageFlag.STATUS_OPEN, ChatMessageFlag.STATUS_IN_REVIEW])


class ChatModerationCase(models.Model):
    PRIORITY_LOW = "low"
    PRIORITY_MEDIUM = "medium"
    PRIORITY_HIGH = "high"

    PRIORITY_CHOICES = [
        (PRIORITY_LOW, "Low"),
        (PRIORITY_MEDIUM, "Medium"),
        (PRIORITY_HIGH, "High"),
    ]

    message = models.ForeignKey(
        "chat.ChatMessage",
        on_delete=models.CASCADE,
        related_name="moderation_cases",
    )
    thread = models.ForeignKey(
        "chat.ChatThread",
        on_delete=models.CASCADE,
        related_name="moderation_cases",
    )
    status = models.CharField(max_length=16, choices=ChatMessageFlag.STATUS_CHOICES, default=ChatMessageFlag.STATUS_OPEN)
    priority = models.CharField(max_length=16, choices=PRIORITY_CHOICES, default=PRIORITY_MEDIUM)
    escalation_reason = models.CharField(max_length=255)
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="assigned_moderation_cases",
    )
    sla_due_at = models.DateTimeField()
    escalated_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolution_notes = models.TextField(blank=True)

    objects = ChatModerationCaseQuerySet.as_manager()

    class Meta:
        ordering = ("-escalated_at",)
        indexes = [
            models.Index(fields=["status", "priority"]),
            models.Index(fields=["sla_due_at"]),
        ]

    def mark_resolved(self, *, actor, notes: str = "") -> None:
        self.status = ChatMessageFlag.STATUS_RESOLVED
        self.resolved_at = timezone.now()
        self.resolution_notes = notes
        self.assigned_to = actor
        self.save(update_fields=["status", "resolved_at", "resolution_notes", "assigned_to", "updated_at"])


class StaffActionLog(models.Model):
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="staff_actions",
    )
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveBigIntegerField()
    target = GenericForeignKey("content_type", "object_id")
    action = models.CharField(max_length=64)
    payload = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
        ]

    def __str__(self) -> str:  # pragma: no cover - debug helper
        return f"StaffAction<{self.action}:{self.object_id}>"


@dataclass(frozen=True)
class EscalationDecision:
    case: ChatModerationCase
    created: bool


__all__ = [
    "ChatMessageFlag",
    "ChatMessageReport",
    "ChatModerationCase",
    "ChatParticipantRestriction",
    "ChatRedFlagPattern",
    "EscalationDecision",
    "StaffActionLog",
]
