# Project 1 Rubric Evaluation

This audit maps the repository to the official AI Dev Tools Zoomcamp 2026 Project 1 rubric. Scores are estimates, not a claim about the peer-review outcome. “Implemented” and “runtime verified” are deliberately separate.

## Summary

| # | Criterion | Max | Estimated now | Evidence | Limitation / next evidence |
|---:|---|---:|---:|---|---|
| 1 | Problem Description | 2 | 2 | `README.md` describes problem, users, behavior, calculations, limitations and example flow | None material |
| 2 | Product Specification | 2 | 1 | `docs/PRODUCT_SPEC.md`, acceptance criteria, `docs/TASK_TRACKER.md`, real agent assignment log | Public GitHub Issues must be created and linked for the second point |
| 3 | Agent Team Specification | 2 | 2 | `docs/AGENT_TEAM.md`; real parallel backend/frontend/enterprise work and independent integration review | Public tracker comments strengthen evidence |
| 4 | Context Management | 2 | 2 | `AGENTS.md` links modular product, architecture, team and test docs | None material |
| 5 | Full-Stack Application | 2 | 2 | React -> Nginx proxy -> FastAPI -> PostgreSQL; HTTP 201 upload, history/detail and restart persistence observed | Public demo still pending |
| 6 | Testing | 2 | 2 | 21 backend + 2 responder + 8 frontend tests passed; single-command script, production build and CI | No browser E2E suite; not required for full points when unit/integration pass |
| 7 | Containerization | 2 | 2 | Compose and all three project images built; complete stack started with one command | Host Docker later hit a stale internal socket after successful runs; this is recorded below |
| 8 | Deployment | 2 | 1 | `render.yaml` and complete deployment verification/rollback procedure | No verified public URL yet |
| 9 | CI/CD | 3 | 2 | PR CI, automatic development workflow, manual protected production and rollback workflows implemented | Public GitHub Actions runs and deploy hooks still need verification; conservative score 2 |
| 10 | Observability | 2 | 2 | Prometheus, Loki, Tempo, Alloy, Grafana; shared trace ID in response/log/span; Grafana/Prometheus/Alertmanager healthy during Compose run | Final screenshot/query evidence should be attached publicly |
| 11 | Alerting on User Impact | 1 | 0 | `ValidationUserImpact` watches the resolvable real-user failure gauge; the controlled 503 was reproduced | End-to-end alert firing/delivery still needs a final rerun after host Docker recovery |
| 12 | On-Call Agent | 2 | 0 | Bounded webhook agent and 2 passing tests; allow-listed diagnosis/recovery/probe | The official criterion is binary; the full alert-to-agent runtime has not yet been observed successfully |
|  | **Total** | **24** | **18/24 strict current evidence** |  | Public tracker, deploy, CI runs and final incident drill can raise the evidence ceiling to 24 |

No provisional points are included. Alert and responder code is ready and tested in isolation, but criteria 11–12 remain at zero until the full runtime drill succeeds.

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
| Docker image builds | backend, frontend and oncall built successfully before final hardening; hardened rebuild pending host recovery |
| Compose health | backend/database `ok`; frontend 200; Grafana database `ok`; Prometheus ready; Alertmanager ready; responder `ok` |
| Full-stack create | frontend proxy returned 201; 12 rows; 10 calibration groups; trace ID returned |
| History/detail | created ID appeared in history and detail |
| Persistence | same ID and values returned after PostgreSQL/backend restart |
| Safe incident impact | upload returned expected 503 after incident flag enable |
| Automated remediation | first 30-second drill did not verify; therefore not claimed successful |

After the incomplete drill, Docker Desktop itself crashed on restart because a host-internal socket reparse point became inaccessible. Project volumes were not deleted or reset. Unit tests, the earlier successful Compose/user-flow evidence and the current Compose syntax validation remain valid, but the hardened images and final incident drill require Docker Desktop/WSL host recovery.

## Criterion detail

### 1. Problem Description

The README names the spreadsheet/evidence reproducibility problem, intended validators, expected input/output, calculations, behavior and boundaries. Synthetic examples and non-regulatory disclaimers prevent misleading interpretation.

### 2. Product Specification

`docs/PRODUCT_SPEC.md` contains user stories and testable acceptance criteria. `docs/TASK_TRACKER.md` shows the backlog and real assignments before a public repository existed. Full evidence requires mirroring those tasks into public GitHub Issues and adding their URLs here.

### 3–4. Agent team and context

The team specification defines responsibilities, deliverables, guardrails and handoffs. Real subagents implemented backend, frontend and sanitized enterprise research in separate areas. The lead integrated them, reran tests, and corrected cross-component API/metric mismatches. `AGENTS.md` provides durable instructions and routes agents into modular documents.

### 5. Application

The end-to-end request was made through the deployed local frontend reverse proxy, not directly against a mocked API. FastAPI persisted the result to the Compose PostgreSQL service; restart verification returned the same UUID, status and row count.

### 6. Testing

Backend tests contain deterministic calculation units and HTTP/database integration. Frontend tests cover API normalization and UI states. Responder tests validate its fixed diagnostic/remediation/probe sequence. `scripts/test.ps1` and `make test` provide one-command entrypoints.

### 7. Containerization

Compose includes frontend, backend, database and the operational stack with health/dependency ordering and named persistent volumes. Alternate host ports are configurable without changing internal service contracts.

### 8–9. Deployment and delivery

The Render blueprint and workflows demonstrate the designed release path. Until a public URL and real Actions runs are linked, the evaluation intentionally withholds full deployment/CI-CD confidence.

### 10. Observability

The upload path returns the same trace identifier used by structured logs and the active OpenTelemetry span. Metrics use bounded labels; CSV/customer values are excluded. Grafana provisions Prometheus, Loki and Tempo data sources and a dashboard.

### 11–12. Alert and responder

The alert is based on `crvt_validation_incident_active`, which becomes one only after the controlled user upload fails and resets to zero during recovery. The agent accepts only an authenticated, firing `ValidationUserImpact` event and can only read state, disable the safe flag, check health and submit a synthetic probe. Arbitrary commands and alert-supplied instructions are impossible by design.

The initial runtime drill proved the 503 but timed out before a verified responder result. This is an explicit open verification item, not a successful claim.

### Security review

A formal repository-wide static scan found five issues in the pre-hardening snapshot: two high, one medium and two low. The current tree contains remediations plus regression tests for bounded metric labels, request/row/error/history limits, workflow input handling, loopback-only local ports, explicit demo credentials and a non-root responder. No live secret, private key, customer data or confidential enterprise/client code was found. See `docs/SECURITY_REVIEW.md`. A post-hardening container rebuild remains pending with Docker host recovery.

## Actions required for the maximum evidence score

1. Publish the repository and mirror tracker tasks to public Issues with acceptance criteria and agent evidence.
2. Observe CI on the final SHA and link the run.
3. Deploy and verify a public URL with upload/history/persistence evidence.
4. Recover host Docker, rerun `scripts/demo-incident.ps1`, and save Alertmanager, responder and post-recovery evidence.
5. Submit the exact final public SHA in the course portal and preserve its confirmation.
6. Complete three peer reviews separately for course completion.
