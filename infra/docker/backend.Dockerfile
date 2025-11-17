# syntax=docker/dockerfile:1.6
FROM python:3.12-slim AS base
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 PIP_NO_CACHE_DIR=1
RUN addgroup --system app && adduser --system --ingroup app app

FROM base AS build
WORKDIR /app
COPY backend/pyproject.toml backend/requirements.txt ./
RUN apt-get update && apt-get install -y --no-install-recommends build-essential curl && rm -rf /var/lib/apt/lists/*
RUN python -m venv /opt/venv && . /opt/venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt

FROM base AS runtime
ENV PATH="/opt/venv/bin:$PATH"
WORKDIR /app
COPY --from=build /opt/venv /opt/venv
COPY backend /app
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/* \
    && chown -R app:app /app
USER app
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s CMD curl -f http://127.0.0.1:8000/healthz || exit 1
CMD ["uvicorn", "obsidian_backend.asgi:application", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
