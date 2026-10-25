# Testing Strategy and Evidence

## Test pyramid

1. **Backend unit tests** cover CSV parsing, input constraints, quality checks, deterministic metrics, calibration buckets and example policy classification.
2. **Backend integration tests** exercise the FastAPI contract and database persistence through HTTP using an isolated SQLite database.
3. **Frontend component tests** exercise upload, error, results and history behavior with the network boundary mocked, while the production build targets the real API.
4. **Responder tests** verify that only the allow-listed alert can trigger diagnosis, recovery and a functional probe.
5. **Compose smoke and incident tests** run all real services, submit a CSV, query persisted history and demonstrate the Prometheus-to-responder loop.

## One-command checks

PowerShell:

```powershell
./scripts/test.ps1
```

GNU Make:

```bash
make test
```

Full system:

```bash
docker compose up --build -d
curl http://localhost:8000/health
curl -F "file=@sample-data/valid_portfolio.csv" http://localhost:8000/api/v1/validations
curl http://localhost:8000/api/v1/validations
```

## Persistence check

1. Create a validation and note its `id`.
2. Run `docker compose restart backend db` (do not use `down -v`).
3. Request `GET /api/v1/validations/{id}` and confirm the same resource is returned.

The named `postgres_data` volume is deliberately retained by `docker compose down`. `docker compose down -v` is destructive and should be used only when intentionally resetting local data.

## Incident test

With the stack healthy:

```powershell
./scripts/demo-incident.ps1
```

Success requires all of the following: the upload fails while the incident flag is enabled; the Prometheus alert fires; Alertmanager wakes the responder; the responder reads diagnostic state; it performs the single allow-listed recovery action; health and a synthetic validation probe succeed; the original sample succeeds again.

## Evidence policy

Observed command output belongs in `evidence/` or a linked CI run. A checked-in test is not proof that it passed. `docs/EVALUATION.md` distinguishes implementation evidence from runtime evidence and is updated after final verification.

## Latest observed results

On 2026-10-25, `scripts/test.ps1` completed successfully from the repository root:

- backend: 21 passed, with one third-party Starlette deprecation warning;
- bounded responder: 2 passed;
- frontend: 8 passed in two files;
- TypeScript/Vite production build: passed;
- `npm ci` audit: 0 vulnerabilities.

`docker compose config --quiet` also passed. The hardened backend, frontend and responder images rebuilt successfully. The complete stack became healthy on alternate loopback ports, an upload through the frontend proxy returned 201, and validation `89bcf4d7-f3f5-45c9-943f-deb77b5bff30` remained available after a backend restart. The final incident script observed the controlled 503, verified alert-to-responder remediation, completed a post-recovery upload and emitted `INCIDENT_DEMO_OK`.

