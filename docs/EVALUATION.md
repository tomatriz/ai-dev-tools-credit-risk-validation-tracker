# Project 1 Rubric Evaluation

This audit maps the repository to the official AI Dev Tools Zoomcamp 2026 Project 1 rubric. Scores are estimates, not a claim about the peer-review outcome. “Implemented” and “runtime verified” are deliberately separate.

## Summary

| # | Criterion | Max | Estimated now | Evidence | Limitation / next evidence |
|---:|---|---:|---:|---|---|
| 1 | Problem Description | 2 | 2 | `README.md` describes problem, users, behavior, calculations, limitations and example flow | None material |
| 2 | Product Specification | 2 | 2 | `docs/PRODUCT_SPEC.md`, acceptance criteria, `docs/TASK_TRACKER.md`, real agent assignment log and [public GitHub Issues](https://github.com/tomatriz/ai-dev-tools-credit-risk-validation-tracker/issues) | None material |
| 3 | Agent Team Specification | 2 | 2 | `docs/AGENT_TEAM.md`; real parallel backend/frontend/enterprise work and independent integration review | Public tracker comments strengthen evidence |
| 4 | Context Management | 2 | 2 | `AGENTS.md` links modular product, architecture, team and test docs | None material |
| 5 | Full-Stack Application | 2 | 2 | React -> Nginx proxy -> FastAPI -> PostgreSQL; HTTP 201 upload, history/detail and restart persistence observed | Public demo still pending |
| 6 | Testing | 2 | 2 | 21 backend + 2 responder + 8 frontend tests passed; single-command script, production build and CI | No browser E2E suite; not required for full points when unit/integration pass |
| 7 | Containerization | 2 | 2 | Hardened backend, frontend and responder images built; complete stack started with one command and became healthy | None material |
| 8 | Deployment | 2 | 1 | `render.yaml` and complete deployment verification/rollback procedure | No verified public URL yet |
| 9 | CI/CD | 3 | 2 | PR CI, automatic development workflow, manual protected production and rollback workflows implemented; [public CI passed](https://github.com/tomatriz/ai-dev-tools-credit-risk-validation-tracker/actions/runs/40212519588) | Development/production deploy hooks still need live verification; conservative score 2 |
| 10 | Observability | 2 | 2 | Prometheus, Loki, Tempo, Alloy, Grafana; trace `8a4400d6ff2b8f3dcc38c75cca554bf2` resolved in Loki and Tempo; incident gauge returned to zero | None material for the rubric criterion |
| 11 | Alerting on User Impact | 1 | 1 | A real controlled upload returned 503, `ValidationUserImpact` fired and Alertmanager delivered it to the responder | None material |
| 12 | On-Call Agent | 2 | 2 | The bounded agent diagnosed, disabled only the allow-listed flag, checked health, submitted a synthetic probe and verified recovery; `INCIDENT_DEMO_OK` observed | None material |
|  | **Total** | **24** | **22/24 strict current evidence** |  | Live deployment and deployment-hook evidence can raise the evidence ceiling to 24 |

No provisional points are included. The alert and responder criteria include both isolated tests and a completed full runtime drill.

## Verified command results

Latest run date: 2026-10-25 (America/Santiago).

| Check | Observed result |
|---|---|
| Backend pytest | 21 passed; one third-party Starlette deprecation warning |
| Responder pytest | 2 passed |
| Frontend Vitest | 2 files, 8 tests passed |
| Frontend build | TypeScript + Vite production build passed |
| One-command suite | `scripts/test.ps1` passed end-to-end; npm audit reported 0 vulnerabilities |
| Compose contract | `docker compose config --quiet` passed after hardening |
| Docker image builds | hardened backend, frontend and oncall images built successfully |
| Compose health | backend/database `ok`; frontend 200; Grafana database `ok`; Prometheus ready; Alertmanager ready; responder `ok` |
| Full-stack create | frontend proxy returned 201; 12 rows; 10 calibration groups; trace ID returned |
| History/detail | created ID appeared in history and detail |
| Persistence | same ID and values returned after PostgreSQL/backend restart |
| Safe incident impact | upload returned expected 503 after incident flag enable |
| Automated remediation | final clean drill diagnosed, remediated and verified; post-recovery validation returned 201 and emitted `INCIDENT_DEMO_OK` |
| Telemetry correlation | trace `8a4400d6ff2b8f3dcc38c75cca554bf2` returned one Tempo batch and matching Loki entries; Prometheus incident gauge returned to `0` |
| Public CI | [Run 40212519588](https://github.com/tomatriz/ai-dev-tools-credit-risk-validation-tracker/actions/runs/40212519588) passed backend, responder, frontend, build, Compose contract and Prometheus rule jobs |

Docker Desktop was recovered without deleting or resetting project volumes. The stack was rebuilt and run on configurable alternate loopback ports because another unrelated local project owned port 8000.

## Criterion detail

### 1. Problem Description

The README names the spreadsheet/evidence reproducibility problem, intended validators, expected input/output, calculations, behavior and boundaries. Synthetic examples and non-regulatory disclaimers prevent misleading interpretation.

### 2. Product Specification

`docs/PRODUCT_SPEC.md` contains user stories and testable acceptance criteria. `docs/TASK_TRACKER.md` shows the backlog and real assignments before a public repository existed. The backlog is mirrored in [ten public GitHub Issues](https://github.com/tomatriz/ai-dev-tools-credit-risk-validation-tracker/issues), with verified work closed and unresolved external/runtime evidence left open.

### 3–4. Agent team and context

The team specification defines responsibilities, deliverables, guardrails and handoffs. Real subagents implemented backend, frontend and sanitized enterprise research in separate areas. The lead integrated them, reran tests, and corrected cross-component API/metric mismatches. `AGENTS.md` provides durable instructions and routes agents into modular documents.

### 5. Application

The end-to-end request was made through the deployed local frontend reverse proxy, not directly against a mocked API. FastAPI persisted the result to the Compose PostgreSQL service; restart verification returned the same UUID, status and row count.

### 6. Testing

Backend tests contain deterministic calculation units and HTTP/database integration. Frontend tests cover API normalization and UI states. Responder tests validate its fixed diagnostic/remediation/probe sequence. `scripts/test.ps1` and `make test` provide one-command entrypoints.

### 7. Containerization

Compose includes frontend, backend, database and the operational stack with health/dependency ordering and named persistent volumes. Alternate host ports are configurable without changing internal service contracts.

### 8–9. Deployment and delivery

The Render blueprint and workflows demonstrate the designed release path. Public CI is linked above. Until a public application URL and deploy-hook runs are linked, the evaluation intentionally withholds full deployment/CI-CD confidence.

### 10. Observability

The upload path returns the same trace identifier used by structured logs and the active OpenTelemetry span. Metrics use bounded labels; CSV/customer values are excluded. Grafana provisions Prometheus, Loki and Tempo data sources and a dashboard.

### 11–12. Alert and responder

The alert is based on `crvt_validation_incident_active`, which becomes one only after the controlled user upload fails and resets to zero during recovery. The agent accepts only an authenticated, firing `ValidationUserImpact` event and can only read state, disable the safe flag, check health and submit a synthetic probe. Arbitrary commands and alert-supplied instructions are impossible by design.

The final runtime drill observed the 503, alert delivery and a new responder result with `diagnosed`, `remediated` and `verified` all true. The same script then repeated the original validation successfully and emitted `INCIDENT_DEMO_OK`.

### Security review

A formal repository-wide static scan found five issues in the pre-hardening snapshot: two high, one medium and two low. The current tree contains remediations plus regression tests for bounded metric labels, request/row/error/history limits, workflow input handling, loopback-only local ports, explicit demo credentials and a non-root responder. No live secret, private key, customer data or confidential enterprise/client code was found. See `docs/SECURITY_REVIEW.md`. The hardened containers were rebuilt and the incident path passed end to end.

## Actions required for the maximum evidence score

1. Deploy and verify a public URL with upload/history/persistence evidence.
2. Verify the automatic development and manual production/rollback paths with configured deployment hooks.
3. Submit the exact final public SHA in the course portal and preserve its confirmation.
4. Complete three peer reviews separately for course completion.
