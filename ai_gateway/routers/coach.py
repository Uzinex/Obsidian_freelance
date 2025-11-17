from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter(prefix="/coach")


class FreelancerProfile(BaseModel):
    name: str | None = None
    skills: list[str] = Field(default_factory=list)
    hourly_rate: float | None = Field(default=None, ge=0)
    currency: str = "USD"
    availability: str | None = None
    portfolio_links: list[str] = Field(default_factory=list)


class CoachRequest(BaseModel):
    task_id: str
    task_description: str
    key_requirements: list[str] = Field(default_factory=list)
    freelancer_profile: FreelancerProfile


class RangeField(BaseModel):
    min: float
    max: float
    units: str


class DraftResponse(BaseModel):
    id: int
    text: str
    price: float
    eta_days: int
    price_eta_rationale: str
    confidence: float = Field(ge=0.0, le=1.0)
    flags: list[str] = Field(default_factory=list)


class CoachResponse(BaseModel):
    task_id: str
    disclaimer: str
    auto_send_allowed: bool = False
    price_range: RangeField
    eta_range: RangeField
    drafts: list[DraftResponse]
    checklist: list[str]
    portfolio_slots: list[str]
    requires_manual_review: bool


def _estimate_price_and_eta(request: CoachRequest) -> tuple[float, int]:
    base_rate = request.freelancer_profile.hourly_rate or 35.0
    complexity_factor = max(1.0, len(request.key_requirements) / 3.0)
    price = round(base_rate * 8 * complexity_factor, 2)
    eta_days = max(2, int(round(complexity_factor * 3)))
    return price, eta_days


def _build_draft_text(idx: int, request: CoachRequest, price: float, eta_days: int) -> str:
    intro = "Это черновик, отредактируйте перед отправкой."
    summary = request.task_description.strip()
    skills = ", ".join(request.freelancer_profile.skills[:3]) or "указанные навыки"
    emphasis = "Вариант" if idx == 1 else ("Фокус на сроках" if idx == 2 else "Фокус на рисках")
    return (
        f"{intro}\n\n{emphasis}: готов закрыть задачу, опираясь на опыт в {skills}. "
        f"Оцениваю бюджет около {price} {request.freelancer_profile.currency} при сроке {eta_days} дн."
        f"\n\nКратко о задаче: {summary}\n\nПеред отправкой добавьте детали портфолио и тон общения."
    )


def _confidence(request: CoachRequest) -> float:
    skill_score = min(1.0, len(request.freelancer_profile.skills) / 5)
    portfolio_bonus = 0.1 if request.freelancer_profile.portfolio_links else 0.0
    return round(0.5 + skill_score * 0.4 + portfolio_bonus, 2)


@router.post("/drafts", response_model=CoachResponse)
def generate_coach_drafts(request: CoachRequest) -> CoachResponse:
    price, eta_days = _estimate_price_and_eta(request)
    price_range = RangeField(min=price * 0.9, max=price * 1.2, units=request.freelancer_profile.currency)
    eta_range = RangeField(min=max(1, eta_days - 1), max=eta_days + 3, units="days")

    drafts: list[DraftResponse] = []
    confidence = _confidence(request)
    flags = ["needs_manual_review"] if confidence < 0.7 else []

    for idx in range(1, 4):
        adjusted_price = round(price * (1 + (idx - 2) * 0.05), 2)
        adjusted_eta = max(1, eta_days + idx - 2)
        drafts.append(
            DraftResponse(
                id=idx,
                text=_build_draft_text(idx, request, adjusted_price, adjusted_eta),
                price=adjusted_price,
                eta_days=adjusted_eta,
                price_eta_rationale=(
                    "Оценка основана на сопоставлении требований и релевантных навыков исполнителя"
                ),
                confidence=max(0.0, min(1.0, confidence - 0.05 * abs(idx - 2))),
                flags=flags if idx == 1 else [],
            )
        )

    checklist = [
        "Подтвердить формат результатов и критерии приёмки",
        "Уточнить доступ к данным/сервисам",
        "Согласовать частоту апдейтов и контрольные точки",
    ]
    if not request.freelancer_profile.portfolio_links:
        checklist.append("Добавить ссылки на релевантные работы")

    return CoachResponse(
        task_id=request.task_id,
        disclaimer="Это черновик, отредактируйте перед отправкой",
        auto_send_allowed=False,
        price_range=price_range,
        eta_range=eta_range,
        drafts=drafts,
        checklist=checklist,
        portfolio_slots=request.freelancer_profile.portfolio_links[:2],
        requires_manual_review=confidence < 0.7,
    )
