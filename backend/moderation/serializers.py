from __future__ import annotations

from rest_framework import serializers

from chat.serializers import ChatMessageSerializer

from .models import ChatMessageFlag, ChatModerationCase
from .services import file_user_report


class ChatMessageReportSerializer(serializers.Serializer):
    category = serializers.ChoiceField(choices=ChatMessageFlag.CATEGORY_CHOICES)
    comment = serializers.CharField(max_length=500, allow_blank=True, required=False)

    def create(self, validated_data):
        message = self.context["message"]
        request = self.context["request"]
        return file_user_report(
            message=message,
            reporter=request.user,
            category=validated_data["category"],
            comment=validated_data.get("comment", ""),
        )

    def to_representation(self, instance):  # pragma: no cover - passthrough for API output
        return {
            "id": instance.id,
            "category": instance.category,
            "comment": instance.comment,
            "created_at": instance.created_at,
        }


class ChatModerationCaseSerializer(serializers.ModelSerializer):
    message = ChatMessageSerializer(read_only=True)
    is_overdue = serializers.SerializerMethodField()

    class Meta:
        model = ChatModerationCase
        fields = [
            "id",
            "message",
            "thread_id",
            "status",
            "priority",
            "escalation_reason",
            "assigned_to_id",
            "sla_due_at",
            "escalated_at",
            "resolved_at",
            "resolution_notes",
            "is_overdue",
        ]
        read_only_fields = fields

    def get_is_overdue(self, obj: ChatModerationCase) -> bool:
        from django.utils import timezone

        reference = obj.resolved_at or timezone.now()
        return obj.sla_due_at < reference


class ChatModerationCaseUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=ChatMessageFlag.STATUS_CHOICES)
    resolution_notes = serializers.CharField(allow_blank=True, required=False)

    def save(self, **kwargs):
        case: ChatModerationCase = self.context["case"]
        actor = self.context["request"].user
        status_value = self.validated_data["status"]
        case.status = status_value
        if status_value == ChatMessageFlag.STATUS_RESOLVED:
            case.mark_resolved(actor=actor, notes=self.validated_data.get("resolution_notes", ""))
        else:
            case.assigned_to = actor
            case.resolution_notes = self.validated_data.get("resolution_notes", case.resolution_notes)
            case.save(update_fields=["status", "assigned_to", "resolution_notes", "updated_at"])
        return case
