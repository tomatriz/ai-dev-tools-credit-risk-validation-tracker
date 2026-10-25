import { formatDate, formatPercent } from '../format'
import type { Validation } from '../types'
import { StatusBadge } from './StatusBadge'

interface HistoryProps {
  items: Validation[]
  activeId?: string
  loading: boolean
  onSelect: (id: string) => void
}

export function History({ items, activeId, loading, onSelect }: HistoryProps) {
  return (
    <section className="history" aria-labelledby="history-title">
      <div className="history__heading">
        <div><div className="eyebrow">Audit trail</div><h2 id="history-title">Validation history</h2></div>
        <span className="history__count">{items.length}</span>
      </div>
      {loading ? (
        <div className="history__loading"><span className="spinner" /> Loading history…</div>
      ) : items.length ? (
        <ul className="history__list">
          {items.map((item) => (
            <li key={item.id}>
              <button className={item.id === activeId ? 'history-item history-item--active' : 'history-item'} onClick={() => onSelect(item.id)}>
                <span className="history-item__top"><strong>{item.filename}</strong><StatusBadge status={item.status} /></span>
                <span className="history-item__metrics">
                  <span>{item.record_count.toLocaleString()} rows</span>
                  <span>{formatPercent(item.average_pd)} avg. PD</span>
                </span>
                <time dateTime={item.created_at}>{formatDate(item.created_at)}</time>
              </button>
            </li>
          ))}
        </ul>
      ) : (
        <div className="history__empty">
          <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 5h18M5 5v15h14V5M9 9h6m-6 4h6" /></svg>
          <strong>No validations yet</strong>
          <span>Your completed runs will appear here.</span>
        </div>
      )}
    </section>
  )
}
