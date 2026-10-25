"""Alertmanager webhook receiver with a deliberately narrow remediation policy."""

from __future__ import annotations

import json
import logging
import os
from datetime import UTC, datetime
from typing import Any

import httpx
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("crvt.oncall")

BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000").rstrip("/")
OPS_TOKEN = os.getenv("OPS_TOKEN", "local-demo-token")
WEBHOOK_TOKEN = os.getenv("WEBHOOK_TOKEN", "local-alert-token")

app = FastAPI(
    title="Credit Risk Validation On-Call Responder",
    description="Receives one allow-listed user-impact alert and performs one bounded recovery action.",
    version="1.0.0",
)


class Alert(BaseModel):
    status: str
    labels: dict[str, str] = Field(default_factory=dict)
    annotations: dict[str, str] = Field(default_factory=dict)


class AlertPayload(BaseModel):
    status: str | None = None
    alerts: list[Alert] = Field(default_factory=list)


class RemediationResult(BaseModel):
    alert_name: str
    action: str
    diagnosed: bool
    remediated: bool
    verified: bool
    detail: str
    completed_at: str


_last_result: RemediationResult | None = None


def _emit(event: str, **fields: Any) -> None:
    logger.info(json.dumps({"timestamp": datetime.now(UTC).isoformat(), "event": event, **fields}))


def _probe_csv() -> tuple[str, bytes, str]:
    data = b"observation_id,predicted_pd,default_flag\noncall-probe,0.05,0\n"
    return ("oncall-recovery-probe.csv", data, "text/csv")


async def handle_user_impact_alert(client: httpx.AsyncClient) -> RemediationResult:
    """Diagnose, perform the only authorized mutation, and verify user recovery."""
    headers = {"X-Ops-Token": OPS_TOKEN}
    diagnosed = remediated = verified = False
    detail = ""
    try:
        diagnosis = await client.get(f"{BACKEND_URL}/api/v1/ops/incident", headers=headers)
        diagnosis.raise_for_status()
        state = diagnosis.json()
        diagnosed = True
        _emit("incident_diagnosed", incident_state=state)

        if state.get("validation_failure_enabled") is True:
            recovery = await client.post(f"{BACKEND_URL}/api/v1/ops/incident/recover", headers=headers)
            recovery.raise_for_status()
            remediated = recovery.json().get("validation_failure_enabled") is False
        else:
            remediated = True

        health = await client.get(f"{BACKEND_URL}/health")
        health.raise_for_status()
        probe = await client.post(
            f"{BACKEND_URL}/api/v1/validations",
            files={"file": _probe_csv()},
            headers={"X-Remediation-Probe": "true"},
        )
        probe.raise_for_status()
        verified = health.json().get("status") == "ok" and probe.status_code in (200, 201)
        detail = "Incident switch disabled and validation probe succeeded." if verified else "Recovery checks were inconclusive."
    except (httpx.HTTPError, ValueError, KeyError) as exc:
        detail = f"Bounded remediation failed: {type(exc).__name__}"
        _emit("remediation_failed", error_type=type(exc).__name__)

    result = RemediationResult(
        alert_name="ValidationUserImpact",
        action="disable_demo_validation_failure",
        diagnosed=diagnosed,
        remediated=remediated,
        verified=verified,
        detail=detail,
        completed_at=datetime.now(UTC).isoformat(),
    )
    _emit("remediation_completed", **result.model_dump())
    return result


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/v1/remediations/latest", response_model=RemediationResult | None)
async def latest() -> RemediationResult | None:
    return _last_result


@app.post("/api/v1/alerts", response_model=list[RemediationResult])
async def receive_alert(
    payload: AlertPayload,
    x_webhook_token: str | None = Header(default=None),
    authorization: str | None = Header(default=None),
) -> list[RemediationResult]:
    """React only to the allow-listed firing alert; ignore every other alert/action."""
    global _last_result
    bearer = f"Bearer {WEBHOOK_TOKEN}"
    if x_webhook_token != WEBHOOK_TOKEN and authorization != bearer:
        raise HTTPException(status_code=401, detail="Invalid webhook token")

    results: list[RemediationResult] = []
    async with httpx.AsyncClient(timeout=10) as client:
        for alert in payload.alerts:
            if alert.status != "firing" or alert.labels.get("alertname") != "ValidationUserImpact":
                _emit("alert_ignored", status=alert.status, labels=alert.labels)
                continue
            _last_result = await handle_user_impact_alert(client)
            results.append(_last_result)
    return results

