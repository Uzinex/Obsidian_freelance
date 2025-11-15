from __future__ import annotations

import hashlib
import re
import uuid
from datetime import timedelta

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from marketplace.models import Contract
from uploads.storage import private_storage

_LINK_PATTERN = re.compile(r"https?://", re.IGNORECASE)


class ChatThread(models.Model):
    """Represents a 1:1 conversation scoped to a contract."""

    contract = models.OneToOneField(
        Contract,
        on_delete=models.CASCADE,
        related_name="chat_thread",
    )
    client = models.ForeignKey(
        "accounts.Profile",
        on_delete=models.CASCADE,
        related_name="client_threads",
    )
    freelancer = models.ForeignKey(
        "accounts.Profile",
        on_delete=models.CASCADE,
        related_name="freelancer_threads",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_message_at = models.DateTimeField(null=True, blank=True)
    blocked_until = models.DateTimeField(null=True, blank=True)
    blocked_reason = models.CharField(max_length=255, blank=True)
    blocked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="blocked_threads",
    )

    class Meta:
        ordering = ("-last_message_at", "-updated_at")
        indexes = [
            models.Index(fields=["contract"]),
            models.Index(fields=["client"]),
            models.Index(fields=["freelancer"]),
        ]

    def __str__(self) -> str:  # pragma: no cover - debugging helper
        return f"ChatThread<{self.contract_id}>"

    def is_participant(self, user) -> bool:
        if not getattr(user, "is_authenticated", False):
            return False
        if getattr(user, "is_staff", False) or getattr(user, "is_superuser", False):
            return True
        profile = getattr(user, "profile", None)
        if not profile:
            return False
        return profile_id_matches(profile_id=profile.id, thread=self)

    def is_blocked(self) -> bool:
        return bool(self.blocked_until and self.blocked_until > timezone.now())

    def block(self, *, until: timezone.datetime, reason: str, by_user) -> None:
        self.blocked_until = until
        self.blocked_reason = reason
        self.blocked_by = by_user
        self.save(update_fields=["blocked_until", "blocked_reason", "blocked_by", "updated_at"])

    def unblock(self) -> None:
        self.blocked_until = None
        self.blocked_reason = ""
        self.blocked_by = None
        self.save(update_fields=["blocked_until", "blocked_reason", "blocked_by", "updated_at"])


class ChatMessageQuerySet(models.QuerySet):
    def visible(self):
        return self.filter(is_deleted=False, is_hidden=False)

    def with_tag(self, tag: str | None):
        if not tag:
            return self
        if tag == "has_attachments":
            return self.filter(has_attachments=True)
        if tag == "link":
            return self.filter(contains_link=True)
        return self


