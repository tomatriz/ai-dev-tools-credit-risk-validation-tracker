"""Deterministic parsing, quality checks, metrics and demonstration scoring."""

from __future__ import annotations

import csv
import io
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation

from .config import Settings

REQUIRED_COLUMNS = ("observation_id", "predicted_pd", "default_flag")
DISCLAIMER = (
    "Configurable demonstration policy only; these thresholds are not regulatory "
    "requirements and must not be used for real model approval decisions."
)


class InputValidationError(ValueError):
    def __init__(
        self,
        code: str,
        message: str,
        *,
        errors: list[dict] | None = None,
        quality: dict | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.errors = errors or []
        self.quality = quality


@dataclass(frozen=True)
class Observation:
    observation_id: str
    predicted_pd: Decimal
    default_flag: int
    input_order: int


@dataclass(frozen=True)
class ValidationResult:
    status: str
    record_count: int
    average_pd: float
    observed_default_rate: float
    brier_score: float
    calibration_gap: float
    quality: dict
    findings: list[dict]
    calibration: list[dict]
    policy: dict


def _empty_quality(row_count: int = 0) -> dict:
    return {
        "row_count": row_count,
        "null_count": 0,
        "duplicate_count": 0,
        "format_error_count": 0,
        "out_of_range_count": 0,
    }


def parse_csv(
    content: bytes, *, max_rows: int, max_errors: int
) -> tuple[list[Observation], dict]:
    try:
        text = content.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise InputValidationError(
            "invalid_encoding", "CSV must use UTF-8 encoding"
        ) from exc

    try:
        reader = csv.DictReader(io.StringIO(text, newline=""), strict=True)
        headers = reader.fieldnames
        if headers is None:
            raise InputValidationError("empty_file", "CSV is empty or has no header")
        normalized = [header.strip() for header in headers]
        missing = [column for column in REQUIRED_COLUMNS if column not in normalized]
        if missing:
            raise InputValidationError(
                "missing_columns",
                f"Missing required columns: {', '.join(missing)}",
                errors=[{"field": column, "message": "required column is missing"} for column in missing],
            )
        if len(normalized) != len(set(normalized)):
            raise InputValidationError(
                "duplicate_columns", "CSV contains duplicate column names"
            )
        reader.fieldnames = normalized
    except csv.Error as exc:
        raise InputValidationError("malformed_csv", f"Malformed CSV: {exc}") from exc

    quality = _empty_quality()
    errors: list[dict] = []
    observations: list[Observation] = []
    seen_ids: set[str] = set()

    def add_error(error: dict) -> None:
        errors.append(error)
        if len(errors) >= max_errors:
            raise InputValidationError(
                "too_many_errors",
                f"CSV reached the maximum of {max_errors} reported validation errors",
                errors=errors,
                quality=quality,
            )

    try:
        for index, row in enumerate(reader, start=2):
            quality["row_count"] += 1
            if quality["row_count"] > max_rows:
                raise InputValidationError(
                    "too_many_rows",
                    f"CSV exceeds the maximum of {max_rows} data rows",
                    quality=quality,
                )
            if None in row:
                quality["format_error_count"] += 1
                add_error(
                    {
                        "row": index,
                        "field": None,
                        "message": "row contains more values than the header",
                    }
                )
                continue
            values = {column: (row.get(column) or "").strip() for column in REQUIRED_COLUMNS}
            null_fields = [column for column, value in values.items() if not value]
            if null_fields:
                quality["null_count"] += len(null_fields)
                for field in null_fields:
                    add_error({"row": index, "field": field, "message": "value is required"})
                continue

            observation_id = values["observation_id"]
            if observation_id in seen_ids:
                quality["duplicate_count"] += 1
            seen_ids.add(observation_id)

            try:
                predicted_pd = Decimal(values["predicted_pd"])
            except InvalidOperation:
                quality["format_error_count"] += 1
                add_error(
                    {"row": index, "field": "predicted_pd", "message": "must be numeric"}
                )
                continue
            if not predicted_pd.is_finite() or not Decimal("0") <= predicted_pd <= Decimal("1"):
                quality["out_of_range_count"] += 1
                add_error(
                    {"row": index, "field": "predicted_pd", "message": "must be within [0, 1]"}
                )
                continue

            if values["default_flag"] not in {"0", "1"}:
                category = (
                    "out_of_range_count"
                    if values["default_flag"].lstrip("+-").isdigit()
                    else "format_error_count"
                )
                quality[category] += 1
                add_error(
                    {"row": index, "field": "default_flag", "message": "must be exactly 0 or 1"}
                )
                continue

            observations.append(
                Observation(observation_id, predicted_pd, int(values["default_flag"]), index)
            )
    except csv.Error as exc:
        raise InputValidationError("malformed_csv", f"Malformed CSV: {exc}") from exc

    if quality["row_count"] == 0:
        raise InputValidationError("empty_file", "CSV contains no data rows")

    if errors:
        raise InputValidationError(
            "invalid_rows",
            f"CSV contains {len(errors)} invalid value(s)",
            errors=errors,
            quality=quality,
        )
    return observations, quality


def _calibration(observations: list[Observation]) -> list[dict]:
    group_count = min(10, len(observations))
    ordered = sorted(
        observations,
        key=lambda item: (item.predicted_pd, item.observation_id, item.input_order),
    )
    groups: list[list[Observation]] = [[] for _ in range(group_count)]
    for index, observation in enumerate(ordered):
        group_index = min((index * group_count) // len(ordered), group_count - 1)
        groups[group_index].append(observation)

    result = []
    for index, group in enumerate(groups, start=1):
        count = Decimal(len(group))
        result.append(
            {
                "decile": index,
                "record_count": len(group),
                "average_pd": float(sum((item.predicted_pd for item in group), Decimal(0)) / count),
                "observed_default_rate": float(
                    Decimal(sum(item.default_flag for item in group)) / count
                ),
            }
        )
    return result


def calculate(observations: list[Observation], quality: dict, settings: Settings) -> ValidationResult:
    count = Decimal(len(observations))
    average_pd_d = sum((item.predicted_pd for item in observations), Decimal(0)) / count
    default_rate_d = Decimal(sum(item.default_flag for item in observations)) / count
    brier_d = (
        sum(
            ((item.predicted_pd - Decimal(item.default_flag)) ** 2 for item in observations),
            Decimal(0),
        )
        / count
    )
    gap_d = abs(average_pd_d - default_rate_d)
    duplicate_rate = Decimal(quality["duplicate_count"]) / count

    average_pd = float(average_pd_d)
    default_rate = float(default_rate_d)
    brier = float(brier_d)
    gap = float(gap_d)
    duplicate_rate_f = float(duplicate_rate)

    findings: list[dict] = []
    if brier <= settings.pass_brier_max:
        brier_severity = "PASS"
        brier_message = "Brier score is within the example pass range"
    elif brier <= settings.warning_brier_max:
        brier_severity = "WARNING"
        brier_message = "Brier score exceeds the example pass threshold"
    else:
        brier_severity = "FAIL"
        brier_message = "Brier score exceeds the example fail threshold"
    findings.append(
        {
            "code": "brier_score",
            "severity": brier_severity,
            "message": brier_message,
            "actual": brier,
            "threshold": (
                settings.pass_brier_max
                if brier_severity != "FAIL"
                else settings.warning_brier_max
            ),
        }
    )

    if gap <= settings.pass_calibration_gap_max:
        gap_severity = "PASS"
        gap_message = "Portfolio calibration gap is within the example pass range"
    elif gap <= settings.warning_calibration_gap_max:
        gap_severity = "WARNING"
        gap_message = "Portfolio calibration gap exceeds the example pass threshold"
    else:
        gap_severity = "FAIL"
        gap_message = "Portfolio calibration gap exceeds the example fail threshold"
    findings.append(
        {
            "code": "portfolio_calibration_gap",
            "severity": gap_severity,
            "message": gap_message,
            "actual": gap,
            "threshold": (
                settings.pass_calibration_gap_max
                if gap_severity != "FAIL"
                else settings.warning_calibration_gap_max
            ),
        }
    )

    if quality["duplicate_count"] == 0:
        duplicate_severity = "PASS"
        duplicate_message = "Observation identifiers are unique"
    elif duplicate_rate_f <= settings.warning_duplicate_rate_max:
        duplicate_severity = "WARNING"
        duplicate_message = "Duplicate observation identifiers were found"
    else:
        duplicate_severity = "FAIL"
        duplicate_message = "Duplicate rate exceeds the example tolerance"
    findings.append(
        {
            "code": "duplicate_observation_ids",
            "severity": duplicate_severity,
            "message": duplicate_message,
            "actual": quality["duplicate_count"],
            "threshold": settings.warning_duplicate_rate_max,
        }
    )

    severities = {finding["severity"] for finding in findings}
    status = "FAIL" if "FAIL" in severities else "WARNING" if "WARNING" in severities else "PASS"
    policy = {
        "disclaimer": DISCLAIMER,
        "pass_brier_max": settings.pass_brier_max,
        "warning_brier_max": settings.warning_brier_max,
        "pass_calibration_gap_max": settings.pass_calibration_gap_max,
        "warning_calibration_gap_max": settings.warning_calibration_gap_max,
        "warning_duplicate_rate_max": settings.warning_duplicate_rate_max,
    }
    return ValidationResult(
        status=status,
        record_count=len(observations),
        average_pd=average_pd,
        observed_default_rate=default_rate,
        brier_score=brier,
        calibration_gap=gap,
        quality=quality,
        findings=findings,
        calibration=_calibration(observations),
        policy=policy,
    )


def validate_csv(content: bytes, settings: Settings) -> ValidationResult:
    observations, quality = parse_csv(
        content,
        max_rows=settings.max_csv_rows,
        max_errors=settings.max_validation_errors,
    )
    return calculate(observations, quality, settings)

