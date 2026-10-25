"""Public API schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


Status = Literal["PASS", "WARNING", "FAIL"]


class QualityResult(BaseModel):
    row_count: int
    null_count: int
    duplicate_count: int
    format_error_count: int
    out_of_range_count: int


class Finding(BaseModel):
    code: str
    severity: Status
    message: str
    actual: float | int
    threshold: float | int | None = None


class CalibrationBin(BaseModel):
    decile: int
    record_count: int
    average_pd: float
    observed_default_rate: float


class DemonstrationPolicy(BaseModel):
    disclaimer: str
    pass_brier_max: float
    warning_brier_max: float
    pass_calibration_gap_max: float
    warning_calibration_gap_max: float
    warning_duplicate_rate_max: float


class ValidationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    filename: str
    created_at: datetime
    status: Status
    record_count: int
    average_pd: float
    observed_default_rate: float
    brier_score: float
    calibration_gap: float
    quality: QualityResult
    findings: list[Finding]
    calibration: list[CalibrationBin]
    policy: DemonstrationPolicy
    trace_id: str


class ValidationSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    filename: str
    created_at: datetime
    status: Status
    record_count: int
    average_pd: float
    observed_default_rate: float
    brier_score: float
    trace_id: str


class ValidationList(BaseModel):
    items: list[ValidationSummary]
    total: int
    limit: int
    offset: int


class IncidentStateResponse(BaseModel):
    enabled: bool
    mode: Literal["validation_upload_failure"] = "validation_upload_failure"
    message: str
    updated_at: datetime | None = None


class HealthResponse(BaseModel):
    status: Literal["ok"] = "ok"
    database: Literal["ok"] = "ok"
    incident_enabled: bool
    service: str


class ErrorItem(BaseModel):
    row: int | None = None
    field: str | None = None
    message: str


class ValidationErrorBody(BaseModel):
    code: str
    message: str
    errors: list[ErrorItem] = Field(default_factory=list)
    quality: QualityResult | None = None

