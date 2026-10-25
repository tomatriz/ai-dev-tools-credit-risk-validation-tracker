from __future__ import annotations

from dataclasses import replace

from app import main

def upload(client, content: bytes, filename: str = "portfolio.csv"):
    return client.post(
        "/api/v1/validations",
        files={"file": (filename, content, "text/csv")},
    )


def test_health_openapi_and_metrics(client):
    health = client.get("/health")
    assert health.status_code == 200
    assert health.json()["database"] == "ok"
    assert health.headers["x-trace-id"]

    schema = client.get("/openapi.json")
    assert schema.status_code == 200
    assert "/api/v1/validations" in schema.json()["paths"]

    metrics = client.get("/metrics")
    assert metrics.status_code == 200
    assert "crvt_http_requests_total" in metrics.text
    assert "crvt_validation_requests_total" in metrics.text


def test_unmatched_paths_use_one_bounded_metric_label(client):
    assert client.get("/missing-one").status_code == 404
    assert client.get("/missing-two").status_code == 404
    metrics = client.get("/metrics").text
    assert 'path="__unmatched__"' in metrics
    assert "/missing-one" not in metrics
    assert "/missing-two" not in metrics


def test_request_body_limit_runs_before_multipart_parsing(client):
    response = client.post(
        "/api/v1/validations",
        headers={"Content-Length": str(6 * 1024 * 1024)},
        content=b"",
    )
    assert response.status_code == 413
    assert response.json()["detail"]["code"] == "request_too_large"


def test_upload_persists_and_can_be_reopened(client, valid_csv):
    response = upload(client, valid_csv)
    assert response.status_code == 201, response.text
    created = response.json()
    assert created["status"] == "PASS"
    assert created["trace_id"] == response.headers["x-trace-id"]
    assert created["quality"]["row_count"] == 4

    history = client.get("/api/v1/validations")
    assert history.status_code == 200
    assert history.json()["total"] == 1
    assert history.json()["items"][0]["id"] == created["id"]

    detail = client.get(f"/api/v1/validations/{created['id']}")
    assert detail.status_code == 200
    assert detail.json() == created


def test_invalid_upload_is_not_persisted(client):
    response = upload(
        client,
        b"observation_id,predicted_pd,default_flag\nA,9,0\n",
    )
    assert response.status_code == 422
    assert response.json()["detail"]["code"] == "invalid_rows"
    assert response.json()["detail"]["quality"]["out_of_range_count"] == 1
    assert client.get("/api/v1/validations").json()["total"] == 0


def test_history_capacity_bounds_anonymous_persistence(client, valid_csv, monkeypatch):
    monkeypatch.setattr(main, "settings", replace(main.settings, max_history_records=1))
    assert upload(client, valid_csv).status_code == 201
    response = upload(client, valid_csv)
    assert response.status_code == 429
    assert response.json()["detail"]["code"] == "history_capacity_reached"
    assert client.get("/api/v1/validations").json()["total"] == 1


def test_non_csv_and_missing_history(client, valid_csv):
    assert upload(client, valid_csv, "portfolio.txt").status_code == 422
    assert client.get("/api/v1/validations/unknown").status_code == 404


def test_incident_contract_is_authenticated_and_reversible(client, valid_csv):
    assert client.get("/api/v1/ops/incident").status_code == 401
    headers = {"X-Ops-Token": "test-ops-token"}

    initial = client.get("/api/v1/ops/incident", headers=headers)
    assert initial.status_code == 200
    assert initial.json()["enabled"] is False

    enabled = client.post("/api/v1/ops/incident/enable", headers=headers)
    assert enabled.status_code == 200
    assert enabled.json()["enabled"] is True
    failure = upload(client, valid_csv)
    assert failure.status_code == 503
    assert failure.json()["detail"]["code"] == "incident_simulation_active"
    assert client.get("/api/v1/validations").json()["total"] == 0
    assert "crvt_validation_incident_active 1.0" in client.get("/metrics").text

    recovered = client.post("/api/v1/ops/incident/recover", headers=headers)
    assert recovered.status_code == 200
    assert recovered.json()["enabled"] is False
    assert "crvt_validation_incident_active 0.0" in client.get("/metrics").text
    assert upload(client, valid_csv).status_code == 201


def test_trace_id_is_correlated(client, valid_csv):
    response = client.post(
        "/api/v1/validations",
        headers={"X-Trace-ID": "testtrace123"},
        files={"file": ("portfolio.csv", valid_csv, "text/csv")},
    )
    assert response.status_code == 201
    # A valid OTEL span takes precedence when SDK tracing is active; either way response and body agree.
    assert response.json()["trace_id"] == response.headers["x-trace-id"]

