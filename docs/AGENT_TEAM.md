# Agent Team and Collaboration Process

## Roles

| Role | Responsibility | Deliverables | Guardrails |
|---|---|---|---|
| Lead Software Engineer | Architecture, integration and final decisions | Working integrated repository | Reviews all shared contracts |
| Product Manager | User stories, acceptance criteria and tracker | Spec and issues | Does not mark work complete without evidence |
| Backend Engineer | API, validation engine and persistence | Backend and tests | Deterministic calculations only |
| Frontend Engineer | Accessible dashboard and history UX | Frontend and tests | No mocked final results |
| QA Engineer | Independent functional and failure testing | Test/evaluation evidence | Records failures honestly |
| DevOps/SRE Engineer | Containers, delivery, telemetry and incident response | Compose, workflows, runbooks | Bounded remediation; no arbitrary execution |
| Technical Documentation Specialist | Reproducible docs and learning material | English academic docs; Spanish learning guide | Sanitizes private/confidential material |

## Coordination

The Lead converts the official rubric into tasks. Parallel agents own separate directories, report changed files and commands, and hand results back for integration. The Lead resolves contract conflicts. QA then runs the full system independently; defects return to the owning engineer. SRE runs the incident drill only after the normal user journey passes. Documentation cites observed evidence and distinguishes verified, partial, missing and not-verifiable capabilities.

## Real agent activity

The project was started in Codex with parallel specialized subagents for backend, frontend and documentation work. Their outputs are integrated and independently checked by the lead. GitHub Issue links and agent comments will be added after the public repository is available; the local handoff log remains in `docs/TASK_TRACKER.md`.
