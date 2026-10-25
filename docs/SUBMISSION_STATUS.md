# Submission Status

## Current state

**NOT SUBMITTED.** This file is updated only after external facts are verified.

| Item | Value |
|---|---|
| Public repository | Pending publication |
| Evaluated commit SHA | Pending final verified commit |
| Public deployment | Pending external deployment |
| Tests | 21 backend + 2 responder + 8 frontend passed; frontend build passed; npm audit 0 |
| Course portal | Open; login required |
| Portal confirmation | Not saved yet |
| Time spent | Measured from work log before submission; never estimated retroactively |
| Certificate name | Must be read from authenticated profile or confirmed by user |
| Peer reviews | Three required after submission; not completed by this project build |

Local full-stack upload/history/persistence was verified before the final hardening changes. Compose configuration validates after hardening, but Docker Desktop is currently unavailable on the host, so the final image rebuild and alert-to-responder drill are not yet claimed.

## Evidence required before changing status

- Repository URL resolves publicly and matches the final SHA.
- Public application responds and completes a validation/history flow.
- CI links and local runtime evidence are recorded.
- The course portal displays a saved/received confirmation with the same repository and SHA.

Filling fields is not submission confirmation. If authentication, CAPTCHA or a profile name requires the learner, the final status remains `SUBMISSION BLOCKED` with that exact action listed.

