"""FastAPI application and REST contract."""

from __future__ import annotations

import logging
import secrets
import time
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import Depends, FastAPI, File, Header, HTTPException, Query, Request, UploadFile
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from opentelemetry.trace import Status, StatusCode
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from sqlalchemy import func, select, text
from sqlalchemy.orm import Session
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from .config import Settings, get_settings
from .database import Base, engine, get_db
from .models import OperationalState, ValidationRecord
from .observability import (
    HTTP_DURATION,
    HTTP_REQUESTS,
    VALIDATION_INCIDENT_ACTIVE,
    VALIDATION_REQUESTS,
    configure_logging,
    configure_tracing,
    current_otel_trace_id,
    trace_id_context,
)
from .schemas import (
    HealthResponse,
    IncidentStateResponse,
    ValidationList,
    ValidationResponse,
)
from .validation import InputValidationError, validate_csv

settings = get_settings()
logger = configure_logging(settings)
tracer = configure_tracing(settings)
INCIDENT_KEY = "validation_upload_failure"


class RequestBodyTooLarge(Exception):
    pass


class RequestBodyLimitMiddleware:
    """Bound actual request bytes before multipart parsing can spool an upload."""

    def __init__(self, app: ASGIApp, max_bytes: int) -> None:
        self.app = app
        self.max_bytes = max_bytes

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if (
            scope["type"] != "http"
            or scope.get("method") != "POST"
            or scope.get("path") != "/api/v1/validations"
        ):
            await self.app(scope, receive, send)
            return

        headers = {key.lower(): value for key, value in scope.get("headers", [])}
        raw_length = headers.get(b"content-length")
        if raw_length is not None:
            try:
                if int(raw_length) > self.max_bytes:
                    response = JSONResponse(
                        status_code=413,
                        content={"detail": {"code": "request_too_large", "message": "Upload request is too large"}},
                    )
                    await response(scope, receive, send)
                    return
            except ValueError:
                response = JSONResponse(status_code=400, content={"detail": "Invalid Content-Length"})
                await response(scope, receive, send)
                return

        received = 0

        async def limited_receive() -> Message:
            nonlocal received
            message = await receive()
            if message["type"] == "http.request":
                received += len(message.get("body", b""))
                if received > self.max_bytes:
                    raise RequestBodyTooLarge
            return message

        try:
            await self.app(scope, limited_receive, send)
        except RequestBodyTooLarge:
            response = JSONResponse(
                status_code=413,
                content={"detail": {"code": "request_too_large", "message": "Upload request is too large"}},
            )
            await response(scope, receive, send)


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description=(
        "Deterministic validation of synthetic PD datasets. Classification thresholds "
        "are configurable demonstration policy, not regulatory requirements."
    ),
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.cors_origins),
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "X-Trace-ID", "X-Ops-Token"],
    expose_headers=["X-Trace-ID"],
)
app.add_middleware(
    RequestBodyLimitMiddleware,
    max_bytes=settings.max_upload_bytes + 128 * 1024,
)


def _normalized_path(request: Request) -> str:
    route = request.scope.get("route")
    route_path = getattr(route, "path", None)
    return route_path if route_path else "__unmatched__"


@app.middleware("http")
async def correlated_request_middleware(request: Request, call_next):
    started = time.perf_counter()
    supplied = request.headers.get("X-Trace-ID", "")
    fallback_trace_id = supplied if supplied.isalnum() and len(supplied) <= 64 else uuid.uuid4().hex
    with tracer.start_as_current_span(f"{request.method} {request.url.path}") as span:
        trace_id = current_otel_trace_id() or fallback_trace_id
        token = trace_id_context.set(trace_id)
        request.state.trace_id = trace_id
        span.set_attribute("http.request.method", request.method)
        span.set_attribute("url.path", request.url.path)
        status_code = 500
        try:
            response = await call_next(request)
            status_code = response.status_code
            if status_code >= 500:
                span.set_status(Status(StatusCode.ERROR))
            response.headers["X-Trace-ID"] = trace_id
            return response
        except Exception as exc:
            span.record_exception(exc)
            span.set_status(Status(StatusCode.ERROR, str(exc)))
            logger.exception("Unhandled request error", extra={"event": "request_error"})
            raise
        finally:
            duration = time.perf_counter() - started
            path = _normalized_path(request)
            HTTP_REQUESTS.labels(request.method, path, str(status_code)).inc()
            HTTP_DURATION.labels(request.method, path).observe(duration)
            logger.info(
                "HTTP request completed",
                extra={
                    "event": "http_request",
                    "method": request.method,
                    "path": path,
                    "status": status_code,
                    "duration_ms": round(duration * 1000, 3),
                },
            )
            trace_id_context.reset(token)


@app.exception_handler(InputValidationError)
async def input_error_handler(request: Request, exc: InputValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "detail": {
                "code": exc.code,
                "message": exc.message,
                "errors": exc.errors,
                "quality": exc.quality,
                "trace_id": request.state.trace_id,
            }
        },
    )


@app.exception_handler(RequestValidationError)
async def request_error_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "detail": {
                "code": "invalid_request",
                "message": "Request validation failed",
                "errors": exc.errors(),
                "trace_id": request.state.trace_id,
            }
        },
    )


def _incident_state(db: Session) -> OperationalState:
    state = db.get(OperationalState, INCIDENT_KEY)
    if state is None:
        state = OperationalState(key=INCIDENT_KEY, enabled=False)
        db.add(state)
        db.commit()
        db.refresh(state)
    return state


def _incident_response(state: OperationalState, message: str) -> IncidentStateResponse:
    return IncidentStateResponse(
        enabled=state.enabled,
        message=message,
        updated_at=state.updated_at,
    )


