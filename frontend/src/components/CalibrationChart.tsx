import { formatPercent } from '../format'
import type { CalibrationBucket } from '../types'

export function CalibrationChart({ data }: { data: CalibrationBucket[] }) {
  if (!data.length) return <div className="empty-inline">No calibration groups were returned.</div>

  const width = 720
  const height = 300
  const margin = { top: 20, right: 24, bottom: 48, left: 56 }
  const innerW = width - margin.left - margin.right
  const innerH = height - margin.top - margin.bottom
  const max = Math.max(0.01, ...data.flatMap((item) => [item.average_pd, item.observed_default_rate])) * 1.12
  const x = (index: number) => margin.left + (index / Math.max(data.length - 1, 1)) * innerW
  const y = (value: number) => margin.top + innerH - (value / max) * innerH
  const points = (field: 'average_pd' | 'observed_default_rate') =>
    data.map((item, index) => `${x(index)},${y(item[field])}`).join(' ')
  const ticks = [0, 0.25, 0.5, 0.75, 1]

  return (
    <div className="chart-wrap">
      <div className="chart-legend" aria-hidden="true">
        <span><i className="legend-line legend-line--expected" />Average PD</span>
        <span><i className="legend-line legend-line--observed" />Observed defaults</span>
      </div>
      <svg
        className="chart"
        role="img"
        aria-labelledby="chart-title chart-description"
        viewBox={`0 0 ${width} ${height}`}
      >
        <title id="chart-title">Calibration by risk decile</title>
        <desc id="chart-description">
          Average predicted probability of default compared with the observed default rate for each risk decile.
        </desc>
        {ticks.map((tick) => {
          const value = tick * max
          return (
            <g key={tick}>
              <line className="chart__grid" x1={margin.left} x2={width - margin.right} y1={y(value)} y2={y(value)} />
              <text className="chart__label" x={margin.left - 12} y={y(value) + 4} textAnchor="end">
                {formatPercent(value, 0)}
              </text>
            </g>
          )
        })}
        <polyline className="chart__line chart__line--expected" points={points('average_pd')} />
        <polyline className="chart__line chart__line--observed" points={points('observed_default_rate')} />
        {data.map((item, index) => (
          <g key={item.decile}>
            <circle className="chart__point chart__point--expected" cx={x(index)} cy={y(item.average_pd)} r="4" />
            <circle className="chart__point chart__point--observed" cx={x(index)} cy={y(item.observed_default_rate)} r="4" />
            <text className="chart__label" x={x(index)} y={height - 18} textAnchor="middle">D{item.decile}</text>
            <title>{`Decile ${item.decile}: average PD ${formatPercent(item.average_pd)}, observed ${formatPercent(item.observed_default_rate)}, ${item.record_count} records`}</title>
          </g>
        ))}
      </svg>
      <div className="chart-table-wrap">
        <table className="chart-table">
          <caption className="visually-hidden">Calibration values by decile</caption>
          <thead><tr><th>Decile</th><th>Records</th><th>Avg. PD</th><th>Observed</th></tr></thead>
          <tbody>
            {data.map((item) => (
              <tr key={item.decile}>
                <td>D{item.decile}</td><td>{item.record_count}</td><td>{formatPercent(item.average_pd)}</td><td>{formatPercent(item.observed_default_rate)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
