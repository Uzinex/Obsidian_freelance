"""Подготовка данных для smart-matching и fallback-алгоритм."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
from typing import Iterable

from django.db.models import Prefetch, Q

from accounts.models import Profile
from marketplace.models import Order
from obsidian_backend.ai.client import AiGatewayClient, AiGatewayError
from profiles.models import ProfileStats

_MATCH_LIMIT = 200


@dataclass(slots=True)
class RankedItem:
    identifier: int
    score: float
    rationale: list[str]


def _safe_ratio(numerator: float | int, denominator: float | int) -> float:
    if not denominator:
        return 0.0
    return float(numerator) / float(denominator)


def _profile_score(profile: Profile, stats: ProfileStats | None) -> float:
    score = 0.4 if profile.is_verified else 0.2
    score += 0.3 if profile.avatar else 0
    score += 0.1 if profile.last_activity_at else 0
    if stats is not None:
        score += float(stats.completion_rate) / 100 * 0.2
        score += (1 - float(stats.dispute_rate) / 100) * 0.1
    return round(min(score, 1.0), 4)


def _response_minutes(stats: ProfileStats | None) -> float:
    if stats is None or stats.response_time is None:
        return 60.0
    if isinstance(stats.response_time, timedelta):
        return stats.response_time.total_seconds() / 60
    return float(stats.response_time)


def _serialize_profile(profile: Profile, *, locale: str) -> dict:
    stats = getattr(profile, "stats", None)
    skill_slugs = list(profile.skills.values_list("slug", flat=True))
    badges = list(profile.badges.values_list("badge_type", flat=True))
    return {
        "id": profile.id,
        "slug": profile.slug,
        "skills": skill_slugs,
        "hourly_rate": float(profile.hourly_rate or 0),
        "min_budget": float(profile.min_budget or 0),
        "availability": profile.availability,
        "location": profile.location,
        "languages": profile.languages,
        "profile_score": _profile_score(profile, stats),
        "historical_conversion": {
            "view_to_invite": _safe_ratio(getattr(stats, "invites", 0), getattr(stats, "views", 0)),
            "invite_to_hire": float(getattr(stats, "hire_rate", 0)) / 100,
        },
        "escrow_share": float(getattr(stats, "escrow_share", 0)) / 100,
        "response_time_minutes": _response_minutes(stats),
        "tldr": profile.get_tldr(locale),
        "badges": badges,
    }


def _serialize_order(order: Order, *, locale: str) -> dict:
    return {
        "id": order.id,
        "title": order.title,
        "description": order.description,
        "budget": float(order.budget),
        "payment_type": order.payment_type,
        "order_type": order.order_type,
        "availability": getattr(order.client, "availability", None),
        "location": getattr(order.client, "location", {}),
        "skills": list(order.required_skills.values_list("slug", flat=True)),
        "tldr": order.get_tldr(locale),
    }


def _collect_profiles(order: Order) -> Iterable[Profile]:
    base_queryset = (
        Profile.objects.filter(
            role=Profile.ROLE_FREELANCER,
            is_completed=True,
            visibility=Profile.VISIBILITY_PUBLIC,
        )
        .select_related("user")
        .prefetch_related(
            "skills",
            "badges",
            Prefetch("stats", ProfileStats.objects.all()),
        )
    )
    if order.required_skills.exists():
        base_queryset = base_queryset.filter(skills__in=order.required_skills.all())
    if order.client.country:
        base_queryset = base_queryset.filter(
            Q(country=order.client.country) | Q(location__country=order.client.country)
        )
    return base_queryset.distinct()[:_MATCH_LIMIT]


def _collect_orders(profile: Profile) -> Iterable[Order]:
    queryset = (
        Order.objects.filter(status=Order.STATUS_PUBLISHED)
        .select_related("client", "client__user")
        .prefetch_related("required_skills")
    )
    if profile.skills.exists():
        queryset = queryset.filter(required_skills__in=profile.skills.all())
    if profile.country:
        queryset = queryset.filter(
            Q(client__country=profile.country)
            | Q(client__location__country=profile.country)
            | Q(client__location__icontains=profile.country)
        )
    return queryset.distinct()[:_MATCH_LIMIT]


def _jaccard(a: set[str], b: set[str]) -> float:
    if not a and not b:
        return 0.0
    intersection = len(a & b)
    union = len(a | b)
    if union == 0:
        return 0.0
    return intersection / union


def _fallback_rank(order: Order, profiles: Iterable[Profile]) -> list[RankedItem]:
    order_skills = set(order.required_skills.values_list("slug", flat=True))
    ranked: list[RankedItem] = []
    for profile in profiles:
        stats = getattr(profile, "stats", None)
        skill_score = _jaccard(order_skills, set(profile.skills.values_list("slug", flat=True)))
        budget_penalty = 0.0
        if profile.hourly_rate and order.payment_type == Order.PAYMENT_HOURLY:
            budget_penalty = min(float(profile.hourly_rate) / float(order.budget or 1), 2)
        profile_score = _profile_score(profile, stats)
        score = skill_score * 0.5 + profile_score * 0.3 + (1 - min(budget_penalty, 1)) * 0.2
        rationale = [
            f"Навыки: {skill_score:.2f}",
            f"Профиль: {profile_score:.2f}",
            f"Бюджет: {1 - min(budget_penalty, 1):.2f}",
        ]
        ranked.append(
            RankedItem(
                identifier=profile.id,
                score=round(score, 4),
                rationale=rationale,
            )
        )
    ranked.sort(key=lambda item: item.score, reverse=True)
    return ranked[:20]


def _fallback_rank_orders(profile: Profile, orders: Iterable[Order]) -> list[RankedItem]:
    profile_skills = set(profile.skills.values_list("slug", flat=True))
    ranked: list[RankedItem] = []
    for order in orders:
        overlap = _jaccard(profile_skills, set(order.required_skills.values_list("slug", flat=True)))
        budget_alignment = 1.0
        if profile.hourly_rate and order.payment_type == Order.PAYMENT_HOURLY:
            budget_alignment = min(float(order.budget or 0) / float(profile.hourly_rate), 2)
        score = overlap * 0.6 + min(budget_alignment, 1) * 0.4
        ranked.append(
            RankedItem(
                identifier=order.id,
                score=round(score, 4),
                rationale=[
                    f"Навыки: {overlap:.2f}",
                    f"Ставка: {min(budget_alignment, 1):.2f}",
                ],
            )
        )
    ranked.sort(key=lambda item: item.score, reverse=True)
    return ranked[:20]


def build_match_payload(
    *, order: Order | None, profile: Profile | None, locale: str
) -> dict:
    profiles = list(_collect_profiles(order)) if order else []
    orders = list(_collect_orders(profile)) if profile else []
    return {
        "job": _serialize_order(order, locale=locale) if order else None,
        "profiles": [_serialize_profile(p, locale=locale) for p in profiles],
        "freelancer": _serialize_profile(profile, locale=locale) if profile else None,
        "orders": [_serialize_order(o, locale=locale) for o in orders],
        "locale": locale,
    }


def execute_match(*, order: Order | None, profile: Profile | None, locale: str) -> dict:
    payload = build_match_payload(order=order, profile=profile, locale=locale)
    client = AiGatewayClient()
    try:
        return client.match(payload)
    except AiGatewayError:
        fallback_profiles = list(_collect_profiles(order)) if order else []
        fallback_orders = list(_collect_orders(profile)) if profile else []
        return {
            "invite_recommendations": [
                item.__dict__
                for item in _fallback_rank(order, fallback_profiles)
            ]
            if order
            else [],
            "order_recommendations": [
                item.__dict__ for item in _fallback_rank_orders(profile, fallback_orders)
            ]
            if profile
            else [],
            "source": "fallback",
        }
