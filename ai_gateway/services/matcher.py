"""Сервис умного матчинга с прозрачным аудитом."""

from __future__ import annotations

import math
from collections import Counter
from dataclasses import dataclass
from typing import Any

from ..core.config import get_settings


@dataclass(slots=True)
class RankedRecommendation:
    identifier: int
    score: float
    rationale: list[str]


class FairnessAuditor:
    _sensitive_keys = {"gender", "sex", "age", "birth_year"}

    def __init__(self) -> None:
        self._settings = get_settings()

    def scrub(self, payload: dict[str, Any]) -> None:
        for key in list(payload.keys()):
            if key in self._sensitive_keys:
                payload.pop(key)

    def cluster_for(self, skills: list[str]) -> str:
        lowered = {skill.lower() for skill in skills}
        for cluster in self._settings.fairness_clusters:
            if any(cluster in skill for skill in lowered):
                return cluster
        return "other"

    def audit_distribution(self, ranked: list[RankedRecommendation], lookup: dict[int, dict]) -> dict:
        histogram = Counter()
        for item in ranked[:10]:
            candidate = lookup.get(item.identifier, {})
            cluster = self.cluster_for(candidate.get("skills", []))
            histogram[cluster] += 1
        total = sum(histogram.values()) or 1
        balance = {cluster: round(count / total, 3) for cluster, count in histogram.items()}
        return {
            "clusters": balance,
            "total_sampled": total,
        }


class SmartMatcher:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.auditor = FairnessAuditor()

    @staticmethod
    def _vectorize(text: str | None, *, dim: int = 32) -> list[float]:
        if not text:
            return [0.0] * dim
        tokens = text.lower().split()
        vector = [0.0] * dim
        for token in tokens:
            idx = hash(token) % dim
            vector[idx] += 1.0
        norm = math.sqrt(sum(value * value for value in vector)) or 1.0
        return [value / norm for value in vector]

    @staticmethod
    def _cosine(a: list[float], b: list[float]) -> float:
        return sum(x * y for x, y in zip(a, b))

    def _skill_score(self, job_skills: set[str], profile_skills: set[str]) -> float:
        if not job_skills and not profile_skills:
            return 0.0
        intersection = len(job_skills & profile_skills)
        union = len(job_skills | profile_skills) or 1
        return intersection / union

    def _pricing_score(self, job: dict | None, profile: dict) -> float:
        if not job or not job.get("budget"):
            return 0.5
        budget = float(job["budget"])
        hourly = float(profile.get("hourly_rate") or 0) or budget
        ratio = min(budget / max(hourly, 1), 2.0)
        return min(ratio, 1.0)

    def _response_score(self, profile: dict) -> float:
        minutes = float(profile.get("response_time_minutes") or 60)
        return max(0.0, 1 - min(minutes / 120, 1))

    def _conversion_score(self, profile: dict) -> float:
        stats = profile.get("historical_conversion") or {}
        view_to_invite = float(stats.get("view_to_invite", 0))
        invite_to_hire = float(stats.get("invite_to_hire", 0))
        return min((view_to_invite + invite_to_hire) / 2, 1.0)

    def _rank_profiles(self, job: dict | None, profiles: list[dict], locale: str) -> list[RankedRecommendation]:
        if not job:
            return []
        weights = self.settings.rank_weights
        job_skills = set(job.get("skills", []))
        job_vector = self._vectorize(job.get("description"))
        results: list[RankedRecommendation] = []
        lookup = {}
        for profile in profiles:
            self.auditor.scrub(profile)
            lookup[profile["id"]] = profile
            skill_score = self._skill_score(job_skills, set(profile.get("skills", [])))
            embedding_score = self._cosine(job_vector, self._vectorize(profile.get("tldr") or profile.get("slug")))
            pricing = self._pricing_score(job, profile)
            response = self._response_score(profile)
            conversion = self._conversion_score(profile)
            escrow = float(profile.get("escrow_share") or 0)
            profile_score = float(profile.get("profile_score") or 0)
            final_score = (
                weights["skill"] * skill_score
                + weights["embedding"] * embedding_score
                + weights["profile"] * profile_score
                + weights["conversion"] * conversion
                + weights["escrow"] * escrow
                + weights["response"] * response
                + weights["pricing"] * pricing
            )
            results.append(
                RankedRecommendation(
                    identifier=profile["id"],
                    score=round(final_score, 4),
                    rationale=[
                        f"skills:{skill_score:.2f}",
                        f"embedding:{embedding_score:.2f}",
                        f"profile:{profile_score:.2f}",
                        f"conversion:{conversion:.2f}",
                        f"escrow:{escrow:.2f}",
                        f"response:{response:.2f}",
                        f"pricing:{pricing:.2f}",
                    ],
                )
            )
        results.sort(key=lambda item: item.score, reverse=True)
        audit = self.auditor.audit_distribution(results, lookup)
        return results[:20], audit

    def _rank_orders(self, freelancer: dict | None, orders: list[dict]) -> list[RankedRecommendation]:
        if not freelancer:
            return []
        freel_skills = set(freelancer.get("skills", []))
        freelancer_vector = self._vectorize(freelancer.get("tldr") or freelancer.get("slug"))
        ranked: list[RankedRecommendation] = []
        for order in orders:
            skill_overlap = self._skill_score(freel_skills, set(order.get("skills", [])))
            embedding = self._cosine(freelancer_vector, self._vectorize(order.get("description")))
            pricing = self._pricing_score(order, freelancer)
            score = 0.5 * skill_overlap + 0.3 * embedding + 0.2 * pricing
            ranked.append(
                RankedRecommendation(
                    identifier=order["id"],
                    score=round(score, 4),
                    rationale=[
                        f"skills:{skill_overlap:.2f}",
                        f"embedding:{embedding:.2f}",
                        f"pricing:{pricing:.2f}",
                    ],
                )
            )
        ranked.sort(key=lambda item: item.score, reverse=True)
        return ranked[:20]

    def match(self, payload: dict[str, Any]) -> dict:
        locale = payload.get("locale", "ru")
        job = payload.get("job")
        profiles = payload.get("profiles", [])
        freelancer = payload.get("freelancer")
        orders = payload.get("orders", [])
        invite_ranked, audit = self._rank_profiles(job, profiles, locale) if job else ([], {})
        order_ranked = self._rank_orders(freelancer, orders)
        return {
            "invite_recommendations": [item.__dict__ for item in invite_ranked],
            "order_recommendations": [item.__dict__ for item in order_ranked],
            "audit": audit,
            "source": "ai",
        }
