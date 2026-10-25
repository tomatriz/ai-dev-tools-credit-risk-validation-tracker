import { CalibrationChart } from './CalibrationChart'
import { StatusBadge } from './StatusBadge'
import { formatDate, formatNumber, formatPercent } from '../format'
import type { Validation } from '../types'

function Metric({ label, value, hint }: { label: string; value: string; hint: string }) {
  return (
    <div className="metric">
      <span>{label}</span>
      <strong>{value}</strong>
      <small>{hint}</small>
    </div>
  )
}

export function ValidationDetail({ validation }: { validation: Validation }) {
  const clean = validation.quality.null_count === 0 && validation.quality.duplicate_count === 0 && validation.quality.format_error_count === 0 && validation.quality.out_of_range_count === 0

  return (
    <div className="detail" aria-live="polite">
      <header className="detail__header">
        <div>
          <div className="eyebrow">Validation result</div>
          <h2>{validation.filename}</h2>
          <p>{formatDate(validation.created_at)} · ID {validation.id}</p>
        </div>
        <StatusBadge status={validation.status} />
      </header>

      <section className="metrics" aria-label="Validation metrics">
        <Metric label="Records" value={formatNumber(validation.record_count)} hint="Valid observations" />
        <Metric label="Average PD" value={formatPercent(validation.average_pd)} hint="Mean predicted risk" />
        <Metric label="Default rate" value={formatPercent(validation.observed_default_rate)} hint="Observed outcomes" />
        <Metric label="Brier score" value={validation.brier_score.toFixed(4)} hint="Lower is better" />
      </section>

      <div className="detail-grid">
        <section className="panel panel--chart" aria-labelledby="calibration-heading">
          <div className="panel__heading">
            <div><div className="eyebrow">Model performance</div><h3 id="calibration-heading">Calibration profile</h3></div>
            <span className="panel__meta">Equal-frequency groups</span>
          </div>
          <CalibrationChart data={validation.calibration} />
        </section>

        <aside className="panel quality" aria-labelledby="quality-heading">
          <div className="panel__heading">
            <div><div className="eyebrow">Input controls</div><h3 id="quality-heading">Data quality</h3></div>
            <span className={`quality__signal ${clean ? 'quality__signal--clean' : ''}`}>{clean ? 'Clean' : 'Review'}</span>
          </div>
          <dl className="quality__counts">
            <div><dt>Null values</dt><dd>{formatNumber(validation.quality.null_count)}</dd></div>
            <div><dt>Duplicate IDs</dt><dd>{formatNumber(validation.quality.duplicate_count)}</dd></div>
            <div><dt>Format errors</dt><dd>{formatNumber(validation.quality.format_error_count)}</dd></div>
            <div><dt>Out of range</dt><dd>{formatNumber(validation.quality.out_of_range_count)}</dd></div>
          </dl>
          <p className="quality__empty">{clean ? 'All structural input-quality checks passed.' : 'Review the counts above and the policy findings before relying on this result.'}</p>
        </aside>
      </div>

      <section className="panel findings" aria-labelledby="findings-heading">
        <div className="panel__heading">
          <div><div className="eyebrow">Policy assessment</div><h3 id="findings-heading">Findings</h3></div>
          <span className="panel__meta">{validation.findings.length} total</span>
        </div>
        {validation.findings.length ? (
          <ul className="finding-list">
            {validation.findings.map((finding, index) => (
              <li key={`${finding.code}-${index}`}>
                <StatusBadge status={finding.severity} />
                <div><strong>{finding.code.replaceAll('_', ' ')}</strong><p>{finding.message}</p></div>
              </li>
            ))}
          </ul>
        ) : <div className="empty-inline">No policy findings were returned.</div>}
      </section>

      {validation.policy?.disclaimer ? <p className="policy-disclaimer">{validation.policy.disclaimer}</p> : null}
      {validation.trace_id ? <p className="trace">Trace ID <code>{validation.trace_id}</code></p> : null}
    </div>
  )
}
