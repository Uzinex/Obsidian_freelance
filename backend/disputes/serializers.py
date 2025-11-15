from __future__ import annotations

from rest_framework import serializers

from .models import DisputeCase, DisputeEvidence, DisputeOutcome, DisputeParticipant, DisputeTimelineEvent
from .services import add_evidence, open_dispute, record_outcome, update_status


class DisputeEvidenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = DisputeEvidence
        fields = [
            "id",
            "kind",
            "title",
            "description",
            "link_url",
            "created_at",
            "scanned_at",
        ]
        read_only_fields = fields


class DisputeParticipantSerializer(serializers.ModelSerializer):
    class Meta:
        model = DisputeParticipant
        fields = ["profile_id", "role", "created_at"]
        read_only_fields = fields


class DisputeCaseSerializer(serializers.ModelSerializer):
    evidence = DisputeEvidenceSerializer(many=True, read_only=True)
    participants = DisputeParticipantSerializer(many=True, read_only=True)
    events = serializers.SerializerMethodField()
    outcome = serializers.SerializerMethodField()

    class Meta:
        model = DisputeCase
        fields = [
            "id",
            "contract_id",
            "status",
            "priority",
            "category",
            "claim_summary",
            "amount_under_review",
            "sla_due_at",
            "release_frozen_at",
            "resolved_at",
            "resolution_notes",
            "created_at",
            "updated_at",
            "evidence",
            "participants",
            "events",
            "outcome",
        ]
        read_only_fields = fields

    def get_events(self, obj: DisputeCase):
        events = obj.events.order_by("created_at")
        output = []
        for event in events:
            output.append(
                {
                    "type": event.event_type,
                    "payload": event.payload,
                    "created_at": event.created_at,
                    "actor_id": event.actor_id,
                }
            )
        return output

    def get_outcome(self, obj: DisputeCase):
        if not hasattr(obj, "outcome") or obj.outcome is None:
            return None
        return {
            "outcome": obj.outcome.outcome_type,
            "payload": obj.outcome.payload,
            "executed_at": obj.outcome.executed_at,
        }


class DisputeCaseCreateSerializer(serializers.Serializer):
    category = serializers.CharField(max_length=64)
    claim_summary = serializers.CharField(allow_blank=True, required=False)

    def create(self, validated_data):
        contract = self.context["contract"]
        request = self.context["request"]
        return open_dispute(
            contract=contract,
            opened_by=request.user,
            category=validated_data["category"],
            claim_summary=validated_data.get("claim_summary", ""),
        )

    def to_representation(self, instance):  # pragma: no cover
        return DisputeCaseSerializer(instance, context=self.context).data


class DisputeEvidenceUploadSerializer(serializers.Serializer):
    file = serializers.FileField(required=False)
    link_url = serializers.URLField(required=False, allow_blank=True)
    title = serializers.CharField(max_length=255, required=False)
    description = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        if not attrs.get("file") and not attrs.get("link_url"):
            raise serializers.ValidationError("Нужно загрузить файл или ссылку")
        return attrs

    def create(self, validated_data):
        case = self.context["case"]
        request = self.context["request"]
        return add_evidence(
            case=case,
            uploaded_by=request.user,
            file_obj=validated_data.get("file"),
            link_url=validated_data.get("link_url", ""),
            title=validated_data.get("title", ""),
            description=validated_data.get("description", ""),
        )

    def to_representation(self, instance):  # pragma: no cover
        return DisputeEvidenceSerializer(instance).data


class DisputeStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=DisputeCase.STATUS_CHOICES)
    note = serializers.CharField(allow_blank=True, required=False)

    def create(self, validated_data):
        case = self.context["case"]
        actor = self.context["request"].user
        return update_status(case=case, status=validated_data["status"], actor=actor, note=validated_data.get("note", ""))

    def to_representation(self, instance):  # pragma: no cover
        return DisputeCaseSerializer(instance).data


class DisputeOutcomeSerializer(serializers.Serializer):
    outcome = serializers.ChoiceField(choices=DisputeOutcome.OUTCOME_CHOICES)
    payload = serializers.JSONField(required=False)

    def create(self, validated_data):
        case = self.context["case"]
        actor = self.context["request"].user
        return record_outcome(case=case, outcome_type=validated_data["outcome"], actor=actor, payload=validated_data.get("payload", {}))

    def to_representation(self, instance):  # pragma: no cover
        return {
            "case": instance.case_id,
            "outcome": instance.outcome_type,
            "payload": instance.payload,
            "executed_at": instance.executed_at,
        }
