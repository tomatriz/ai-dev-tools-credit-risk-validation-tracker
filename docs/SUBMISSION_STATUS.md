# Submission Status

## Current state

**SUBMITTED — CONFIRMED.** The authenticated course platform displayed its saved-submission confirmation and `STATUS: SUBMITTED` on 2026-10-26.

| Item | Value |
|---|---|
| Public repository | https://github.com/tomatriz/ai-dev-tools-credit-risk-validation-tracker |
| Runtime evidence | Production and persistence evidence is documented in the sanitized public transcript linked below |
| Evaluated release | Current public `main`; the authenticated portal stores the final submitted commit prefix |
| Production dashboard | https://crvt-dashboard.onrender.com |
| Production API | https://crvt-api.onrender.com |
| Development dashboard | https://tomatriz.github.io/ai-dev-tools-credit-risk-validation-tracker/ |
| OpenAPI UI | https://crvt-api.onrender.com/docs |
| Tests | 23 backend + 2 responder + 8 frontend passed in public CI; frontend build, Compose contract and Prometheus rules passed |
| CI/CD evidence | [CI run 40327236666](https://github.com/tomatriz/ai-dev-tools-credit-risk-validation-tracker/actions/runs/40327236666) and [automatic development deployment 40327289953](https://github.com/tomatriz/ai-dev-tools-credit-risk-validation-tracker/actions/runs/40327289953) |
| Manual production deployment | Render deploy `dep-dbf95mlg1s2s73eub47g`, successful for the runtime-evidence commit |
| Course portal | Saved and confirmed in the authenticated Project 1 form |
| Portal confirmation | Saved-submission thank-you message plus `STATUS: SUBMITTED` |
| Time spent | Supplied by the learner and retained only in the authenticated portal |
| Certificate name | Read from the authenticated profile and retained only in the authenticated portal |
| Peer reviews | Three required after submission; not completed by this project build |

The production API reported both application and database status `ok`. Public upload `3350f123-257e-474d-8f7d-376fdc82f171` persisted 12 records with status `WARNING` and trace `0e9756c6793b4f409bdb0c369bcd9ed1`. Validation `87a30b4f-6257-4eff-b571-1efc94554dec` remained retrievable after the API redeployment, proving managed PostgreSQL persistence across releases. The automatic development site returned HTTP 200 and its browser-origin preflight was explicitly allowed by the API.

The sanitized command-result transcript is stored in `evidence/PUBLIC_DEPLOYMENT_2026-10-25.md`.

The final controlled local incident produced a real 503, fired `ValidationUserImpact`, invoked the bounded responder, verified recovery and completed with `INCIDENT_DEMO_OK`. Trace `8a4400d6ff2b8f3dcc38c75cca554bf2` resolved in Loki and Tempo, and the Prometheus incident gauge returned to zero.

## Submission verification

- The saved form displays the public repository URL and evaluated release prefix.
- The course page displays both the saved-submission confirmation and `STATUS: SUBMITTED`.
- Personal profile details and the learner-supplied time are intentionally not duplicated in this public repository.

Three peer reviews remain a separate mandatory learner action. They are not claimed complete.