def require_ops_token(x_ops_token: str | None = Header(default=None)) -> None:
    if x_ops_token is None or not secrets.compare_digest(x_ops_token, settings.ops_token):
        raise HTTPException(status_code=401, detail="Invalid or missing X-Ops-Token")


@app.get("/health", response_model=HealthResponse, tags=["operations"])
def health(db: Session = Depends(get_db)) -> HealthResponse:
    db.execute(text("SELECT 1"))
    state = _incident_state(db)
    return HealthResponse(
        incident_enabled=state.enabled,
        service=settings.app_name,
    )


@app.get("/metrics", include_in_schema=False)
def metrics() -> Response:
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.post(
    "/api/v1/validations",
    response_model=ValidationResponse,
    status_code=201,
    tags=["validations"],
)
async def create_validation(
    request: Request,
    file: UploadFile = File(..., description="UTF-8 CSV with synthetic PD observations"),
    db: Session = Depends(get_db),
) -> ValidationRecord:
    if _incident_state(db).enabled:
        VALIDATION_INCIDENT_ACTIVE.set(1)
        VALIDATION_REQUESTS.labels("incident_failure").inc()
        logger.warning(
            "Validation upload rejected by safe incident simulation",
            extra={"event": "validation_upload", "outcome": "incident_failure"},
        )
        raise HTTPException(
            status_code=503,
            detail={
                "code": "incident_simulation_active",
                "message": "Validation uploads are temporarily unavailable",
                "trace_id": request.state.trace_id,
            },
        )
    filename = file.filename or "upload.csv"
    if not filename.lower().endswith(".csv"):
        VALIDATION_REQUESTS.labels("validation_error").inc()
        raise InputValidationError("invalid_file_type", "Upload must have a .csv extension")
    content = await file.read(settings.max_upload_bytes + 1)
    if len(content) > settings.max_upload_bytes:
        VALIDATION_REQUESTS.labels("validation_error").inc()
        raise InputValidationError(
            "file_too_large",
            f"CSV exceeds maximum size of {settings.max_upload_bytes} bytes",
        )
    try:
        result = validate_csv(content, settings)
    except InputValidationError:
        VALIDATION_REQUESTS.labels("validation_error").inc()
        raise

    current_records = db.scalar(select(func.count()).select_from(ValidationRecord)) or 0
    if current_records >= settings.max_history_records:
        VALIDATION_REQUESTS.labels("capacity_reached").inc()
        raise HTTPException(
            status_code=429,
            detail={
                "code": "history_capacity_reached",
                "message": "Validation history capacity has been reached",
                "trace_id": request.state.trace_id,
            },
        )

    record = ValidationRecord(
        id=str(uuid.uuid4()),
        filename=filename[:255],
        status=result.status,
        record_count=result.record_count,
        average_pd=result.average_pd,
        observed_default_rate=result.observed_default_rate,
        brier_score=result.brier_score,
        calibration_gap=result.calibration_gap,
        quality=result.quality,
        findings=result.findings,
        calibration=result.calibration,
        policy=result.policy,
        trace_id=request.state.trace_id,
    )
    try:
        db.add(record)
        db.commit()
        db.refresh(record)
    except Exception:
        db.rollback()
        VALIDATION_REQUESTS.labels("server_error").inc()
        raise
    VALIDATION_REQUESTS.labels("success").inc()
    logger.info(
        "Validation completed",
        extra={
            "event": "validation_upload",
            "outcome": "success",
            "validation_id": record.id,
        },
    )
    return record


@app.get("/api/v1/validations", response_model=ValidationList, tags=["validations"])
def list_validations(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> ValidationList:
    total = db.scalar(select(func.count()).select_from(ValidationRecord)) or 0
    items = list(
        db.scalars(
            select(ValidationRecord)
            .order_by(ValidationRecord.created_at.desc(), ValidationRecord.id.desc())
            .offset(offset)
            .limit(limit)
        )
    )
    return ValidationList(items=items, total=total, limit=limit, offset=offset)


@app.get(
    "/api/v1/validations/{validation_id}",
    response_model=ValidationResponse,
    tags=["validations"],
)
def get_validation(validation_id: str, db: Session = Depends(get_db)) -> ValidationRecord:
    record = db.get(ValidationRecord, validation_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Validation not found")
    return record


@app.get(
    "/api/v1/ops/incident",
    response_model=IncidentStateResponse,
    tags=["operations"],
    dependencies=[Depends(require_ops_token)],
)
def get_incident(db: Session = Depends(get_db)) -> IncidentStateResponse:
    return _incident_response(_incident_state(db), "Incident state retrieved")


def _set_incident(db: Session, enabled: bool) -> OperationalState:
    state = _incident_state(db)
    state.enabled = enabled
    state.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(state)
    if not enabled:
        VALIDATION_INCIDENT_ACTIVE.set(0)
    return state


@app.post(
    "/api/v1/ops/incident/enable",
    response_model=IncidentStateResponse,
    tags=["operations"],
    dependencies=[Depends(require_ops_token)],
)
def enable_incident(db: Session = Depends(get_db)) -> IncidentStateResponse:
    state = _set_incident(db, True)
    logger.warning("Safe incident simulation enabled", extra={"event": "incident_enabled"})
    return _incident_response(state, "Safe validation upload failure enabled")


@app.post(
    "/api/v1/ops/incident/recover",
    response_model=IncidentStateResponse,
    tags=["operations"],
    dependencies=[Depends(require_ops_token)],
)
def recover_incident(db: Session = Depends(get_db)) -> IncidentStateResponse:
    state = _set_incident(db, False)
    logger.info("Safe incident simulation recovered", extra={"event": "incident_recovered"})
    return _incident_response(state, "Validation upload service recovered")

