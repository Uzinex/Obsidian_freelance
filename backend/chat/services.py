from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Iterable, Sequence

from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import UploadedFile
from django.db import transaction
from django.utils import timezone

from accounts import rbac
from marketplace.models import Contract
from uploads.scanner import scan_bytes
from uploads.validators import detect_mime_type, scrub_exif_if_image

from moderation.services import apply_red_flag_detection, enforce_chat_safety

from .exceptions import ChatBlockedError, ChatRateLimitError
from .models import ChatAttachment, ChatMessage, ChatThread, profile_id_matches, _LINK_PATTERN

CHAT_ATTACHMENT_MAX_BYTES = 15 * 1024 * 1024
CHAT_ATTACHMENT_ALLOWED_MIME_TYPES = {
    "image/jpeg",
    "image/png",
    "application/pdf",
    "application/zip",
}

QUICK_ACTIONS = {
    "propose_milestone": "Предложить milestone",
    "request_revision": "Запросить правки",
    "open_dispute": "Открыть спор",
}


@dataclass(frozen=True)
class AttachmentUploadResult:
    attachment: ChatAttachment
    sanitized_bytes: bytes


def _ensure_participant(user, thread: ChatThread) -> None:
    if getattr(user, "is_staff", False) or getattr(user, "is_superuser", False):
        return
    profile = getattr(user, "profile", None)
    if profile and profile_id_matches(profile_id=profile.id, thread=thread):
        return
    if rbac.user_has_role(user, rbac.Role.MODERATOR):
        return
    raise PermissionDenied("Доступ к чату контракта ограничен участниками и модераторами")


def _thread_from_contract(contract: Contract) -> ChatThread:
    thread, _ = ChatThread.objects.get_or_create(
        contract=contract,
        defaults={
            "client": contract.client,
            "freelancer": contract.freelancer,
            "last_message_at": timezone.now(),
        },
    )
    # Contract participants could change when a profile is re-linked. Keep the
    # thread in sync to avoid orphaned conversations.
    dirty_fields: list[str] = []
    if thread.client_id != contract.client_id:
        thread.client = contract.client
        dirty_fields.append("client")
    if thread.freelancer_id != contract.freelancer_id:
        thread.freelancer = contract.freelancer
        dirty_fields.append("freelancer")
    if dirty_fields:
        thread.save(update_fields=dirty_fields)
    return thread


def get_thread_for_user(*, contract_id: int, user) -> ChatThread:
    contract = Contract.objects.select_related("client", "freelancer").get(pk=contract_id)
    thread = _thread_from_contract(contract)
    _ensure_participant(user, thread)
    return thread


def enforce_message_rate_limits(*, user_id: int, thread_id: int) -> None:
    now = timezone.now()
    limits = [
        (settings.CHAT_RATE_LIMIT_USER_PER_SECOND, 1, f"chat:user:{user_id}:sec"),
        (settings.CHAT_RATE_LIMIT_USER_PER_MINUTE, 60, f"chat:user:{user_id}:min"),
        (settings.CHAT_RATE_LIMIT_THREAD_PER_SECOND, 1, f"chat:thread:{thread_id}:sec"),
        (settings.CHAT_RATE_LIMIT_THREAD_PER_MINUTE, 60, f"chat:thread:{thread_id}:min"),
    ]
    for limit, window, cache_key in limits:
        if not limit:
            continue
        count = cache.get(cache_key, 0)
        if count >= limit:
            raise ChatRateLimitError(
                "Превышен лимит отправки сообщений, повторите попытку чуть позже"
            )
        cache.set(cache_key, count + 1, timeout=window)
    # Track last activity to mitigate flood storms on reconnect.
    cache.set(f"chat:last:{thread_id}:{user_id}", now.isoformat(), timeout=300)


def _ensure_thread_not_blocked(thread: ChatThread) -> None:
    if thread.is_blocked():
        raise ChatBlockedError(thread.blocked_reason or "Отправка сообщений временно недоступна")


@transaction.atomic
def create_message(
    *,
    thread: ChatThread,
    sender,
    body: str,
    attachment_ids: Sequence[str] | None = None,
    action: str | None = None,
) -> ChatMessage:
    _ensure_thread_not_blocked(thread)
    enforce_message_rate_limits(user_id=sender.id, thread_id=thread.id)
    if action and action not in QUICK_ACTIONS:
        raise ValidationError("Неизвестное контекстное действие")
    normalized_body = (body or QUICK_ACTIONS.get(action, "")).strip()
    attachments_query = ChatAttachment.objects.filter(
        thread=thread,
        uploaded_by=sender,
        message__isnull=True,
    )
    if attachment_ids:
        attachments_query = attachments_query.filter(id__in=attachment_ids)
    attachments = list(attachments_query)
    if not normalized_body and not attachments:
        raise ValidationError("Нельзя отправить пустое сообщение")
    contains_link = bool(_LINK_PATTERN.search(normalized_body)) if normalized_body else False
    shadow_ban = enforce_chat_safety(thread=thread, sender=sender)
    message = ChatMessage.objects.create(
        thread=thread,
        sender=sender,
        body=normalized_body,
        has_attachments=bool(attachments),
        contains_link=contains_link,
        action=action or "",
        is_shadow_blocked=shadow_ban,
    )
    for attachment in attachments:
        attachment.attach_to_message(message)
    thread.last_message_at = message.sent_at
    thread.save(update_fields=["last_message_at", "updated_at"])
    apply_red_flag_detection(message)
    return message


def store_attachment(
    *,
    thread: ChatThread,
    uploaded_by,
    file_obj: UploadedFile,
) -> ChatAttachment:
    if not settings.CHAT_ATTACHMENTS_ENABLED:
        raise ValidationError("Отправка вложений временно недоступна")
    raw = file_obj.read()
    if len(raw) > CHAT_ATTACHMENT_MAX_BYTES:
        raise ValidationError("Вложение превышает максимальный размер 15 МБ")
    mime_type = detect_mime_type(raw)
    if mime_type not in CHAT_ATTACHMENT_ALLOWED_MIME_TYPES:
        raise ValidationError("Этот тип файла запрещён в чате")
    scrubbed = scrub_exif_if_image(raw, mime_type)
    if len(scrubbed) > CHAT_ATTACHMENT_MAX_BYTES:
        raise ValidationError("Вложение превышает максимальный размер после обработки")
    scan_bytes(scrubbed, filename=file_obj.name)
    checksum = hashlib.sha256(scrubbed).hexdigest()
    attachment = ChatAttachment.objects.create(
        thread=thread,
        uploaded_by=uploaded_by,
        original_name=file_obj.name,
        mime_type=mime_type,
        size=len(scrubbed),
        checksum=checksum,
    )
    content = ContentFile(scrubbed, name=file_obj.name)
    attachment.file.save(file_obj.name, content, save=True)
    attachment.mark_scanned()
    return attachment


__all__ = [
    "AttachmentUploadResult",
    "ChatAttachment",
    "ChatMessage",
    "ChatThread",
    "QUICK_ACTIONS",
    "create_message",
    "enforce_message_rate_limits",
    "get_thread_for_user",
    "store_attachment",
]
