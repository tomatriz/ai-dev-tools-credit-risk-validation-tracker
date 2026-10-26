# Security Review

## Scope and method

A repository-wide static security review covered the 87 current source, configuration, workflow, test, sample and documentation files before publication. An independent baseline reviewer and architecture reviewer were reconciled by the lead. The review used no production service, live secret, customer data or destructive denial-of-service payload.

The retained Codex Security scan ID is `e98a5d3f-6a13-42d6-9540-97f975c1fff0`. Its local immutable report is outside the public repository because it belongs to the tool's scan store.

## Results and remediation

The scan found five source-backed issues in the pre-hardening snapshot: two high-severity resource-exhaustion paths, one medium workflow-input injection, and two low-severity local-demo configuration exposures. The working tree then received these controls:

- unmatched HTTP paths use one bounded Prometheus label;
- actual request bytes are limited before multipart parsing;
- CSV rows and retained error details are capped and parsed without materializing all raw rows;
- retained validation history has a configurable capacity;
- deployment inputs are treated as environment data and validated in an unprivileged job before a protected deploy job;
- Compose ports bind to loopback and direct service startup rejects placeholder operational credentials unless explicit demo mode is enabled;
- the responder container runs as a non-root user;
- the alert now uses a resolvable incident-active gauge.

Regression tests cover unmatched metric labels, pre-parser body rejection, row/error caps and gauge reset. The complete one-command suite passed after these changes. The hardened containers were rebuilt and the end-to-end incident rerun completed with `INCIDENT_DEMO_OK`.

## Secret and data review

No live API key, deploy hook, private key, customer dataset or confidential client code was found. Values such as `local-demo-token`, `local-alert-token`, `local_demo_only` and test tokens are explicit local placeholders. `.env` is ignored; non-local deployment must provide secret values through the platform.

## Boundary

This is an educational synthetic-data application, not a production security certification. Production requires identity, RBAC, TLS, managed secrets, rate limiting at the gateway, retention governance, audit durability, backup controls and institutional approval.
