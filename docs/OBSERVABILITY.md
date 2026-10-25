# Observability

## Instrumented user journey

The observed journey is `POST /api/v1/validations`: a user uploads a CSV, the API validates it, computes metrics and persists a result. This is a meaningful function, not an infrastructure-only health signal.

## Correlation model

For each HTTP request the backend obtains the active OpenTelemetry trace ID (or creates a request correlation ID when tracing is unavailable). The same ID appears in:

- the distributed trace exported through OTLP to Tempo;
- structured JSON application/request logs collected by Alloy into Loki;
- the `X-Trace-ID` response header, allowing a user-visible failure to be located;
- log fields surrounding metric increments and validation outcomes.

Metrics do not carry trace IDs as labels because that would create unbounded cardinality. Correlation begins from the response/log trace ID and follows Grafana's Loki-to-Tempo derived field. Metrics establish time and outcome, logs identify the request, and Tempo shows spans.

## Signals

- `crvt_validation_requests_total{outcome="success|incident_failure|validation_error|capacity_reached|server_error"}`: user-journey outcomes.
- `crvt_validation_incident_active`: resolvable user-impact gauge used by `ValidationUserImpact`.
- standard process/runtime metrics from the Prometheus client.
- structured request, successful upload, incident rejection, incident state and remediation events.
- an OpenTelemetry span for each incoming FastAPI request, covering validation processing.

CSV contents, observation identifiers, database credentials, tokens and customer data are excluded from telemetry. Safe metadata such as record counts and classification status may be logged.

## Collection and UI

- Prometheus scrapes `/metrics` and evaluates `observability/prometheus/alerts.yml`.
- Tempo receives OTLP HTTP/gRPC traces.
- The backend writes JSON logs to the shared `app_logs` volume; Alloy tails them into Loki.
- Grafana provisions all three data sources and the `Credit Risk Validation Overview` dashboard.

## Verification

1. Start Compose and upload `sample-data/valid_portfolio.csv`.
2. Copy `X-Trace-ID` from the response.
3. In Grafana Explore, query Loki with `{job="crvt-backend"} |= "<trace-id>"`.
4. Open the derived TraceID link and confirm the matching trace in Tempo.
5. Query `sum by (outcome) (crvt_validation_requests_total)` in Prometheus or Grafana.

If an exporter is unavailable, the application continues serving requests and logs the exporter error; telemetry must not become a single point of failure.

