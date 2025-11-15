from __future__ import annotations

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.conf import settings
from django.core.exceptions import PermissionDenied

from marketplace.models import Contract

from .exceptions import ChatBlockedError, ChatRateLimitError
from .models import ChatMessage, ChatThread
from .serializers import ChatMessageSerializer
from .services import create_message, get_thread_for_user


class ContractChatConsumer(AsyncJsonWebsocketConsumer):
    thread_id: int | None = None

    async def connect(self):
        user = self.scope.get("user")
        if not user or not user.is_authenticated:
            await self.close(code=4401)
            return
        contract_id = self.scope["url_route"]["kwargs"].get("contract_id")
        try:
            thread = await database_sync_to_async(get_thread_for_user)(
                contract_id=contract_id,
                user=user,
            )
        except Contract.DoesNotExist:
            await self.close(code=4404)
            return
        except PermissionDenied:
            await self.close(code=4403)
            return
        self.thread_id = thread.id
        self.group_name = f"chat.thread.{thread.id}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        if settings.CHAT_PRESENCE_ENABLED:
            await self.channel_layer.group_send(
                self.group_name,
                {
                    "type": "chat.presence",
                    "user_id": user.id,
                    "status": "online",
                },
            )

    async def disconnect(self, code):
        user = self.scope.get("user")
        if self.thread_id:
            await self.channel_layer.group_discard(self.group_name, self.channel_name)
            if settings.CHAT_PRESENCE_ENABLED and user and user.is_authenticated:
                await self.channel_layer.group_send(
                    self.group_name,
                    {
                        "type": "chat.presence",
                        "user_id": user.id,
                        "status": "offline",
                    },
                )

    async def receive_json(self, content, **kwargs):
        action = content.get("action")
        if action == "send_message":
            await self._handle_send(content)
        elif action == "mark_delivered":
            await self._handle_status(content, ChatMessage.STATUS_DELIVERED)
        elif action == "mark_read":
            await self._handle_status(content, ChatMessage.STATUS_READ)
        elif action == "typing" and settings.CHAT_PRESENCE_ENABLED:
            await self.channel_layer.group_send(
                self.group_name,
                {
                    "type": "chat.typing",
                    "user_id": self.scope["user"].id,
                    "state": content.get("state", "typing"),
                },
            )
        else:  # pragma: no cover - unknown action fallback
            await self.send_json({"error": "unknown_action"})

    async def _handle_send(self, content):
        payload = content.get("payload") or content
        attachments = payload.get("attachments") or []
        body = payload.get("body", "")
        action_type = payload.get("action")
        try:
            message = await database_sync_to_async(self._create_message)(
                body=body,
                attachments=attachments,
                action=action_type,
            )
        except ChatRateLimitError as exc:
            await self.send_json({"type": "error", "code": "rate_limited", "detail": str(exc)})
            return
        except ChatBlockedError as exc:
            await self.send_json({"type": "error", "code": "blocked", "detail": str(exc)})
            return
        payload = await database_sync_to_async(self._serialize_message)(message)
        await self.channel_layer.group_send(
            self.group_name,
            {"type": "chat.message", "payload": payload},
        )

    async def _handle_status(self, content, status_value: str):
        message_id = content.get("message_id")
        if not message_id:
            return
        await database_sync_to_async(self._apply_status)(message_id, status_value)
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "chat.status",
                "payload": {
                    "id": message_id,
                    "status": status_value,
                },
            },
        )

    def _create_message(self, *, body: str, attachments: list[str], action: str | None):
        if not self.thread_id:
            raise PermissionDenied
        thread = ChatThread.objects.get(pk=self.thread_id)
        return create_message(
            thread=thread,
            sender=self.scope["user"],
            body=body,
            attachment_ids=attachments,
            action=action,
        )

    def _apply_status(self, message_id: int, status_value: str) -> None:
        if not self.thread_id:
            raise PermissionDenied
        try:
            message = ChatMessage.objects.get(pk=message_id, thread_id=self.thread_id)
        except ChatMessage.DoesNotExist:
            return
        message.apply_status(status_value)

    def _serialize_message(self, message: ChatMessage) -> dict:
        serializer = ChatMessageSerializer(message)
        return serializer.data

    async def chat_message(self, event):
        await self.send_json({"type": "message", "payload": event["payload"]})

    async def chat_status(self, event):
        await self.send_json({"type": "status", "payload": event["payload"]})

    async def chat_presence(self, event):
        await self.send_json({"type": "presence", "payload": event})

    async def chat_typing(self, event):
        await self.send_json({"type": "typing", "payload": event})
