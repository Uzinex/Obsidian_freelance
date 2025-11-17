from __future__ import annotations

from itertools import islice

from django.core.management.base import BaseCommand

from accounts.models import Profile
from marketplace.models import Order
from obsidian_backend.ai import tldr as tldr_cache
from obsidian_backend.ai.client import AiGatewayClient, AiGatewayError


class Command(BaseCommand):
    help = "Синхронное формирование TL;DR для заказов и профилей"

    def add_arguments(self, parser):
        parser.add_argument(
            "--entity",
            choices=["orders", "profiles", "all"],
            default="all",
        )
        parser.add_argument("--batch-size", type=int, default=32)
        parser.add_argument(
            "--locale",
            action="append",
            dest="locales",
            help="Языки, для которых пересчитываем TL;DR",
        )

    def handle(self, *args, **options):
        entity = options["entity"]
        batch_size = int(options["batch_size"])
        locales = options.get("locales") or ["ru", "uz"]
        client = AiGatewayClient(timeout=5)
        targets = []
        if entity in {"orders", "all"}:
            targets.append("orders")
        if entity in {"profiles", "all"}:
            targets.append("profiles")
        for locale in locales:
            for target in targets:
                self.stdout.write(f"Processing {target} ({locale})...")
                queryset = self._load_queryset(target, locale)
                chunk = list(islice(queryset, batch_size))
                while chunk:
                    payload = {
                        "locale": locale,
                        "items": [self._serialize_item(target, item, locale) for item in chunk],
                    }
                    try:
                        response = client.generate_tldr(payload)
                    except AiGatewayError as exc:  # pragma: no cover - network failure
                        self.stderr.write(str(exc))
                        break
                    self._persist(target, response.get("items", []), locale)
                    chunk = list(islice(queryset, batch_size))

    def _load_queryset(self, entity: str, locale: str):
        field = "tldr_ru" if locale.startswith("ru") else "tldr_uz"
        filters = {field: ""}
        if entity == "orders":
            return (
                Order.objects.filter(status=Order.STATUS_PUBLISHED, **filters)
                .select_related("client", "client__user")
                .prefetch_related("required_skills")
                .iterator()
            )
        return (
            Profile.objects.filter(role=Profile.ROLE_FREELANCER, **filters)
            .select_related("user")
            .prefetch_related("skills")
            .iterator()
        )

    def _serialize_item(self, entity: str, obj, locale: str) -> dict:
        if entity == "orders":
            return {
                "id": obj.id,
                "type": "order",
                "title": obj.title,
                "body": obj.description,
                "locale": locale,
            }
        return {
            "id": obj.id,
            "type": "profile",
            "title": obj.headline or obj.user.full_name,
            "body": obj.bio,
            "locale": locale,
        }

    def _persist(self, entity: str, items: list[dict], locale: str) -> None:
        for item in items:
            text = item.get("tldr")
            if not text:
                continue
            field = "ru" if locale.startswith("ru") else "uz"
            if entity == "orders":
                Order.objects.filter(pk=item["id"]).update(**{f"tldr_{field}": text})
                tldr_cache.set_tldr(entity="order", pk=item["id"], locale=locale, value=text)
            else:
                Profile.objects.filter(pk=item["id"]).update(**{f"tldr_{field}": text})
                tldr_cache.set_tldr(entity="profile", pk=item["id"], locale=locale, value=text)
