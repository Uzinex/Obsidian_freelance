from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel, Field

from ..services.matcher import SmartMatcher

router = APIRouter()
matcher = SmartMatcher()


class HistoricalConversion(BaseModel):
    view_to_invite: float = 0
    invite_to_hire: float = 0


class MatchJob(BaseModel):
    id: int
    title: str
    description: str
    budget: float | None = None
    payment_type: str | None = None
    order_type: str | None = None
    skills: list[str] = Field(default_factory=list)
    tldr: str | None = None


class ProfileCandidate(BaseModel):
    id: int
    slug: str | None = None
    skills: list[str] = Field(default_factory=list)
    hourly_rate: float | None = None
    min_budget: float | None = None
    availability: str | None = None
    location: dict | None = None
    languages: list[str] = Field(default_factory=list)
    profile_score: float = 0.0
    historical_conversion: HistoricalConversion = Field(default_factory=HistoricalConversion)
    escrow_share: float = 0.0
    response_time_minutes: float | None = None
    tldr: str | None = None


class MatchRequest(BaseModel):
    job: MatchJob | None = None
    profiles: list[ProfileCandidate] = Field(default_factory=list)
    freelancer: ProfileCandidate | None = None
    orders: list[MatchJob] = Field(default_factory=list)
    locale: str = "ru"


class RankedResponse(BaseModel):
    identifier: int
    score: float
    rationale: list[str]


class MatchResponse(BaseModel):
    invite_recommendations: list[RankedResponse]
    order_recommendations: list[RankedResponse]
    audit: dict
    source: str


@router.post("/match", response_model=MatchResponse)
def match_endpoint(request: MatchRequest) -> MatchResponse:
    payload = matcher.match(request.model_dump())
    return MatchResponse(**payload)
