from __future__ import annotations

from datetime import timedelta
from typing import Any

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone


class NotificationEventQuerySet(models.QuerySet):
    def for_user(self, user):
        if not getattr(user, "is_authenticated", False):
            return self.none()
        return self.filter(recipient=user)

    def unread(self):
        return self.filter(is_read=False)


class NotificationEvent(models.Model):
    CATEGORY_CHAT = "chat"
    CATEGORY_CONTRACT = "contract"
    CATEGORY_PAYMENTS = "payments"
    CATEGORY_ACCOUNT = "account"

    CATEGORY_CHOICES = [
        (CATEGORY_CHAT, "Chat"),
        (CATEGORY_CONTRACT, "Contract"),
        (CATEGORY_PAYMENTS, "Payments"),
        (CATEGORY_ACCOUNT, "Account"),
    ]

    class Priority(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"

    class EventType(models.TextChoices):
        CHAT_NEW_MESSAGE = "chat.new_message", "Chat: new message"
        CHAT_MENTION = "chat.mention", "Chat: mention"
        CONTRACT_CREATED = "contract.created", "Contract created"
        CONTRACT_SIGNED = "contract.signed", "Contract signed"
        CONTRACT_DELIVERED = "contract.delivered", "Deliverable uploaded"
        CONTRACT_DISPUTE_OPENED = "contract.dispute_opened", "Dispute opened"
        CONTRACT_DISPUTE_CLOSED = "contract.dispute_closed", "Dispute closed"
        CONTRACT_APPLICATION_SUBMITTED = (
            "contract.application_submitted",
            "Application submitted",
        )
        CONTRACT_APPLICATION_DECISION = (
            "contract.application_decision",
            "Application decision",
        )
        CONTRACT_TERMINATION_REQUESTED = "contract.termination_requested", "Termination requested"
        CONTRACT_TERMINATION_APPROVED = "contract.termination_approved", "Termination approved"
        CONTRACT_COMPLETED = "contract.completed", "Contract completed"
        PAYMENTS_HOLD = "payments.hold", "Funds on hold"
        PAYMENTS_RELEASE = "payments.release", "Funds released"
        PAYMENTS_PAYOUT = "payments.payout", "Payout sent"
        ACCOUNT_LOGIN = "account.login", "Account login"
        ACCOUNT_2FA = "account.2fa", "Two-factor challenge"
        ACCOUNT_PASSWORD_RESET = "account.password_reset", "Password reset"
        ACCOUNT_GENERIC = "account.generic", "Account event"

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notification_events",
    )
    profile = models.ForeignKey(
        "accounts.Profile",
        on_delete=models.SET_NULL,
        related_name="notification_events",
        null=True,
        blank=True,
    )
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="triggered_events",
        null=True,
        blank=True,
    )
    category = models.CharField(max_length=32, choices=CATEGORY_CHOICES)
    event_type = models.CharField(max_length=64, choices=EventType.choices)
    title = models.CharField(max_length=255)
    body = models.TextField()
    data = models.JSONField(default=dict, blank=True)
    priority = models.CharField(
        max_length=16, choices=Priority.choices, default=Priority.MEDIUM
    )
    dedupe_key = models.CharField(max_length=255, blank=True)
    throttle_until = models.DateTimeField(null=True, blank=True)
    digest_key = models.CharField(max_length=255, blank=True)
    digest_window = models.DurationField(null=True, blank=True)
    is_digest = models.BooleanField(default=False)
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = NotificationEventQuerySet.as_manager()

    class Meta:
        ordering = ("-created_at", "-id")
        indexes = [
            models.Index(fields=["recipient", "is_read"]),
            models.Index(fields=["dedupe_key", "recipient"]),
            models.Index(fields=["digest_key", "recipient"]),
        ]

    def mark_as_read(self):
        if self.is_read:
            return
        self.is_read = True
        self.read_at = timezone.now()
        self.save(update_fields=["is_read", "read_at", "updated_at"])

    @property
    def message(self) -> str:
        return self.body


