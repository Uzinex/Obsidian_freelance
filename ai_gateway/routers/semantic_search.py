from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel, Field

from ..services.search import SemanticSearchService

router = APIRouter()
search_service = SemanticSearchService()


class SearchDocument(BaseModel):
    id: str
    title: str | None = None
    body: str | None = None
    tldr: str | None = None
    metadata: dict | None = None


class SemanticSearchRequest(BaseModel):
    query: str
    entity: str = Field(default="orders", pattern="^(orders|profiles|portfolio)$")
    locale: str = "ru"
    limit: int = Field(default=20, le=50)
    documents: list[SearchDocument] = Field(default_factory=list)


class SemanticSearchResponse(BaseModel):
    results: list[dict]
    fallback_triggered: bool | None = None
    source: str = "ai"


@router.post("/semantic_search", response_model=SemanticSearchResponse)
def semantic_search(request: SemanticSearchRequest) -> SemanticSearchResponse:
    payload = search_service.search(
        query=request.query,
        documents=[doc.model_dump() for doc in request.documents],
        limit=request.limit,
    )
    payload["source"] = "ai"
    return SemanticSearchResponse(**payload)
