from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel, Field

from ..services.summarizer import TldrSummarizer

router = APIRouter(prefix="/summaries")
summarizer = TldrSummarizer()


class TldrItem(BaseModel):
    id: int
    type: str = Field(pattern="^(order|profile)$")
    title: str
    body: str
    locale: str | None = None


class SummariesRequest(BaseModel):
    locale: str = "ru"
    items: list[TldrItem]


class SummariesResponse(BaseModel):
    items: list[dict]
    source: str = "ai"


@router.post("/tldr", response_model=SummariesResponse)
def generate_tldr(request: SummariesRequest) -> SummariesResponse:
    payload: list[dict] = []
    for item in request.items:
        locale = item.locale or request.locale
        payload.append(
            {
                "id": item.id,
                "type": item.type,
                "tldr": summarizer.summarize(
                    title=item.title,
                    body=item.body,
                    locale=locale,
                ),
            }
        )
    return SummariesResponse(items=payload, source="ai")
