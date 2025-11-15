from __future__ import annotations

from rest_framework import serializers

from .models import NotificationDelivery, NotificationEvent, NotificationPreference


class NotificationDeliverySerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationDelivery
        fields = ("channel", "status", "scheduled_for", "sent_at", "metadata")
        read_only_fields = fields


class NotificationEventSerializer(serializers.ModelSerializer):
    message = serializers.CharField(source="body", read_only=True)
    deliveries = NotificationDeliverySerializer(many=True, read_only=True)
    channels = serializers.SerializerMethodField()

    class Meta:
        model = NotificationEvent
        fields = (
            "id",
            "title",
            "message",
            "category",
            "event_type",
            "data",
            "is_read",
            "read_at",
            "created_at",
            "priority",
            "is_digest",
            "deliveries",
            "channels",
        )
        read_only_fields = fields

    def get_channels(self, obj: NotificationEvent) -> list[str]:
        return [delivery.channel for delivery in obj.deliveries.all()]


class NotificationPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationPreference
        fields = (
            "id",
            "category",
            "channel",
            "enabled",
            "frequency",
            "language",
            "timezone",
            "quiet_hours_start",
            "quiet_hours_end",
            "time_window_start",
            "time_window_end",
            "daily_digest_hour",
        )
        read_only_fields = ("category", "channel")
