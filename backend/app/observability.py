"""Correlated structured logging, Prometheus metrics and optional OTLP traces."""

from __future__ import annotations

import contextvars
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

from prometheus_client import Counter, Gauge, Histogram

from .config import Settings

trace_id_context: contextvars.ContextVar[str] = contextvars.ContextVar(
    "trace_id", default="unavailable"
)

VALIDATION_REQUESTS = Counter(
    "crvt_validation_requests_total",
    "Validation upload requests by outcome",
    ("outcome",),
)
VALIDATION_INCIDENT_ACTIVE = Gauge(
    "crvt_validation_incident_active",
    "Whether a real validation request has encountered the simulated incident",
)
HTTP_REQUESTS = Counter(
    "crvt_http_requests_total",
    "HTTP requests by method, normalized path and status",
    ("method", "path", "status"),
)
HTTP_DURATION = Histogram(
    "crvt_http_request_duration_seconds",
    "HTTP request duration by method and normalized path",
    ("method", "path"),
)


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "trace_id": getattr(record, "trace_id", None) or trace_id_context.get(),
        }
        for field in ("event", "method", "path", "status", "duration_ms", "validation_id", "outcome"):
            value = getattr(record, field, None)
            if value is not None:
                payload[field] = value
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, separators=(",", ":"), ensure_ascii=False)


def configure_logging(settings: Settings) -> logging.Logger:
    logger = logging.getLogger("crvt")
    logger.handlers.clear()
    logger.setLevel(settings.log_level)
    logger.propagate = False
    formatter = JsonFormatter()

    stream = logging.StreamHandler(sys.stdout)
    stream.setFormatter(formatter)
    logger.addHandler(stream)

    if settings.log_file:
        log_path = Path(settings.log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_path, encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    return logger


def configure_tracing(settings: Settings):
    """Configure OTLP only when an endpoint is supplied; otherwise use a no-op provider."""
    from opentelemetry import trace

    if settings.otlp_endpoint:
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor

        provider = TracerProvider(
            resource=Resource.create({"service.name": "crvt-backend"})
        )
        exporter = OTLPSpanExporter(endpoint=settings.otlp_endpoint.rstrip("/") + "/v1/traces")
        provider.add_span_processor(BatchSpanProcessor(exporter))
        trace.set_tracer_provider(provider)
    return trace.get_tracer("crvt.backend")


def current_otel_trace_id() -> str | None:
    from opentelemetry import trace

    context = trace.get_current_span().get_span_context()
    if context.is_valid:
        return format(context.trace_id, "032x")
    return None

