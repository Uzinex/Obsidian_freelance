from django.contrib import admin

from .models import (
    NotificationDelivery,
    NotificationDigest,
    NotificationEvent,
    NotificationPreference,
    SlaActionLog,
)


@admin.register(NotificationEvent)
class NotificationEventAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "recipient",
        "category",
        "event_type",
        "title",
        "is_read",
        "created_at",
    )
    list_filter = ("category", "event_type", "is_read")
    search_fields = ("title", "body", "recipient__email")
    autocomplete_fields = ("recipient", "actor", "profile")


@admin.register(NotificationDelivery)
class NotificationDeliveryAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "event",
        "channel",
        "status",
        "scheduled_for",
        "sent_at",
    )
    list_filter = ("channel", "status")
    search_fields = ("event__title", "event__recipient__email")


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "category",
        "channel",
        "enabled",
        "frequency",
        "language",
    )
    list_filter = ("category", "channel", "enabled", "frequency")
    search_fields = ("user__email",)


@admin.register(NotificationDigest)
class NotificationDigestAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "channel",
        "category",
        "status",
        "scheduled_for",
        "sent_at",
    )
    list_filter = ("channel", "status")
    search_fields = ("user__email",)


@admin.register(SlaActionLog)
class SlaActionLogAdmin(admin.ModelAdmin):
    list_display = ("rule_code", "triggered_at", "contract", "dispute", "chat_thread")
    list_filter = ("rule_code",)
    search_fields = ("contract__order__title", "dispute__contract__order__title")
