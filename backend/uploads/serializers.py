from __future__ import annotations

from rest_framework import serializers

from .models import SecureDocument, SecureDocumentLink


class SecureDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = SecureDocument
        fields = [
            "id",
            "category",
            "original_name",
            "mime_type",
            "size",
            "created_at",
            "scanned_at",
        ]
        read_only_fields = [
            "id",
            "original_name",
            "mime_type",
            "size",
            "created_at",
            "scanned_at",
        ]


class SecureDocumentLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = SecureDocumentLink
        fields = ["token", "expires_at"]
        read_only_fields = fields


class SecureDocumentUploadSerializer(serializers.Serializer):
    category = serializers.ChoiceField(choices=SecureDocument.CATEGORY_CHOICES)
    file = serializers.FileField()
