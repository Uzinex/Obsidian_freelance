from __future__ import annotations

from django.utils import timezone
from rest_framework import generics, permissions
from rest_framework.response import Response

from .models import ChatModerationCase
from .permissions import IsModerator
from .serializers import ChatModerationCaseSerializer, ChatModerationCaseUpdateSerializer


class ModerationCaseListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated, IsModerator]
    serializer_class = ChatModerationCaseSerializer

    def get_queryset(self):
        queryset = ChatModerationCase.objects.select_related("message", "thread", "message__sender").all()
        status_value = self.request.query_params.get("status")
        if status_value:
            queryset = queryset.filter(status=status_value)
        priority = self.request.query_params.get("priority")
        if priority:
            queryset = queryset.filter(priority=priority)
        overdue = self.request.query_params.get("overdue")
        if overdue in {"1", "true", "yes"}:
            queryset = queryset.filter(sla_due_at__lt=timezone.now()).exclude(status=ChatModerationCase.STATUS_RESOLVED)
        category = self.request.query_params.get("category")
        if category:
            queryset = queryset.filter(message__moderation_flags__category=category).distinct()
        thread_id = self.request.query_params.get("thread")
        if thread_id:
            queryset = queryset.filter(thread_id=thread_id)
        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["now"] = timezone.now()
        return context


class ModerationCaseDetailView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated, IsModerator]
    serializer_class = ChatModerationCaseSerializer
    queryset = ChatModerationCase.objects.select_related("message", "thread", "message__sender")

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["now"] = timezone.now()
        return context


class ModerationCaseUpdateView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated, IsModerator]
    serializer_class = ChatModerationCaseUpdateSerializer

    def get_case(self):
        return ChatModerationCase.objects.select_related("message").get(pk=self.kwargs["case_id"])

    def post(self, request, *args, **kwargs):
        case = self.get_case()
        serializer = self.get_serializer(data=request.data, context={"case": case, "request": request})
        serializer.is_valid(raise_exception=True)
        result = serializer.save()
        output = ChatModerationCaseSerializer(result, context={"now": timezone.now()})
        return Response(output.data)
