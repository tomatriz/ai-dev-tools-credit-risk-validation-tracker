"""Environment-driven application configuration.

All scoring values are demonstration policy, not regulatory thresholds.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache


def _float(name: str, default: float) -> float:
    try:
        return float(os.getenv(name, str(default)))
    except ValueError as exc:
        raise ValueError(f"{name} must be numeric") from exc


@dataclass(frozen=True)
class Settings:
    app_name: str
    database_url: str
    ops_token: str
    max_upload_bytes: int
    max_csv_rows: int
    max_validation_errors: int
    max_history_records: int
    pass_brier_max: float
    warning_brier_max: float
    pass_calibration_gap_max: float
    warning_calibration_gap_max: float
    warning_duplicate_rate_max: float
    log_level: str
    log_file: str | None
    otlp_endpoint: str | None
    cors_origins: tuple[str, ...]


@lru_cache
def get_settings() -> Settings:
    ops_token = os.getenv("OPS_TOKEN", "change-me-in-production")
    allow_demo_credentials = os.getenv("ALLOW_INSECURE_DEMO_CREDENTIALS", "false").lower() == "true"
    if ops_token in {"change-me-in-production", "local-demo-token"} and not allow_demo_credentials:
        raise ValueError(
            "OPS_TOKEN must be explicitly configured; demo credentials require "
            "ALLOW_INSECURE_DEMO_CREDENTIALS=true"
        )
    settings = Settings(
        app_name=os.getenv("APP_NAME", "Credit Risk Validation Tracker API"),
        database_url=os.getenv("DATABASE_URL", "sqlite:///./crvt.db"),
        ops_token=ops_token,
        max_upload_bytes=int(os.getenv("MAX_UPLOAD_BYTES", str(5 * 1024 * 1024))),
        max_csv_rows=int(os.getenv("MAX_CSV_ROWS", "100000")),
        max_validation_errors=int(os.getenv("MAX_VALIDATION_ERRORS", "50")),
        max_history_records=int(os.getenv("MAX_HISTORY_RECORDS", "10000")),
        pass_brier_max=_float("PASS_BRIER_MAX", 0.20),
        warning_brier_max=_float("WARNING_BRIER_MAX", 0.25),
        pass_calibration_gap_max=_float("PASS_CALIBRATION_GAP_MAX", 0.05),
        warning_calibration_gap_max=_float("WARNING_CALIBRATION_GAP_MAX", 0.10),
        warning_duplicate_rate_max=_float("WARNING_DUPLICATE_RATE_MAX", 0.01),
        log_level=os.getenv("LOG_LEVEL", "INFO").upper(),
        log_file=os.getenv("LOG_FILE") or None,
        otlp_endpoint=os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT") or None,
        cors_origins=tuple(
            origin.strip()
            for origin in os.getenv(
                "CORS_ORIGINS",
                (
                    "http://localhost:3000,http://localhost:5173,"
                    "https://tomatriz.github.io"
                ),
            ).split(",")
            if origin.strip()
        ),
    )
    numeric_thresholds = (
        settings.pass_brier_max,
        settings.warning_brier_max,
        settings.pass_calibration_gap_max,
        settings.warning_calibration_gap_max,
        settings.warning_duplicate_rate_max,
    )
    if not all(0 <= value <= 1 for value in numeric_thresholds):
        raise ValueError("Demonstration policy thresholds must be within [0, 1]")
    if settings.pass_brier_max > settings.warning_brier_max:
        raise ValueError("PASS_BRIER_MAX cannot exceed WARNING_BRIER_MAX")
    if settings.pass_calibration_gap_max > settings.warning_calibration_gap_max:
        raise ValueError(
            "PASS_CALIBRATION_GAP_MAX cannot exceed WARNING_CALIBRATION_GAP_MAX"
        )
    if settings.max_upload_bytes <= 0:
        raise ValueError("MAX_UPLOAD_BYTES must be positive")
    if settings.max_csv_rows <= 0:
        raise ValueError("MAX_CSV_ROWS must be positive")
    if settings.max_validation_errors <= 0:
        raise ValueError("MAX_VALIDATION_ERRORS must be positive")
    if settings.max_history_records <= 0:
        raise ValueError("MAX_HISTORY_RECORDS must be positive")
    return settings

