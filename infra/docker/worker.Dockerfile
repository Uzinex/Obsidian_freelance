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
EXPOSE 8001
COPY infra/docker/scripts/health-celery.sh /bin/health-celery
RUN chmod +x /bin/health-celery
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s CMD /bin/health-celery
CMD ["/bin/sh", "-c", "celery -A obsidian_backend worker --loglevel=info"]
