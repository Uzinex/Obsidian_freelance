from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, time, timedelta, timezone as dt_timezone
from typing import Mapping, Sequence
from zoneinfo import ZoneInfo

from django.db import transaction
from django.utils import timezone

from obsidian_backend.feature_flags import is_feature_enabled

from .models import (
    NotificationDelivery,
    NotificationDigest,
    NotificationEvent,
    NotificationPreference,
)
from .emails import render_transactional_email
from .formatting import normalize_locale
from .webpush import render_webpush_payload

DEFAULT_CHANNELS: tuple[str, ...] = (
    NotificationDelivery.CHANNEL_IN_APP,
    NotificationDelivery.CHANNEL_EMAIL,
)

QUIET_HOURS_DEFAULT = (time(hour=22, minute=0), time(hour=8, minute=0))
DIGEST_WINDOWS = {
    NotificationPreference.FREQUENCY_DIGEST_15M: timedelta(minutes=15),
    NotificationPreference.FREQUENCY_HOURLY: timedelta(hours=1),
    NotificationPreference.FREQUENCY_DAILY: timedelta(days=1),
}


@dataclass
class EmittedNotification:
    event: NotificationEvent
    deliveries: list[NotificationDelivery]


class NotificationHub:
    """Centralized entry point for generating and routing events."""

    def emit(
        self,
        *,
        recipient,
        title: str,
        body: str,
        category: str,
        event_type: str,
        actor=None,
        profile=None,
        data: Mapping | None = None,
        channels: Sequence[str] | None = None,
        priority: str | None = None,
        dedupe_key: str | None = None,
        throttle_for: timedelta | None = None,
        digest_window: timedelta | None = None,
    ) -> EmittedNotification:
        now = timezone.now()
        selected_channels = self._resolve_channels(channels)
        throttle_for = throttle_for or timedelta(minutes=5)
        dedupe_key = dedupe_key or self._build_dedupe_key(
            event_type=event_type,
            recipient_id=getattr(recipient, "id", None),
            data=data,
        )
        with transaction.atomic():
            existing = self._should_throttle(recipient, dedupe_key, now)
            if existing:
                delivery = NotificationDelivery(
                    event=existing,
                    channel=NotificationDelivery.CHANNEL_IN_APP,
                    status=NotificationDelivery.STATUS_THROTTLED,
                    metadata={"detail": "duplicate suppressed"},
                )
                delivery.save()
                return EmittedNotification(existing, [delivery])

            event = NotificationEvent.objects.create(
                recipient=recipient,
                profile=profile,
                actor=actor,
                category=category,
                event_type=event_type,
                title=title,
                body=body,
                data=dict(data or {}),
                priority=priority or NotificationEvent.Priority.MEDIUM,
                dedupe_key=dedupe_key,
                throttle_until=now + throttle_for,
                digest_window=digest_window,
            )

            deliveries: list[NotificationDelivery] = []
            for channel in selected_channels:
                deliveries.append(
                    self._route_delivery(
                        event=event,
                        channel=channel,
                        requested_at=now,
                        digest_window=digest_window,
                    )
                )
        return EmittedNotification(event, deliveries)

    # Core helpers ---------------------------------------------------------

    def _resolve_channels(self, channels: Sequence[str] | None) -> list[str]:
        resolved = list(channels or DEFAULT_CHANNELS)
        if (
            NotificationDelivery.CHANNEL_WEB_PUSH in resolved
            and not is_feature_enabled("notify.webpush")
        ):
            resolved.remove(NotificationDelivery.CHANNEL_WEB_PUSH)
        return resolved

    def _build_dedupe_key(self, *, event_type: str, recipient_id: int | None, data: Mapping | None) -> str:
        suffix = ""
        if data:
            if "contract_id" in data:
                suffix = f"contract:{data['contract_id']}"
            elif "case_id" in data:
                suffix = f"case:{data['case_id']}"
            elif "thread_id" in data:
                suffix = f"thread:{data['thread_id']}"
        return f"{recipient_id}:{event_type}:{suffix}"

    def _should_throttle(self, recipient, dedupe_key: str, now: datetime):
        if not dedupe_key:
            return None
        existing = (
            NotificationEvent.objects.filter(
                recipient=recipient,
                dedupe_key=dedupe_key,
                throttle_until__gte=now,
            )
            .order_by("-created_at")
            .first()
        )
        return existing

    def _route_delivery(
        self,
        *,
        event: NotificationEvent,
        channel: str,
        requested_at: datetime,
        digest_window: timedelta | None,
    ) -> NotificationDelivery:
        pref = self._get_preference(event.recipient, event.category, channel)
        if not pref.enabled:
            return NotificationDelivery.objects.create(
                event=event,
                channel=channel,
                status=NotificationDelivery.STATUS_SUPPRESSED,
                metadata={"detail": "channel disabled by user"},
            )

        if channel != NotificationDelivery.CHANNEL_IN_APP:
            if pref.frequency != NotificationPreference.FREQUENCY_IMMEDIATE:
                digest = self._attach_to_digest(
                    event=event,
                    channel=channel,
                    pref=pref,
                    requested_at=requested_at,
                    custom_window=digest_window,
                )
                return NotificationDelivery.objects.create(
                    event=event,
                    channel=channel,
                    status=NotificationDelivery.STATUS_DIGESTED,
                    digest=digest,
                    metadata={"digest_id": digest.id},
                )

            schedule_at = self._respect_quiet_hours(pref, requested_at)
            if schedule_at and schedule_at > requested_at:
                return NotificationDelivery.objects.create(
                    event=event,
                    channel=channel,
                    status=NotificationDelivery.STATUS_SCHEDULED,
                    scheduled_for=schedule_at,
                )

        # In-app is immediate delivery.
        return NotificationDelivery.objects.create(
            event=event,
            channel=channel,
            status=NotificationDelivery.STATUS_SENT
            if channel == NotificationDelivery.CHANNEL_IN_APP
            else NotificationDelivery.STATUS_PENDING,
            sent_at=timezone.now()
            if channel == NotificationDelivery.CHANNEL_IN_APP
            else None,
        )

    def _respect_quiet_hours(
        self,
        pref: NotificationPreference,
        requested_at: datetime,
    ) -> datetime | None:
        start = pref.quiet_hours_start or QUIET_HOURS_DEFAULT[0]
        end = pref.quiet_hours_end or QUIET_HOURS_DEFAULT[1]
        tz = ZoneInfo(pref.timezone or "Asia/Tashkent")
        local_dt = requested_at.astimezone(tz)
        now_time = local_dt.time()
        quiet = False
        if start < end:
            quiet = start <= now_time < end
        else:  # overnight quiet hours
            quiet = now_time >= start or now_time < end
        if quiet:
            target_date = local_dt
            if start < end:
                target_date = target_date.replace(
                    hour=end.hour,
                    minute=end.minute,
                    second=0,
                    microsecond=0,
                )
            else:
                target_date = target_date.replace(
                    hour=end.hour,
                    minute=end.minute,
                    second=0,
                    microsecond=0,
                )
                target_date += timedelta(days=1)
            return target_date.astimezone(dt_timezone.utc)
        return None

    def _attach_to_digest(
        self,
        *,
        event: NotificationEvent,
        channel: str,
        pref: NotificationPreference,
        requested_at: datetime,
        custom_window: timedelta | None,
    ) -> NotificationDigest:
        window = custom_window or DIGEST_WINDOWS.get(pref.frequency)
        if not window:
            window = timedelta(minutes=15)
        tz = ZoneInfo(pref.timezone or "Asia/Tashkent")
        local_dt = requested_at.astimezone(tz)
        if window >= timedelta(days=1):
            period_start = local_dt.replace(
                hour=pref.daily_digest_hour,
                minute=0,
                second=0,
                microsecond=0,
            )
            if period_start > local_dt:
                period_start -= timedelta(days=1)
            period_end = period_start + timedelta(days=1)
        else:
            step_minutes = max(1, int(window.total_seconds() // 60))
            bucket = (local_dt.minute // step_minutes) * step_minutes
            period_start = local_dt.replace(
                minute=bucket,
                second=0,
                microsecond=0,
            )
            period_end = period_start + window
        period_start = period_start.astimezone(dt_timezone.utc)
        period_end = period_end.astimezone(dt_timezone.utc)
        digest, _ = NotificationDigest.objects.get_or_create(
            user=event.recipient,
            channel=channel,
            category=event.category,
            period_start=period_start,
            period_end=period_end,
            defaults={
                "title": f"{event.profile or event.recipient} digest",
                "summary": {},
                "scheduled_for": period_end,
            },
        )
        digest.events.add(event)
        summary = digest.summary or {}
        summary.setdefault("events", 0)
        summary["events"] += 1
        digest.summary = summary
        digest.status = NotificationDigest.STATUS_SCHEDULED
        digest.save(update_fields=["summary", "status", "scheduled_for"])
        return digest

    def _get_preference(self, user, category: str, channel: str) -> NotificationPreference:
        pref, _ = NotificationPreference.objects.get_or_create(
            user=user,
            category=category,
            channel=channel,
            defaults={
                "enabled": True,
                "frequency": NotificationPreference.FREQUENCY_IMMEDIATE,
                "language": getattr(user, "locale", "ru"),
            },
        )
        return pref

    # Digest processing ----------------------------------------------------

    def flush_due_digests(self, *, now: datetime | None = None) -> list[NotificationDigest]:
        now = now or timezone.now()
        due = NotificationDigest.objects.filter(
            status__in=[
                NotificationDigest.STATUS_PENDING,
                NotificationDigest.STATUS_SCHEDULED,
            ],
            scheduled_for__lte=now,
        ).select_related("user")
        processed: list[NotificationDigest] = []
        for digest in due:
            events = list(digest.events.all())
            if not events:
                digest.status = NotificationDigest.STATUS_CANCELLED
                digest.save(update_fields=["status"])
                continue
            body = self._render_digest_body(digest, events)
            event = NotificationEvent.objects.create(
                recipient=digest.user,
                category=digest.category,
                event_type=NotificationEvent.EventType.CHAT_NEW_MESSAGE
                if digest.category == NotificationEvent.CATEGORY_CHAT
                else NotificationEvent.EventType.ACCOUNT_GENERIC,
                title=digest.title or "Сводка уведомлений",
                body=body,
                data={"digest_id": digest.id, "events": [e.id for e in events]},
                is_digest=True,
            )
            NotificationDelivery.objects.create(
                event=event,
                channel=digest.channel,
                status=NotificationDelivery.STATUS_SENT,
                sent_at=now,
                digest=digest,
            )
            digest.status = NotificationDigest.STATUS_SENT
            digest.sent_at = now
            digest.save(update_fields=["status", "sent_at"])
            processed.append(digest)
        return processed

    def _render_digest_body(
        self,
        digest: NotificationDigest,
        events: Sequence[NotificationEvent],
    ) -> str:
        lines = [
            f"Всего событий: {len(events)}",
        ]
        for event in events[:10]:
            lines.append(f"• {event.title}: {event.body[:120]}")
        if len(events) > 10:
            lines.append("… и другие события")
        return "\n".join(lines)

    # Delivery dispatch ---------------------------------------------------

    def dispatch_pending_deliveries(self) -> int:
        pending = NotificationDelivery.objects.filter(
            status=NotificationDelivery.STATUS_PENDING,
        ).select_related("event", "event__recipient")
        processed = 0
        for delivery in pending:
            if delivery.channel == NotificationDelivery.CHANNEL_EMAIL:
                self._send_email_delivery(delivery)
                processed += 1
            elif delivery.channel == NotificationDelivery.CHANNEL_WEB_PUSH:
                self._send_webpush_delivery(delivery)
                processed += 1
        return processed

    def _send_email_delivery(self, delivery: NotificationDelivery) -> None:
        event = delivery.event
        locale = self._resolve_delivery_locale(delivery)
        payload = render_transactional_email(
            event.event_type,
            {
                **event.data,
                "email": getattr(event.recipient, "email", ""),
                "title": event.title,
                "body": event.body,
            },
            locale=locale,
        )
        delivery.metadata = {
            "subject": payload.subject,
            "body": payload.body,
            "recipient": payload.recipient,
            "headers": payload.headers,
            "locale": locale,
        }
        delivery.status = NotificationDelivery.STATUS_SENT
        delivery.sent_at = timezone.now()
        delivery.save(update_fields=["metadata", "status", "sent_at"])

    def _send_webpush_delivery(self, delivery: NotificationDelivery) -> None:
        event = delivery.event
        locale = self._resolve_delivery_locale(delivery)
        payload = render_webpush_payload(
            event.event_type,
            {
                **event.data,
                "title": event.title,
                "body": event.body,
            },
            locale=locale,
        )
        delivery.metadata = {
            "title": payload.title,
            "body": payload.body,
            "url": payload.url,
            "locale": locale,
        }
        delivery.status = NotificationDelivery.STATUS_SENT
        delivery.sent_at = timezone.now()
        delivery.save(update_fields=["metadata", "status", "sent_at"])

    def _resolve_delivery_locale(self, delivery: NotificationDelivery) -> str:
        event = delivery.event
        candidate = event.data.get("locale") or event.data.get("language")
        if candidate:
            return normalize_locale(candidate)
        pref = (
            NotificationPreference.objects.filter(
                user=event.recipient,
                category=event.category,
                channel=delivery.channel,
            )
            .only("language")
            .first()
        )
        if pref:
            return normalize_locale(pref.language)
        return normalize_locale(None)


notification_hub = NotificationHub()
