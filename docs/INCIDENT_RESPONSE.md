# Incident Response: Validation Upload Failure

## User impact and alert

`ValidationUserImpact` fires when at least one CSV validation request fails in the previous minute. This intentionally watches a user function rather than CPU or memory. In a real service the expression would be tuned with traffic volume, error budget and multi-window thresholds; one failure is appropriate here because the incident is a controlled demonstration.

## Safe reproduction

The demo switch makes only the upload endpoint return `503`. It does not delete or corrupt records. Enabling or recovering the switch requires `X-Ops-Token`; never expose the token in a public frontend.

```powershell
./scripts/demo-incident.ps1
```

## Automated responder policy

The `oncall` service accepts Alertmanager webhooks but acts only when all conditions are true:

- webhook authentication is valid;
- alert status is `firing`;
- `alertname` is exactly `ValidationUserImpact`.

It can call only three fixed backend operations: read incident state, disable the demo failure switch, and run health/upload probes. It cannot execute shell commands, change infrastructure, delete data, edit thresholds or act on generated free text.

## Diagnosis, remediation and verification

1. Read the backend incident state.
2. If the reversible validation-failure flag is enabled, call the fixed recovery endpoint.
3. Verify `/health`.
4. Submit a one-row synthetic CSV probe.
5. Record a structured remediation result with `diagnosed`, `remediated` and `verified` booleans.
6. Re-run the original sample request.

If any step fails, the responder records failure and stops. It does not retry unrelated mutations. A human should inspect Grafana, backend logs and `GET /api/v1/remediations/latest`.

## Manual fallback

```bash
curl -H "X-Ops-Token: $OPS_TOKEN" http://localhost:8000/api/v1/ops/incident
curl -X POST -H "X-Ops-Token: $OPS_TOKEN" http://localhost:8000/api/v1/ops/incident/recover
curl http://localhost:8000/health
```

## Production differences

Production would require authenticated service identity, a secret manager, approval tiers, idempotency, durable audit storage, paging, rate limits and a broader root-cause workflow. The demo proves the alert-to-bounded-remediation loop; it does not claim enterprise incident automation.

