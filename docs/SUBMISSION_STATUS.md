# Submission Status

## Current state

**NOT SUBMITTED.** The application, repository, deployment and academic evidence are ready. The course form has not yet displayed a saved/received confirmation, so this document does not claim submission.

| Item | Value |
|---|---|
| Public repository | https://github.com/tomatriz/ai-dev-tools-credit-risk-validation-tracker |
| Runtime-evidence commit | `bea7a600075eecba7754c9894e61b483ebb2701b` |
| Final evaluated SHA | Pending final documentation release and course-form save |
| Production dashboard | https://crvt-dashboard.onrender.com |
| Production API | https://crvt-api.onrender.com |
| Development dashboard | https://tomatriz.github.io/ai-dev-tools-credit-risk-validation-tracker/ |
| OpenAPI UI | https://crvt-api.onrender.com/docs |
| Tests | 23 backend + 2 responder + 8 frontend passed in public CI; frontend build, Compose contract and Prometheus rules passed |
| CI/CD evidence | [CI run 40245553956](https://github.com/tomatriz/ai-dev-tools-credit-risk-validation-tracker/actions/runs/40245553956) and [automatic development deployment 40245588041](https://github.com/tomatriz/ai-dev-tools-credit-risk-validation-tracker/actions/runs/40245588041) |
| Manual production deployment | Render deploy `dep-dbf95mlg1s2s73eub47g`, successful for the runtime-evidence commit |
| Course portal | Not saved/submitted yet; UI automation could not safely bind to the authenticated Windows browser |
| Portal confirmation | Not saved yet |
| Time spent | Measured from work log before submission; never estimated retroactively |
| Certificate name | Must be read from authenticated profile or confirmed by user |
| Peer reviews | Three required after submission; not completed by this project build |

The production API reported both application and database status `ok`. Public upload `3350f123-257e-474d-8f7d-376fdc82f171` persisted 12 records with status `WARNING` and trace `0e9756c6793b4f409bdb0c369bcd9ed1`. Validation `87a30b4f-6257-4eff-b571-1efc94554dec` remained retrievable after the API redeployment, proving managed PostgreSQL persistence across releases. The automatic development site returned HTTP 200 and its browser-origin preflight was explicitly allowed by the API.

The sanitized command-result transcript is stored in `evidence/PUBLIC_DEPLOYMENT_2026-10-25.md`.

The final controlled local incident produced a real 503, fired `ValidationUserImpact`, invoked the bounded responder, verified recovery and completed with `INCIDENT_DEMO_OK`. Trace `8a4400d6ff2b8f3dcc38c75cca554bf2` resolved in Loki and Tempo, and the Prometheus incident gauge returned to zero.

## Evidence required before changing status

- Repository URL resolves publicly and matches the final SHA.
- Public application responds and completes a validation/history flow. **Verified.**
- CI links and local runtime evidence are recorded.
- The course portal displays a saved/received confirmation with the same repository and SHA.

Filling fields is not submission confirmation. If authentication, CAPTCHA or a profile name requires the learner, the final status remains `SUBMISSION BLOCKED` with that exact action listed.

