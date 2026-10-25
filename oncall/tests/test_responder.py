import os

import httpx
import pytest

os.environ.setdefault("OPS_TOKEN", "test-ops-token")
os.environ.setdefault("WEBHOOK_TOKEN", "test-webhook-token")

from app import main


@pytest.mark.asyncio
async def test_bounded_responder_diagnoses_recovers_and_verifies(monkeypatch):
    seen = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append((request.method, request.url.path))
        if request.url.path.endswith("/ops/incident"):
            return httpx.Response(200, json={"enabled": True})
        if request.url.path.endswith("/ops/incident/recover"):
            return httpx.Response(200, json={"enabled": False})
        if request.url.path == "/health":
            return httpx.Response(200, json={"status": "ok"})
        if request.url.path.endswith("/validations"):
            return httpx.Response(201, json={"id": "probe"})
        return httpx.Response(404)

    transport = httpx.MockTransport(handler)
    client = httpx.AsyncClient(transport=transport, base_url="http://backend")
    result = await main.handle_user_impact_alert(client)
    await client.aclose()

    assert result.diagnosed and result.remediated and result.verified
    assert ("POST", "/api/v1/ops/incident/recover") in seen


def test_probe_contains_only_synthetic_data():
    name, content, content_type = main._probe_csv()
    assert name == "oncall-recovery-probe.csv"
    assert b"oncall-probe,0.05,0" in content
    assert content_type == "text/csv"

