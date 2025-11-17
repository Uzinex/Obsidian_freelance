"""Sample observability wiring for logging, metrics, and tracing."""
from __future__ import annotations

import json
import logging
import logging.config
import os
import socket
from typing import Any, Dict

try:  # pragma: no cover - optional dependency wiring
    from opentelemetry import trace
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
except ModuleNotFoundError:  # pragma: no cover - we only need the types when available
    trace = None  # type: ignore
    TracerProvider = None  # type: ignore
    BatchSpanProcessor = None  # type: ignore
    OTLPSpanExporter = None  # type: ignore

try:  # pragma: no cover - optional metrics dependency
    from prometheus_client import Counter, Gauge, Histogram, start_http_server
except ModuleNotFoundError:
    Counter = Gauge = Histogram = None  # type: ignore
    start_http_server = None  # type: ignore

LOGGER = logging.getLogger(__name__)


def _configure_structured_logging(service_name: str, environment: str) -> None:
    """Configure JSON logging with correlation IDs."""

    def _json_formatter(record: logging.LogRecord) -> str:
        payload: Dict[str, Any] = {
            "timestamp": record.created,
            "level": record.levelname,
            "logger": record.name,
            "service": service_name,
            "environment": environment,
            "message": record.getMessage(),
        }
        for attr in ("trace_id", "span_id", "sentry_event_id"):
            if hasattr(record, attr):
                payload[attr] = getattr(record, attr)
        if record.exc_info:
            payload["exc_info"] = logging.Formatter().formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)

    class JsonFormatter(logging.Formatter):
        def format(self, record: logging.LogRecord) -> str:  # noqa: D401
            return _json_formatter(record)

    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {"json": {"()": JsonFormatter}},
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "level": os.getenv("DJANGO_LOG_LEVEL", "INFO"),
                    "formatter": "json",
                }
            },
            "loggers": {
                "": {
                    "handlers": ["console"],
                    "level": os.getenv("DJANGO_LOG_LEVEL", "INFO"),
                }
            },
        }
    )


def _configure_tracing(service_name: str, environment: str) -> None:
    if trace is None or TracerProvider is None:  # pragma: no cover - optional
        LOGGER.debug("OpenTelemetry not installed; skipping tracing configuration")
        return

    resource = Resource.create(
        {
            "service.name": service_name,
            "service.namespace": "obsidian",
            "deployment.environment": environment,
            "host": socket.gethostname(),
        }
    )

    provider = TracerProvider(resource=resource)
    span_exporter = OTLPSpanExporter()
    provider.add_span_processor(BatchSpanProcessor(span_exporter))
    trace.set_tracer_provider(provider)


PROM_LATENCY = None
PROM_INFLIGHT = None
PROM_TASK_COUNTER = None


def _configure_metrics(port: int) -> None:
    global PROM_LATENCY, PROM_INFLIGHT, PROM_TASK_COUNTER

    if start_http_server is None:  # pragma: no cover - optional dependency
        LOGGER.debug("prometheus_client not installed; skipping metrics configuration")
        return

    start_http_server(port)
    PROM_LATENCY = Histogram(
        "obsidian_request_latency_seconds",
        "Request latency by endpoint",
        ["handler", "method"],
        buckets=(0.05, 0.1, 0.2, 0.5, 1, 3),
    )
    PROM_INFLIGHT = Gauge(
        "obsidian_inflight_requests", "In-flight requests", ["handler", "method"]
    )
    PROM_TASK_COUNTER = Counter(
        "obsidian_celery_tasks_total",
        "Celery tasks processed",
        ["queue", "status"],
    )


class PrometheusRequestMetricsMiddleware:
    """Sample middleware that records Prometheus metrics per request."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if PROM_LATENCY is None or PROM_INFLIGHT is None:
            return self.get_response(request)

        handler = request.resolver_match.view_name if request.resolver_match else "unknown"
        method = request.method
        PROM_INFLIGHT.labels(handler=handler, method=method).inc()
        with PROM_LATENCY.labels(handler=handler, method=method).time():
            try:
                response = self.get_response(request)
                if PROM_TASK_COUNTER is not None and hasattr(request, "celery_task_queue"):
                    PROM_TASK_COUNTER.labels(
                        queue=request.celery_task_queue, status=getattr(response, "status_code", 200)
                    ).inc()
                return response
            finally:
                PROM_INFLIGHT.labels(handler=handler, method=method).dec()


def configure_observability(service_name: str, environment: str, enable: bool = False) -> None:
    """Entry point used from settings.py to hook logging/metrics/tracing when needed."""

    if not enable:
        return

    LOGGER.info("Configuring observability stack for %s", service_name)
    _configure_structured_logging(service_name, environment)
    _configure_tracing(service_name, environment)
    metrics_port = int(os.getenv("PROMETHEUS_EXPORTER_PORT", "9464"))
    _configure_metrics(metrics_port)
