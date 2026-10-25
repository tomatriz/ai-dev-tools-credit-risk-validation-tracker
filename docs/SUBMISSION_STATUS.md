# Submission Status

## Current state

**NOT SUBMITTED.** This file is updated only after external facts are verified.

| Item | Value |
|---|---|
| Public repository | https://github.com/tomatriz/ai-dev-tools-credit-risk-validation-tracker |
| Evaluated commit SHA | Pending final evidence commit; published CI-verified code SHA: `54cb7022aeb1ed6ce3fc7a469ce16d60303e4b44` |
| Public deployment | Pending external deployment |
| Tests | 21 backend + 2 responder + 8 frontend passed; frontend build passed; npm audit 0; public CI passed on `54cb7022aeb1ed6ce3fc7a469ce16d60303e4b44` |
| Course portal | Open; login required |
| Portal confirmation | Not saved yet |
| Time spent | Measured from work log before submission; never estimated retroactively |
| Certificate name | Must be read from authenticated profile or confirmed by user |
| Peer reviews | Three required after submission; not completed by this project build |

The hardened images built and the full stack became healthy. Upload/history and PostgreSQL persistence after backend restart were verified. The final controlled incident produced a real 503, fired `ValidationUserImpact`, invoked the bounded responder, verified recovery and completed with `INCIDENT_DEMO_OK`. Trace `8a4400d6ff2b8f3dcc38c75cca554bf2` resolved in Loki and Tempo, and the Prometheus incident gauge returned to zero.

## Evidence required before changing status

- Repository URL resolves publicly and matches the final SHA.
- Public application responds and completes a validation/history flow.
- CI links and local runtime evidence are recorded.
- The course portal displays a saved/received confirmation with the same repository and SHA.

Filling fields is not submission confirmation. If authentication, CAPTCHA or a profile name requires the learner, the final status remains `SUBMISSION BLOCKED` with that exact action listed.

