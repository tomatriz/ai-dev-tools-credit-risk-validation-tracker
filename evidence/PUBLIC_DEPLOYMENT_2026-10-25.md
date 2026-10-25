# Public deployment evidence — 2026-10-25

All values below were observed against public endpoints or public GitHub Actions. No credentials, tokens, CSV rows or customer data are included.

## Immutable revision

- Runtime-evidence commit: `bea7a600075eecba7754c9894e61b483ebb2701b`
- GitHub CI: https://github.com/tomatriz/ai-dev-tools-credit-risk-validation-tracker/actions/runs/40245553956 — successful
- Automatic development deployment: https://github.com/tomatriz/ai-dev-tools-credit-risk-validation-tracker/actions/runs/40245588041 — successful in 19 seconds
- Manual Render API deployment: `dep-dbf95mlg1s2s73eub47g` — successful

## Endpoints

- Production dashboard: https://crvt-dashboard.onrender.com — HTTP 200
- Production API health: https://crvt-api.onrender.com/health — application `ok`, database `ok`
- OpenAPI UI: https://crvt-api.onrender.com/docs — HTTP 200
- Automatic development dashboard: https://tomatriz.github.io/ai-dev-tools-credit-risk-validation-tracker/ — HTTP 200 with the repository-specific asset base path

## Functional smoke test

Uploading the synthetic `sample-data/valid_portfolio.csv` directly to the public API produced:

```text
validation_id=3350f123-257e-474d-8f7d-376fdc82f171
status=WARNING
record_count=12
trace_id=0e9756c6793b4f409bdb0c369bcd9ed1
```

The `WARNING` classification is the deterministic result of configurable demonstration policy and is not a regulatory conclusion.

Validation `87a30b4f-6257-4eff-b571-1efc94554dec`, created before the API deployment, was retrieved successfully afterwards with status `WARNING`. This verifies persistence in the managed PostgreSQL service across application deployments.

## Browser-origin contract

An OPTIONS preflight from origin `https://tomatriz.github.io` to the production validations endpoint returned HTTP 200 and:

```text
Access-Control-Allow-Origin: https://tomatriz.github.io
```

This verifies that the automatically deployed development dashboard is permitted to call the production demonstration API.

## Known service limitation

The deployment uses Render free services. The managed PostgreSQL resource reported expiration on 2026-11-24 unless upgraded or migrated. Free web services may cold-start.
