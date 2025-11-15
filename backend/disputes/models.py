from __future__ import annotations

import uuid

from django.conf import settings
from django.db import models
from marketplace.models import Contract
from uploads.storage import private_storage


class DisputeCase(models.Model):
    STATUS_OPENED = "opened"
    STATUS_EVIDENCE = "evidence_needed"
    STATUS_IN_REVIEW = "in_review"
    STATUS_PROPOSED = "resolution_proposed"
    STATUS_RESOLVED = "resolved"
    STATUS_AUTO_RESOLVED = "auto_resolved"

    STATUS_CHOICES = [
        (STATUS_OPENED, "Opened"),
        (STATUS_EVIDENCE, "Evidence needed"),
        (STATUS_IN_REVIEW, "In review"),
        (STATUS_PROPOSED, "Resolution proposed"),
        (STATUS_RESOLVED, "Resolved"),
        (STATUS_AUTO_RESOLVED, "Auto resolved"),
    ]

    ROLE_CLAIMANT = "claimant"
    ROLE_RESPONDENT = "respondent"
    ROLE_MODERATOR = "moderator"
    ROLE_FINANCE = "finance_observer"

    PRIORITY_LOW = "low"
    PRIORITY_MEDIUM = "medium"
    PRIORITY_HIGH = "high"

    PRIORITY_CHOICES = [
        (PRIORITY_LOW, "Low"),
        (PRIORITY_MEDIUM, "Medium"),
        (PRIORITY_HIGH, "High"),
    ]

    OUTCOME_FULL_RELEASE = "full_release"
    OUTCOME_PARTIAL_RELEASE = "partial_release"
    OUTCOME_REFUND = "refund"

    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, related_name="dispute_cases")
    escrow_reference = models.CharField(max_length=64, blank=True)
    status = models.CharField(max_length=32, choices=STATUS_CHOICES, default=STATUS_OPENED)
    priority = models.CharField(max_length=16, choices=PRIORITY_CHOICES, default=PRIORITY_MEDIUM)
    opened_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="opened_disputes")
    category = models.CharField(max_length=64, blank=True)
    claim_summary = models.TextField(blank=True)
    amount_under_review = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    sla_due_at = models.DateTimeField()
    release_frozen_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolution_notes = models.TextField(blank=True)
    auto_resolved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=["status", "priority"]),
            models.Index(fields=["sla_due_at"]),
        ]

    def __str__(self):  # pragma: no cover - debug helper
        return f"DisputeCase<{self.id}:{self.contract_id}>"

    @property
    def is_open(self) -> bool:
        return self.status not in {self.STATUS_RESOLVED, self.STATUS_AUTO_RESOLVED}

    def freeze_contract(self):
        self.contract.escrow_release_frozen = True
        self.contract.escrow_frozen_reason = "Dispute in progress"
        self.contract.save(update_fields=["escrow_release_frozen", "escrow_frozen_reason"])

    def unfreeze_contract(self, reason: str = ""):
        self.contract.escrow_release_frozen = False
        self.contract.escrow_frozen_reason = reason
        self.contract.save(update_fields=["escrow_release_frozen", "escrow_frozen_reason"])


class DisputeParticipant(models.Model):
    ROLE_CHOICES = [
        (DisputeCase.ROLE_CLAIMANT, "Claimant"),
        (DisputeCase.ROLE_RESPONDENT, "Respondent"),
        (DisputeCase.ROLE_MODERATOR, "Moderator"),
        (DisputeCase.ROLE_FINANCE, "Finance observer"),
    ]

    case = models.ForeignKey(DisputeCase, on_delete=models.CASCADE, related_name="participants")
    profile = models.ForeignKey("accounts.Profile", on_delete=models.CASCADE, related_name="dispute_participations")
    role = models.CharField(max_length=32, choices=ROLE_CHOICES)
    invited_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="added_dispute_participants")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("case", "profile", "role")

    def __str__(self):  # pragma: no cover
        return f"DisputeParticipant<{self.case_id}:{self.role}>"


class DisputeEvidence(models.Model):
    KIND_FILE = "file"
    KIND_LINK = "link"

    KIND_CHOICES = [
        (KIND_FILE, "File"),
        (KIND_LINK, "Link"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    case = models.ForeignKey(DisputeCase, on_delete=models.CASCADE, related_name="evidence")
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="uploaded_evidence")
    kind = models.CharField(max_length=16, choices=KIND_CHOICES, default=KIND_FILE)
    file = models.FileField(storage=private_storage, upload_to="disputes/evidence/%Y/%m/%d", blank=True, null=True)
    link_url = models.URLField(blank=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    scanned_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("created_at",)

    def __str__(self):  # pragma: no cover
        return f"DisputeEvidence<{self.id}>"


class DisputeTimelineEvent(models.Model):
    EVENT_MESSAGE = "message"
    EVENT_STATUS = "status_change"
    EVENT_EVIDENCE = "evidence_uploaded"
    EVENT_NOTE = "staff_note"
    EVENT_OUTCOME = "outcome"

    EVENT_CHOICES = [
        (EVENT_MESSAGE, "Message"),
        (EVENT_STATUS, "Status change"),
        (EVENT_EVIDENCE, "Evidence"),
        (EVENT_NOTE, "Note"),
        (EVENT_OUTCOME, "Outcome"),
    ]

    case = models.ForeignKey(DisputeCase, on_delete=models.CASCADE, related_name="events")
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="dispute_events")
    event_type = models.CharField(max_length=32, choices=EVENT_CHOICES)
    payload = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("created_at",)


class DisputeOutcome(models.Model):
    OUTCOME_CHOICES = [
        (DisputeCase.OUTCOME_FULL_RELEASE, "Full release"),
        (DisputeCase.OUTCOME_PARTIAL_RELEASE, "Partial release"),
        (DisputeCase.OUTCOME_REFUND, "Refund"),
    ]

    case = models.OneToOneField(DisputeCase, on_delete=models.CASCADE, related_name="outcome")
    outcome_type = models.CharField(max_length=32, choices=OUTCOME_CHOICES)
    payload = models.JSONField(default=dict, blank=True)
    executed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="executed_dispute_outcomes")
    executed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):  # pragma: no cover
        return f"DisputeOutcome<{self.case_id}:{self.outcome_type}>"
