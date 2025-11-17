from __future__ import annotations

from fastapi import FastAPI

from .routers import match, semantic_search, summaries

app = FastAPI(title="Obsidian AI Gateway", version="1.0.0")

app.include_router(match.router, tags=["match"])
app.include_router(semantic_search.router, tags=["semantic-search"])
app.include_router(summaries.router, tags=["summaries"])


@app.get("/health")
def healthcheck() -> dict[str, str]:  # pragma: no cover - trivial
    return {"status": "ok"}
