"""Настройки ai-gateway."""

from __future__ import annotations

import os
from functools import lru_cache
from typing import Literal

from pydantic import BaseModel, Field, PositiveFloat


class Settings(BaseModel):
    environment: Literal["dev", "stage", "prod"] = Field(
        default=os.getenv("AI_ENV", "dev").lower()
    )
    enable_rate_limit: bool = Field(default=os.getenv("AI_RATE_LIMIT", "1") == "1")
    timeout_match: PositiveFloat = Field(default=float(os.getenv("AI_TIMEOUT_MATCH", "1.2")))
    timeout_search: PositiveFloat = Field(default=float(os.getenv("AI_TIMEOUT_SEARCH", "0.9")))
    rank_weights: dict[str, float] = Field(
        default_factory=lambda: {
            "skill": 0.35,
            "profile": 0.2,
            "embedding": 0.2,
            "conversion": 0.1,
            "escrow": 0.05,
            "response": 0.05,
            "pricing": 0.05,
        }
    )
    fairness_clusters: list[str] = Field(
        default_factory=lambda: ["design", "development", "marketing", "translation"]
    )
    locale_defaults: list[str] = Field(default_factory=lambda: ["ru", "uz"])


@lru_cache
def get_settings() -> Settings:
    return Settings()
