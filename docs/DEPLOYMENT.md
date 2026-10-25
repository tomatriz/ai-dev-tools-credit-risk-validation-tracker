# Deployment and Release Operations

## Local deployment

Requirements: Docker Desktop with Compose v2. From the repository root:

```bash
cp .env.example .env
docker compose up --build
```

Open the dashboard at `http://localhost:3000`, API documentation at `http://localhost:8000/docs`, Grafana at `http://localhost:3001`, Prometheus at `http://localhost:9090`, and Alertmanager at `http://localhost:9093`.

If a default port is already used, copy `.env.example` and change the corresponding `CRVT_*_PORT` value; container-to-container contracts do not change.

## Public deployments

Production runs on Render from `render.yaml`: [dashboard](https://crvt-dashboard.onrender.com), [API](https://crvt-api.onrender.com), and managed PostgreSQL. Both web services and the database use the free plan. The Render dashboard proxies `/api/v1` to the API from Nginx. Health, OpenAPI, a real sample upload, history retrieval and persistence across an API redeployment were verified on 2026-10-25.

Development is the [GitHub Pages dashboard](https://tomatriz.github.io/ai-dev-tools-credit-risk-validation-tracker/). `.github/workflows/deploy-dev.yml` runs only after the named CI workflow succeeds on `main`, checks out that exact tested SHA, builds with the public API origin and project base path, and deploys through GitHub's OIDC-backed Pages action. [Run 40245588041](https://github.com/tomatriz/ai-dev-tools-credit-risk-validation-tracker/actions/runs/40245588041) is the observed automatic deployment.

The local Grafana/Loki/Tempo/Prometheus demonstration is intentionally Compose-based. A public production deployment should use managed or separately secured telemetry endpoints and must not expose operational controls publicly.

## CI/CD stages

- `.github/workflows/ci.yml` runs backend, responder and frontend tests plus build/config validation on every pull request and `main` push.
- `.github/workflows/deploy-dev.yml` automatically deploys the tested frontend to GitHub Pages only after the named CI workflow succeeds on `main`.
- `.github/workflows/deploy-production.yml` is manual, takes an immutable 40-character SHA and uses the protected `production` environment.
- The observed production promotion used the official Render CLI with an immutable SHA because the current public-repository Render connection does not expose a repository deploy hook to GitHub Actions.
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

## Repository configuration

- GitHub Pages uses `build_type=workflow`; no deploy secret is required for development.
- `RENDER_PRODUCTION_DEPLOY_HOOK` is optional for the GitHub production/rollback workflows. Until configured, production promotion uses the authenticated official Render CLI and an immutable tested SHA.
- The `production` GitHub environment should require a reviewer before enabling its hook-based path.
- Branch protection should require `CI` before merge.

The production and development URLs are verified. The exact current evidence, service limitation and submission state are kept in `docs/SUBMISSION_STATUS.md`. The free Render PostgreSQL instance reports an expiration date of 2026-11-24; preserve or migrate evidence before then.

