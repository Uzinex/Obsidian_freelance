"""Сбор данных и fallback для семантического поиска."""

from __future__ import annotations

from typing import Iterable

from django.db.models import Q

from accounts.models import Profile
from marketplace.models import Order
from obsidian_backend.ai.client import AiGatewayClient, AiGatewayError
from obsidian_backend.ai import tldr as tldr_cache
from profiles.models import PortfolioItem

_MAX_DOCS = 200


def _serialize_order(order: Order, locale: str) -> dict:
    return {
        "id": f"order:{order.id}",
        "title": order.title,
        "body": order.description,
        "tldr": tldr_cache.get_tldr(
            entity="order",
            pk=order.pk,
            locale=locale,
            fetcher=order.get_tldr,
        ),
        "metadata": {
            "budget": str(order.budget),
            "payment_type": order.payment_type,
            "skills": list(order.required_skills.values_list("slug", flat=True)),
        },
    }


def _serialize_profile(profile: Profile, locale: str) -> dict:
    return {
        "id": f"profile:{profile.id}",
        "title": profile.headline or profile.user.full_name,
        "body": profile.bio,
        "tldr": tldr_cache.get_tldr(
            entity="profile",
            pk=profile.pk,
            locale=locale,
            fetcher=profile.get_tldr,
        ),
        "metadata": {
            "skills": list(profile.skills.values_list("slug", flat=True)),
            "hourly_rate": str(profile.hourly_rate or ""),
            "location": profile.location,
        },
    }


def _serialize_portfolio(item: PortfolioItem) -> dict:
    return {
        "id": f"portfolio:{item.id}",
        "title": item.title,
        "body": "\n".join(filter(None, [item.problem, item.solution, item.result])),
        "tldr": None,
        "metadata": {"tags": item.tags, "status": item.status},
    }


def _load_documents(entity: str, locale: str) -> Iterable[dict]:
    if entity == "orders":
        queryset = (
            Order.objects.filter(status=Order.STATUS_PUBLISHED)
            .select_related("client", "client__user")
            .prefetch_related("required_skills")
            .order_by("-created_at")[:_MAX_DOCS]
        )
        return [_serialize_order(order, locale) for order in queryset]
    if entity == "profiles":
        queryset = (
            Profile.objects.filter(role=Profile.ROLE_FREELANCER, visibility=Profile.VISIBILITY_PUBLIC)
            .select_related("user")
            .prefetch_related("skills")
            .order_by("-updated_at")[:_MAX_DOCS]
        )
        return [_serialize_profile(profile, locale) for profile in queryset]
    queryset = (
        PortfolioItem.objects.filter(status=PortfolioItem.STATUS_PUBLISHED)
        .select_related("profile", "profile__user")
        .order_by("-created_at")[:_MAX_DOCS]
    )
    return [_serialize_portfolio(item) for item in queryset]


def _fallback_search(query: str, entity: str, locale: str) -> list[dict]:
    normalized = query.lower()
    results: list[dict] = []
    if entity == "orders":
        orders = Order.objects.filter(Q(title__icontains=normalized) | Q(description__icontains=normalized))[:20]
        for order in orders:
            results.append({
                "id": order.id,
                "score": 0.4,
                "snippet": order.description[:280],
            })
        return results
    if entity == "profiles":
        profiles = Profile.objects.filter(
            Q(headline__icontains=normalized) | Q(bio__icontains=normalized)
        )[:20]
        for profile in profiles:
            results.append({
                "id": profile.id,
                "score": 0.35,
                "snippet": profile.bio[:280],
            })
        return results
    items = PortfolioItem.objects.filter(
        Q(title__icontains=normalized) | Q(problem__icontains=normalized)
    )[:20]
    for item in items:
        results.append({"id": item.id, "score": 0.3, "snippet": item.problem[:280]})
    return results


def execute_semantic_search(*, query: str, entity: str, locale: str, limit: int) -> dict:
    documents = list(_load_documents(entity, locale))
    payload = {
        "query": query,
        "entity": entity,
        "locale": locale,
        "limit": min(limit, 50),
        "documents": documents,
    }
    client = AiGatewayClient()
    try:
        return client.semantic_search(payload)
    except AiGatewayError:
        return {
            "results": _fallback_search(query, entity, locale)[:limit],
            "source": "fallback",
        }
