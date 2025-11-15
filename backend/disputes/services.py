from __future__ import annotations

from datetime import timedelta

from django.core.files.base import ContentFile
from django.db import transaction
from django.utils import timezone

from moderation.services import log_staff_action
from uploads.scanner import scan_bytes

from .models import DisputeCase, DisputeEvidence, DisputeOutcome, DisputeTimelineEvent


def open_dispute(*, contract, opened_by, category: str, claim_summary: str = "") -> DisputeCase:
    with transaction.atomic():
        case = DisputeCase.objects.create(
            contract=contract,
            escrow_reference=f"contract:{contract.id}",
            opened_by=opened_by,
            category=category,
            claim_summary=claim_summary,
            amount_under_review=contract.budget_snapshot,
            sla_due_at=timezone.now() + timedelta(hours=24),
        )
        case.freeze_contract()
        for profile, role in (
            (contract.client, DisputeCase.ROLE_CLAIMANT),
            (contract.freelancer, DisputeCase.ROLE_RESPONDENT),
        ):
            case.participants.create(profile=profile, role=role, invited_by=opened_by)
        DisputeTimelineEvent.objects.create(
            case=case,
            actor=opened_by,
            event_type=DisputeTimelineEvent.EVENT_STATUS,
            payload={"status": DisputeCase.STATUS_OPENED, "category": category},
        )
        log_staff_action(actor=opened_by, target=case, action="dispute.opened", payload={"category": category})
    return case


def add_evidence(*, case: DisputeCase, uploaded_by, file_obj=None, link_url: str = "", title: str = "", description: str = "") -> DisputeEvidence:
    evidence = DisputeEvidence(case=case, uploaded_by=uploaded_by, title=title or "Evidence", description=description)
    if file_obj:
        raw = file_obj.read()
        scan_bytes(raw, filename=file_obj.name)
        content = ContentFile(raw, name=file_obj.name)
        evidence.kind = DisputeEvidence.KIND_FILE
        evidence.file.save(file_obj.name, content, save=False)
        evidence.scanned_at = timezone.now()
    elif link_url:
        evidence.kind = DisputeEvidence.KIND_LINK
        evidence.link_url = link_url
    evidence.save()
    DisputeTimelineEvent.objects.create(
        case=case,
        actor=uploaded_by,
        event_type=DisputeTimelineEvent.EVENT_EVIDENCE,
        payload={"evidence_id": str(evidence.id), "title": evidence.title, "kind": evidence.kind},
    )
    return evidence


def update_status(*, case: DisputeCase, status: str, actor, note: str = "") -> DisputeCase:
    case.status = status
    case.updated_at = timezone.now()
    case.save(update_fields=["status", "updated_at"])
    DisputeTimelineEvent.objects.create(
        case=case,
        actor=actor,
        event_type=DisputeTimelineEvent.EVENT_STATUS,
        payload={"status": status, "note": note},
    )
    log_staff_action(actor=actor, target=case, action="dispute.status", payload={"status": status})
    return case


def record_outcome(*, case: DisputeCase, outcome_type: str, actor, payload: dict | None = None) -> DisputeOutcome:
    outcome, _ = DisputeOutcome.objects.update_or_create(
        case=case,
        defaults={"outcome_type": outcome_type, "payload": payload or {}, "executed_by": actor},
    )
    case.status = DisputeCase.STATUS_RESOLVED
    case.resolved_at = timezone.now()
    case.resolution_notes = f"Outcome: {outcome_type}"
    case.unfreeze_contract(reason="Dispute resolved")
    case.save(update_fields=["status", "resolved_at", "resolution_notes", "updated_at"])
    DisputeTimelineEvent.objects.create(
        case=case,
        actor=actor,
        event_type=DisputeTimelineEvent.EVENT_OUTCOME,
        payload={"outcome": outcome_type, "payload": payload or {}},
    )
    log_staff_action(actor=actor, target=case, action="dispute.outcome", payload={"outcome": outcome_type})
    return outcome


__all__ = [
    "add_evidence",
    "open_dispute",
    "record_outcome",
    "update_status",
]
