from __future__ import annotations

import hashlib
import uuid
from datetime import timedelta

from django.conf import settings
from django.core.files.base import ContentFile
from django.db import models
from django.utils import timezone

from .storage import private_storage


class SecureDocument(models.Model):
    CATEGORY_PORTFOLIO = "portfolio"
    CATEGORY_KYC = "kyc"

    CATEGORY_CHOICES = [
        (CATEGORY_PORTFOLIO, "Portfolio"),
        (CATEGORY_KYC, "KYC"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="secure_documents",
    )
    category = models.CharField(max_length=32, choices=CATEGORY_CHOICES)
    file = models.FileField(storage=private_storage, upload_to="secure", max_length=512)
    original_name = models.CharField(max_length=255)
    mime_type = models.CharField(max_length=64)
    checksum = models.CharField(max_length=64)
    size = models.PositiveBigIntegerField()
    scanned_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=["owner", "category"]),
        ]

    def __str__(self) -> str:  # pragma: no cover - debug helper
        return f"SecureDocument<{self.pk}>"

    def attach_file(self, *, data: bytes, name: str, mime_type: str) -> None:
        checksum = hashlib.sha256(data).hexdigest()
        content = ContentFile(data, name=name)
        self.file.save(name, content, save=False)
        self.original_name = name
        self.mime_type = mime_type
        self.checksum = checksum
        self.size = len(data)
        self.save()

    def mark_scanned(self) -> None:
        self.scanned_at = timezone.now()
        self.save(update_fields=["scanned_at", "updated_at"])

    def build_presigned_token(self, *, ttl_seconds: int = 300) -> "SecureDocumentLink":
        link = SecureDocumentLink(document=self)
        link.save(expires_in=ttl_seconds)
        return link


class SecureDocumentLink(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document = models.ForeignKey(
        SecureDocument,
        on_delete=models.CASCADE,
        related_name="links",
    )
    token = models.CharField(max_length=64, unique=True)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["document", "expires_at"]),
        ]

    def save(self, *args, **kwargs):
        if not self.token:
            raw = f"{self.document_id}:{uuid.uuid4()}".encode("utf-8")
            self.token = hashlib.sha256(raw).hexdigest()
        if not self.expires_at:
            ttl = kwargs.pop("expires_in", 300)
            self.expires_at = timezone.now() + timedelta(seconds=ttl)
        super().save(*args, **kwargs)

    def is_valid(self) -> bool:
        return timezone.now() < self.expires_at

    def refresh(self, *, ttl_seconds: int = 300) -> None:
        self.expires_at = timezone.now() + timedelta(seconds=ttl_seconds)
        self.save(update_fields=["expires_at", "updated_at"])
