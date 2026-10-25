from __future__ import annotations

from dataclasses import replace

import pytest

from app.config import get_settings
from app.validation import InputValidationError, validate_csv


def test_metrics_and_calibration_are_deterministic(valid_csv):
    result = validate_csv(valid_csv, get_settings())

    assert result.record_count == 4
    assert result.average_pd == pytest.approx(0.5)
    assert result.observed_default_rate == pytest.approx(0.5)
    assert result.brier_score == pytest.approx(0.025)
    assert result.calibration_gap == pytest.approx(0)
    assert result.status == "PASS"
    assert len(result.calibration) == 4
    assert result.calibration[0] == {
        "decile": 1,
        "record_count": 1,
        "average_pd": 0.1,
        "observed_default_rate": 0.0,
    }


@pytest.mark.parametrize(
    ("content", "code"),
    [
        (b"", "empty_file"),
        (b"observation_id,predicted_pd\nA,0.1\n", "missing_columns"),
        (b"observation_id,predicted_pd,default_flag\nA,,0\n", "invalid_rows"),
        (b"observation_id,predicted_pd,default_flag\nA,nope,0\n", "invalid_rows"),
        (b"observation_id,predicted_pd,default_flag\nA,1.1,0\n", "invalid_rows"),
        (b"observation_id,predicted_pd,default_flag\nA,0.1,2\n", "invalid_rows"),
    ],
)
def test_invalid_inputs_are_actionable(content, code):
    with pytest.raises(InputValidationError) as caught:
        validate_csv(content, get_settings())
    assert caught.value.code == code


def test_duplicate_ids_are_reported_and_can_fail_policy():
    content = (
        b"observation_id,predicted_pd,default_flag\n"
        b"A,0.1,0\nA,0.2,0\nB,0.8,1\n"
    )
    result = validate_csv(content, get_settings())
    assert result.quality["duplicate_count"] == 1
    assert result.status == "FAIL"
    assert next(item for item in result.findings if item["code"] == "duplicate_observation_ids")[
        "severity"
    ] == "FAIL"


def test_rules_are_configurable_demonstration_policy(valid_csv):
    strict = replace(
        get_settings(),
        pass_brier_max=0.01,
        warning_brier_max=0.02,
        pass_calibration_gap_max=0,
        warning_calibration_gap_max=0,
    )
    result = validate_csv(valid_csv, strict)
    assert result.status == "FAIL"
    assert "not regulatory" in result.policy["disclaimer"]


def test_row_limit_stops_processing_early():
    constrained = replace(get_settings(), max_csv_rows=2)
    content = (
        b"observation_id,predicted_pd,default_flag\n"
        b"A,0.1,0\nB,0.2,0\nC,0.3,0\n"
    )
    with pytest.raises(InputValidationError) as caught:
        validate_csv(content, constrained)
    assert caught.value.code == "too_many_rows"


def test_error_limit_bounds_allocated_error_details():
    constrained = replace(get_settings(), max_validation_errors=2)
    content = (
        b"observation_id,predicted_pd,default_flag\n"
        b"A,,\nB,,\nC,,\n"
    )
    with pytest.raises(InputValidationError) as caught:
        validate_csv(content, constrained)
    assert caught.value.code == "too_many_errors"
    assert len(caught.value.errors) == 2

