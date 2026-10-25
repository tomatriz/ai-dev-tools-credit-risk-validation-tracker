# Product Specification

## Product

Credit Risk Validation Tracker is an educational full-stack application for validating synthetic probability-of-default (PD) datasets and retaining an auditable validation history.

## Users and problem

Model validators and risk analysts need a reproducible way to inspect input quality, compare predicted PD with observed outcomes, review calibration, and share evidence. Spreadsheet-only workflows make rules, calculations and operational failures hard to test and trace.

## Demonstration policy

The application does **not** encode regulatory thresholds. PASS/WARNING/FAIL rules are configurable example policy. A real institution must approve thresholds under its own model-risk framework.

## User stories and acceptance criteria

### US-01 Upload and validate

As a validator, I can upload a CSV containing `observation_id`, `predicted_pd`, and `default_flag` so that I receive deterministic results.

- Reject missing required columns, empty files, invalid types, PD outside `[0,1]`, and default flags outside `{0,1}`.
- Report null and duplicate counts.
- Calculate record count, average PD, observed default rate, and Brier score.
- Return ten or fewer equal-frequency risk groups with expected and observed rates.
- Assign PASS/WARNING/FAIL using documented configurable example rules.

### US-02 Interpret and revisit

As a validator, I can see headline metrics, findings, data-quality results and a calibration chart, then reopen prior validations.

- The frontend uses the live API, not static validation results.
- Completed validations persist in PostgreSQL and remain after application restart.

### US-03 Operate safely

As an operator, I can reproduce a user-impacting validation failure, receive an alert, and invoke a bounded responder that diagnoses, performs one authorized remediation, and verifies recovery.

- Normal uploads emit a metric, structured logs, and traces sharing a trace ID.
- A safe incident switch causes upload requests to fail without corrupting data.
- The responder may only disable that switch through the internal recovery endpoint and must verify health and a probe validation.

## Out of scope

Real customer data, regulatory conclusions, model approval decisions, authentication/authorization for production, model training, and autonomous infrastructure changes.

## Public task tracker

The canonical tracker will be GitHub Issues in the public repository. Issues must include these acceptance criteria and be referenced in commits or comments. Until repository creation/authentication is available, `docs/TASK_TRACKER.md` is the auditable local source that will be mirrored to GitHub.