class NotificationDigest(models.Model):
    STATUS_PENDING = "pending"
    STATUS_SCHEDULED = "scheduled"
    STATUS_SENT = "sent"
    STATUS_CANCELLED = "cancelled"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_SCHEDULED, "Scheduled"),
        (STATUS_SENT, "Sent"),
        (STATUS_CANCELLED, "Cancelled"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notification_digests",
    )
    category = models.CharField(max_length=32, choices=NotificationEvent.CATEGORY_CHOICES)
    channel = models.CharField(max_length=32)
    period_start = models.DateTimeField()
    period_end = models.DateTimeField()
    title = models.CharField(max_length=255)
    summary = models.JSONField(default=dict, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    scheduled_for = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    events = models.ManyToManyField(NotificationEvent, related_name="digests", blank=True)

    class Meta:
        ordering = ("scheduled_for", "created_at")
        indexes = [
            models.Index(fields=["channel", "status"]),
            models.Index(fields=["scheduled_for"]),
        ]


class NotificationDelivery(models.Model):
    CHANNEL_IN_APP = "in_app"
    CHANNEL_EMAIL = "email"
    CHANNEL_WEB_PUSH = "web_push"
    CHANNEL_TELEGRAM = "telegram"

    CHANNEL_CHOICES = [
        (CHANNEL_IN_APP, "In-app"),
        (CHANNEL_EMAIL, "Email"),
        (CHANNEL_WEB_PUSH, "Web push"),
        (CHANNEL_TELEGRAM, "Telegram"),
    ]

    STATUS_PENDING = "pending"
    STATUS_SCHEDULED = "scheduled"
    STATUS_SENT = "sent"
    STATUS_FAILED = "failed"
    STATUS_SUPPRESSED = "suppressed"
    STATUS_DIGESTED = "digested"
    STATUS_THROTTLED = "throttled"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_SCHEDULED, "Scheduled"),
        (STATUS_SENT, "Sent"),
        (STATUS_FAILED, "Failed"),
        (STATUS_SUPPRESSED, "Suppressed"),
        (STATUS_DIGESTED, "Digest queued"),
        (STATUS_THROTTLED, "Throttled"),
    ]

    event = models.ForeignKey(
        NotificationEvent,
        on_delete=models.CASCADE,
        related_name="deliveries",
    )
    channel = models.CharField(max_length=32, choices=CHANNEL_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    scheduled_for = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    digest = models.ForeignKey(
        NotificationDigest,
        on_delete=models.SET_NULL,
        related_name="deliveries",
        null=True,
        blank=True,
    )
    quieted_until = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=["channel", "status"]),
        ]


class NotificationPreference(models.Model):
    FREQUENCY_IMMEDIATE = "immediate"
    FREQUENCY_DIGEST_15M = "digest_15m"
    FREQUENCY_HOURLY = "hourly"
    FREQUENCY_DAILY = "daily"

    FREQUENCY_CHOICES = [
        (FREQUENCY_IMMEDIATE, "Сразу"),
        (FREQUENCY_DIGEST_15M, "Каждые 15 минут"),
        (FREQUENCY_HOURLY, "Каждый час"),
        (FREQUENCY_DAILY, "Раз в день"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notification_preferences",
    )
    category = models.CharField(max_length=32, choices=NotificationEvent.CATEGORY_CHOICES)
    channel = models.CharField(max_length=32, choices=NotificationDelivery.CHANNEL_CHOICES)
    enabled = models.BooleanField(default=True)
    frequency = models.CharField(
        max_length=20,
        choices=FREQUENCY_CHOICES,
        default=FREQUENCY_IMMEDIATE,
    )
    language = models.CharField(max_length=8, default="ru")
    timezone = models.CharField(max_length=64, default="Asia/Tashkent")
    quiet_hours_start = models.TimeField(null=True, blank=True)
    quiet_hours_end = models.TimeField(null=True, blank=True)
    time_window_start = models.TimeField(null=True, blank=True)
    time_window_end = models.TimeField(null=True, blank=True)
    daily_digest_hour = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(0)],
        default=9,
        help_text="24h format hour when daily digests may be sent.",
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "category", "channel")
        ordering = ("user", "category")

    def as_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "category": self.category,
            "channel": self.channel,
            "enabled": self.enabled,
            "frequency": self.frequency,
            "language": self.language,
            "timezone": self.timezone,
            "quiet_hours_start": self.quiet_hours_start,
            "quiet_hours_end": self.quiet_hours_end,
            "time_window_start": self.time_window_start,
            "time_window_end": self.time_window_end,
            "daily_digest_hour": self.daily_digest_hour,
        }


class SlaActionLog(models.Model):
    rule_code = models.CharField(max_length=64)
    contract = models.ForeignKey(
        "marketplace.Contract",
        on_delete=models.CASCADE,
        related_name="sla_actions",
        null=True,
        blank=True,
    )
    dispute = models.ForeignKey(
        "disputes.DisputeCase",
        on_delete=models.CASCADE,
        related_name="sla_actions",
        null=True,
        blank=True,
    )
    chat_thread = models.ForeignKey(
        "chat.ChatThread",
        on_delete=models.CASCADE,
        related_name="sla_actions",
        null=True,
        blank=True,
    )
    metadata = models.JSONField(default=dict, blank=True)
    triggered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-triggered_at",)
        indexes = [
            models.Index(fields=["rule_code", "triggered_at"]),
        ]

    def __str__(self) -> str:  # pragma: no cover - debug helper
        return f"SLA<{self.rule_code}:{self.triggered_at:%Y-%m-%d %H:%M}>"
