# Credit Risk Validation Tracker — Agent Context

## Mission

Build and verify a public, non-confidential full-stack demonstration for AI Dev Tools Zoomcamp 2026 Project 1. The application validates synthetic PD datasets, persists validation history, exposes a documented API, and demonstrates correlated observability, user-impact alerting, and bounded automated incident remediation.

## Non-negotiable rules

- Use only synthetic or explicitly public data. Never copy enterprise/client code, data, credentials, or internal details.
- Treat all PASS/WARNING/FAIL thresholds as configurable demonstration policy, not regulatory requirements.
- Do not claim a test, deployment, incident response, GitHub issue, or submission succeeded without evidence.
- Keep secrets out of Git; use `.env.example` and repository/environment secrets.
- Preserve deterministic calculations and return actionable validation errors.

## Architecture and ownership

- `backend/`: FastAPI, SQLAlchemy, validation engine, API and backend tests.
- `frontend/`: React + TypeScript dashboard and frontend tests.
- `oncall/`: bounded incident responder and tests.
- `observability/`: Prometheus, Grafana, Loki, Tempo, Alloy and alerting configuration.
- `docs/`: product, architecture, operations, evidence, learning and sanitized enterprise comparison.
- `.github/workflows/`: CI and deployment workflows.

## Working process

1. Product Manager defines acceptance criteria and tracker tasks.
2. Engineers implement against the documented API and tests.
3. QA independently runs unit, integration, UI, Compose and incident checks.
4. SRE verifies telemetry correlation, alert activation, remediation and rollback.
5. Documentation records only observed results and explicit limitations.

Agents must keep changes within their assigned area, review existing work before editing shared files, and report commands and outcomes. See `docs/AGENT_TEAM.md`, `docs/PRODUCT_SPEC.md`, `docs/ARCHITECTURE.md`, and `docs/TESTING.md`.

## Core commands

- Local stack: `docker compose up --build`
- Backend tests: `python -m pytest backend/tests`
- Frontend tests: `npm --prefix frontend test -- --run`
- All tests: `./scripts/test.ps1` (PowerShell) or `make test`
- Incident demo: `./scripts/demo-incident.ps1`

## Definition of done

Code, tests, containers, documentation, telemetry, alert and responder evidence are verified; public deployment/submission states are recorded accurately in `docs/SUBMISSION_STATUS.md`; peer reviews remain a separate learner action unless actually completed.