class ChatMessage(models.Model):
    STATUS_SENT = "sent"
    STATUS_DELIVERED = "delivered"
    STATUS_READ = "read"

    STATUS_CHOICES = [
        (STATUS_SENT, "Sent"),
        (STATUS_DELIVERED, "Delivered"),
        (STATUS_READ, "Read"),
    ]

    thread = models.ForeignKey(ChatThread, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="chat_messages")
    body = models.TextField(blank=True)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=STATUS_SENT)
    sent_at = models.DateTimeField(auto_now_add=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    read_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    action = models.CharField(max_length=64, blank=True)
    has_attachments = models.BooleanField(default=False)
    contains_link = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    is_hidden = models.BooleanField(default=False)
    hidden_at = models.DateTimeField(null=True, blank=True)
    hidden_reason = models.CharField(max_length=255, blank=True)
    hidden_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="moderated_chat_messages",
    )

    objects = ChatMessageQuerySet.as_manager()

    class Meta:
        ordering = ("sent_at", "pk")
        indexes = [
            models.Index(fields=["thread", "sent_at"]),
            models.Index(fields=["thread", "status"]),
            models.Index(fields=["contains_link"]),
            models.Index(fields=["has_attachments"]),
        ]

    def __str__(self) -> str:  # pragma: no cover - debugging helper
        return f"ChatMessage<{self.pk}>"

    def apply_status(self, status: str) -> None:
        if status not in {self.STATUS_SENT, self.STATUS_DELIVERED, self.STATUS_READ}:
            raise ValidationError("Unknown chat message status")
        now = timezone.now()
        if status == self.STATUS_DELIVERED and self.delivered_at is None:
            self.status = status
            self.delivered_at = now
        elif status == self.STATUS_READ:
            self.status = status
            if self.delivered_at is None:
                self.delivered_at = now
            self.read_at = now if self.read_at is None else self.read_at
        self.save(update_fields=["status", "delivered_at", "read_at", "updated_at"])

    def soft_delete(self, *, by_user=None, reason: str = "") -> None:
        if self.is_deleted:
            return
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.hidden_reason = reason or self.hidden_reason
        self.hidden_by = by_user or self.hidden_by
        self.save(update_fields=["is_deleted", "deleted_at", "hidden_reason", "hidden_by", "updated_at"])

    def hide(self, *, by_user, reason: str) -> None:
        self.is_hidden = True
        self.hidden_by = by_user
        self.hidden_reason = reason
        self.hidden_at = timezone.now()
        self.save(update_fields=[
            "is_hidden",
            "hidden_by",
            "hidden_reason",
            "hidden_at",
            "updated_at",
        ])

    @property
    def tag_labels(self) -> list[str]:
        tags: list[str] = []
        if self.has_attachments:
            tags.append("has_attachments")
        if self.contains_link:
            tags.append("link")
        if self.action:
            tags.append("action")
        return tags


class ChatAttachment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    thread = models.ForeignKey(ChatThread, on_delete=models.CASCADE, related_name="attachments")
    message = models.ForeignKey(
        ChatMessage,
        on_delete=models.CASCADE,
        related_name="attachments",
        null=True,
        blank=True,
    )
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="chat_attachments",
    )
    file = models.FileField(
        storage=private_storage,
        upload_to="chat/attachments/%Y/%m/%d",
        max_length=512,
    )
    original_name = models.CharField(max_length=255)
    mime_type = models.CharField(max_length=64)
    size = models.PositiveBigIntegerField()
    checksum = models.CharField(max_length=64)
    scanned_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("created_at",)
        indexes = [
            models.Index(fields=["thread", "created_at"]),
            models.Index(fields=["uploaded_by"]),
        ]

    def __str__(self) -> str:  # pragma: no cover - debugging helper
        return f"ChatAttachment<{self.pk}>"

    def mark_scanned(self) -> None:
        self.scanned_at = timezone.now()
        self.save(update_fields=["scanned_at", "updated_at"])

    def attach_to_message(self, message: ChatMessage) -> None:
        self.message = message
        self.save(update_fields=["message", "updated_at"])

    def build_presigned_link(self, *, ttl_seconds: int = 300) -> "ChatAttachmentLink":
        link = ChatAttachmentLink(attachment=self)
        link.save(expires_in=ttl_seconds)
        return link


class ChatAttachmentLink(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    attachment = models.ForeignKey(
        ChatAttachment,
        on_delete=models.CASCADE,
        related_name="links",
    )
    token = models.CharField(max_length=64, unique=True)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["attachment", "expires_at"]),
        ]

    def save(self, *args, **kwargs):
        if not self.token:
            raw = f"{self.attachment_id}:{uuid.uuid4()}".encode("utf-8")
            self.token = hashlib.sha256(raw).hexdigest()
        if not self.expires_at:
            ttl = kwargs.pop("expires_in", 300)
            self.expires_at = timezone.now() + timedelta(seconds=ttl)
        return super().save(*args, **kwargs)

    def is_valid(self) -> bool:
        return timezone.now() < self.expires_at


def profile_id_matches(*, profile_id: int | None, thread: ChatThread) -> bool:
    return bool(profile_id and profile_id in {thread.client_id, thread.freelancer_id})
