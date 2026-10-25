# Deployment and Release Operations

## Local deployment

Requirements: Docker Desktop with Compose v2. From the repository root:

```bash
cp .env.example .env
docker compose up --build
```

Open the dashboard at `http://localhost:3000`, API documentation at `http://localhost:8000/docs`, Grafana at `http://localhost:3001`, Prometheus at `http://localhost:9090`, and Alertmanager at `http://localhost:9093`.

If a default port is already used, copy `.env.example` and change the corresponding `CRVT_*_PORT` value; container-to-container contracts do not change.

## Public deployment design

`render.yaml` is a declarative Render blueprint for the frontend, backend and managed PostgreSQL database. Both web services and the database explicitly use the free plan, so Blueprint creation must not select a paid resource. The dashboard receives the API service's private `hostport` through a Render service reference and proxies `/api/v1` on the dashboard origin; no public API URL or cross-origin browser configuration is required. Render automatically deploys new commits; the separate GitHub development workflow provides the CI-gated deployment-hook path once its repository secret is configured. After creation, verify `/health`, `/docs`, a sample upload, history retrieval and persistence across a backend restart.

The local Grafana/Loki/Tempo/Prometheus demonstration is intentionally Compose-based. A public production deployment should use managed or separately secured telemetry endpoints and must not expose operational controls publicly.

## CI/CD stages

- `.github/workflows/ci.yml` runs backend, responder and frontend tests plus build/config validation on every pull request and `main` push.
- `.github/workflows/deploy-dev.yml` automatically triggers the development deployment only after the named CI workflow succeeds on `main`.
- `.github/workflows/deploy-production.yml` is manual, takes an immutable 40-character SHA and uses the protected `production` environment.
- Repository secrets hold deployment hooks. They must never be committed or printed.

## Production promotion checklist

1. Confirm CI succeeded for the exact SHA.
2. Validate the development URL and run the upload/history smoke test.
3. Record release notes and the previous known-good SHA.
4. Approve the protected production environment.
5. Dispatch `Deploy production` with the exact SHA.
6. Run health and functional probes and record the deployment URL/evidence.

## Rollback

Use `Rollback production` with a previously tested full SHA and incident reference. The workflow verifies that the checkout resolves exactly to that SHA before triggering deployment. After rollback, run health, upload and history probes, then document root cause separately. Database migrations must be backward compatible; a destructive schema rollback requires an approved restore plan and is not automated by this demo.

## Required repository configuration

- `RENDER_DEV_DEPLOY_HOOK` secret.
- `RENDER_PRODUCTION_DEPLOY_HOOK` secret.
- `development` environment.
- Protected `production` environment with required reviewer.
- Branch protection requiring `CI` before merge.

Until an external run is observed, deployment is **prepared, not verified**. The exact public status is kept in `docs/SUBMISSION_STATUS.md`.

