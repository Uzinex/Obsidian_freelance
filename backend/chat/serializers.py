from __future__ import annotations

from django.urls import reverse
from rest_framework import serializers

from .models import ChatAttachment, ChatMessage, ChatThread
from .services import QUICK_ACTIONS, create_message, store_attachment


class ChatAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatAttachment
        fields = [
            "id",
            "original_name",
            "mime_type",
            "size",
            "created_at",
        ]
        read_only_fields = fields


class ChatMessageSerializer(serializers.ModelSerializer):
    attachments = ChatAttachmentSerializer(many=True, read_only=True)
    tags = serializers.SerializerMethodField()

    class Meta:
        model = ChatMessage
        fields = [
            "id",
            "thread_id",
            "sender_id",
            "body",
            "status",
            "sent_at",
            "delivered_at",
            "read_at",
            "action",
            "tags",
            "attachments",
        ]
        read_only_fields = fields

    def get_tags(self, obj: ChatMessage) -> list[str]:
        return obj.tag_labels


class ChatMessageCreateSerializer(serializers.Serializer):
    body = serializers.CharField(allow_blank=True, required=False)
    attachments = serializers.ListField(
        child=serializers.UUIDField(), required=False, allow_empty=True
    )
    action = serializers.ChoiceField(
        choices=[(key, label) for key, label in QUICK_ACTIONS.items()],
        required=False,
        allow_blank=True,
    )

    def validate(self, attrs):
        body = attrs.get("body", "")
        attachments = attrs.get("attachments", [])
        if not body and not attachments and not attrs.get("action"):
            raise serializers.ValidationError("Нельзя отправить пустое сообщение")
        return attrs

    def create(self, validated_data):
        thread = self.context["thread"]
        sender = self.context["request"].user
        attachments = validated_data.get("attachments", [])
        return create_message(
            thread=thread,
            sender=sender,
            body=validated_data.get("body", ""),
            attachment_ids=attachments,
            action=validated_data.get("action") or None,
        )

    def to_representation(self, instance):  # pragma: no cover - delegated serializer
        return ChatMessageSerializer(instance, context=self.context).data


class ChatThreadSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatThread
        fields = [
            "id",
            "contract_id",
            "client_id",
            "freelancer_id",
            "last_message_at",
            "blocked_until",
            "blocked_reason",
        ]
        read_only_fields = fields


class ChatAttachmentUploadSerializer(serializers.Serializer):
    file = serializers.FileField()

    def create(self, validated_data):
        thread = self.context["thread"]
        uploaded_by = self.context["request"].user
        return store_attachment(thread=thread, uploaded_by=uploaded_by, file_obj=validated_data["file"])

    def to_representation(self, instance):  # pragma: no cover - delegated serializer
        return ChatAttachmentSerializer(instance, context=self.context).data


class ChatMessageStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=ChatMessage.STATUS_CHOICES)


class ChatAttachmentPresignSerializer(serializers.Serializer):
    ttl = serializers.IntegerField(required=False, min_value=60, max_value=3600)

    def create(self, validated_data):
        attachment = self.context["attachment"]
        ttl = validated_data.get("ttl", 300)
        link = attachment.build_presigned_link(ttl_seconds=ttl)
        download_path = reverse(
            "chat-attachment-download",
            kwargs={"attachment_id": attachment.id},
        )
        request = self.context.get("request")
        if request is not None:
            download_path = request.build_absolute_uri(download_path)
        return {
            "url": f"{download_path}?token={link.token}",
            "expires_at": link.expires_at,
        }

    def to_representation(self, instance):  # pragma: no cover - passthrough
        return instance
