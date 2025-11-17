from __future__ import annotations

from datetime import datetime, timezone as dt_timezone

from django.http import FileResponse, Http404
from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.exceptions import PermissionDenied, Throttled
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from marketplace.models import Contract

from .exceptions import ChatBlockedError, ChatRateLimitError
from .models import ChatAttachmentLink, ChatMessage
from moderation.serializers import ChatMessageReportSerializer

from .serializers import (
    ChatAttachmentPresignSerializer,
    ChatAttachmentUploadSerializer,
    ChatMessageCreateSerializer,
    ChatMessageSerializer,
    ChatMessageStatusSerializer,
    ChatThreadSerializer,
)
from .services import get_thread_for_user


class ContractThreadMixin:
    thread_cache_attr = "_thread_instance"

    def get_thread(self):
        if hasattr(self, self.thread_cache_attr):
            return getattr(self, self.thread_cache_attr)
        try:
            thread = get_thread_for_user(contract_id=self.kwargs["contract_id"], user=self.request.user)
        except Contract.DoesNotExist as exc:
            raise Http404 from exc
        setattr(self, self.thread_cache_attr, thread)
        return thread


class ChatMessagePagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = "page_size"
    max_page_size = 100


class ContractChatThreadView(ContractThreadMixin, APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        thread = self.get_thread()
        serializer = ChatThreadSerializer(thread, context={"request": request})
        return Response(serializer.data)


class ContractChatMessagesView(ContractThreadMixin, generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = ChatMessagePagination
    throttle_scope = "chat_message"

    def get_serializer_class(self):
        if self.request.method.lower() == "post":
            return ChatMessageCreateSerializer
        return ChatMessageSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["thread"] = self.get_thread()
        return context

    def get_queryset(self):
        thread = self.get_thread()
        queryset = (
            ChatMessage.objects.visible_for_user(self.request.user)
            .filter(thread=thread)
            .select_related("sender")
            .prefetch_related("attachments")
        )
        since = self.request.query_params.get("since")
        if since:
            try:
                boundary = datetime.fromisoformat(since)
                if boundary.tzinfo is None:
                    boundary = boundary.replace(tzinfo=dt_timezone.utc)
                queryset = queryset.filter(sent_at__gte=boundary)
            except ValueError:
                pass
        tag = self.request.query_params.get("tag")
        queryset = queryset.with_tag(tag)
        return queryset

    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except ChatRateLimitError as exc:
            raise Throttled(detail=str(exc)) from exc
        except ChatBlockedError as exc:
            raise PermissionDenied(detail=str(exc)) from exc


class ChatMessageStatusView(ContractThreadMixin, APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = ChatMessageStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        thread = self.get_thread()
        try:
            message = thread.messages.get(pk=kwargs["message_id"])
        except ChatMessage.DoesNotExist as exc:
            raise Http404 from exc
        message.apply_status(serializer.validated_data["status"])
        output = ChatMessageSerializer(message, context={"request": request})
        return Response(output.data)


class ChatEventPollView(ContractThreadMixin, APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        thread = self.get_thread()
        since_value = request.query_params.get("since")
        events = []
        boundary = None
        if since_value:
            try:
                boundary = datetime.fromisoformat(since_value)
                if boundary.tzinfo is None:
                    boundary = boundary.replace(tzinfo=dt_timezone.utc)
            except ValueError:
                boundary = None
        qs = (
            ChatMessage.objects.visible_for_user(request.user)
            .filter(thread=thread)
            .select_related("sender")
            .prefetch_related("attachments")
        )
        if boundary:
            qs = qs.filter(updated_at__gte=boundary)
        for message in qs:
            if boundary is None or message.sent_at >= boundary:
                events.append({"type": "message", "payload": ChatMessageSerializer(message).data})
            elif message.status != ChatMessage.STATUS_SENT and message.updated_at >= (boundary or message.updated_at):
                events.append(
                    {
                        "type": "status",
                        "payload": {
                            "id": message.id,
                            "status": message.status,
                            "delivered_at": message.delivered_at,
                            "read_at": message.read_at,
                        },
                    }
                )
        return Response({"events": events, "next_cursor": timezone.now().isoformat()})


class ChatAttachmentUploadView(ContractThreadMixin, generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ChatAttachmentUploadSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["thread"] = self.get_thread()
        return context


class ChatAttachmentPresignView(ContractThreadMixin, APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        thread = self.get_thread()
        try:
            attachment = thread.attachments.get(pk=kwargs["attachment_id"], uploaded_by=request.user)
        except Exception as exc:
            raise Http404 from exc
        serializer = ChatAttachmentPresignSerializer(
            data=request.data or {},
            context={"attachment": attachment, "request": request},
        )
        serializer.is_valid(raise_exception=True)
        data = serializer.save()
        return Response(data, status=status.HTTP_201_CREATED)


class ChatAttachmentDownloadView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        token = request.query_params.get("token")
        if not token:
            raise Http404
        try:
            link = ChatAttachmentLink.objects.select_related("attachment", "attachment__thread").get(
                attachment_id=kwargs["attachment_id"],
                token=token,
            )
        except ChatAttachmentLink.DoesNotExist as exc:
            raise Http404 from exc
        if not link.is_valid():
            raise Http404
        attachment = link.attachment
        if not attachment.thread.is_participant(request.user):
            raise PermissionDenied("Недостаточно прав для скачивания вложения")
        response = FileResponse(
            attachment.file.open("rb"),
            as_attachment=True,
            filename=attachment.original_name,
        )
        response["Content-Type"] = attachment.mime_type
        response["X-Content-Type-Options"] = "nosniff"
        return response


class ChatMessageReportView(ContractThreadMixin, generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ChatMessageReportSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        thread = self.get_thread()
        try:
            message = thread.messages.get(pk=self.kwargs["message_id"])
        except ChatMessage.DoesNotExist as exc:
            raise Http404 from exc
        context["message"] = message
        return context
