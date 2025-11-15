from __future__ import annotations

from django.utils import timezone
from rest_framework import mixins, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import NotificationDelivery, NotificationEvent, NotificationPreference
from .serializers import NotificationEventSerializer, NotificationPreferenceSerializer
from .services import notification_hub


class NotificationEventViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = NotificationEventSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = (
            NotificationEvent.objects.for_user(self.request.user)
            .prefetch_related("deliveries")
            .order_by("-created_at")
        )
        category = self.request.query_params.get("category")
        channel = self.request.query_params.get("channel")
        is_read = self.request.query_params.get("is_read")
        if category:
            queryset = queryset.filter(category=category)
        if channel:
            queryset = queryset.filter(deliveries__channel=channel)
        if is_read in {"true", "false"}:
            queryset = queryset.filter(is_read=is_read == "true")
        return queryset.distinct()

    @action(detail=True, methods=["post"])
    def mark_read(self, request, pk=None):
        event = self.get_object()
        event.mark_as_read()
        serializer = self.get_serializer(event)
        return Response(serializer.data)

    @action(detail=False, methods=["post"])
    def mark_all_read(self, request):
        queryset = self.get_queryset().unread()
        updated = queryset.update(is_read=True, read_at=timezone.now())
        return Response({"updated": updated})

    @action(detail=False, methods=["post"])
    def flush_digests(self, request):
        notification_hub.flush_due_digests()
        notification_hub.dispatch_pending_deliveries()
        return Response({"status": "ok"})


class NotificationPreferenceViewSet(
    mixins.ListModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet
):
    serializer_class = NotificationPreferenceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return NotificationPreference.objects.filter(user=self.request.user)

    def list(self, request, *args, **kwargs):
        self._ensure_defaults(request.user)
        return super().list(request, *args, **kwargs)

    def _ensure_defaults(self, user):
        categories = [choice[0] for choice in NotificationEvent.CATEGORY_CHOICES]
        channels = [
            NotificationDelivery.CHANNEL_IN_APP,
            NotificationDelivery.CHANNEL_EMAIL,
            NotificationDelivery.CHANNEL_WEB_PUSH,
        ]
        for category in categories:
            for channel in channels:
                NotificationPreference.objects.get_or_create(
                    user=user,
                    category=category,
                    channel=channel,
                    defaults={"enabled": True},
                )

    def get_object(self):
        obj = super().get_object()
        if obj.user != self.request.user:
            raise permissions.PermissionDenied("Нельзя изменять чужие настройки")
        return obj

    def partial_update(self, request, *args, **kwargs):
        kwargs["partial"] = True
        return super().update(request, *args, **kwargs)
