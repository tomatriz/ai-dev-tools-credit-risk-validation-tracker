import type { ValidationStatus } from '../types'

export function StatusBadge({ status }: { status: ValidationStatus }) {
  return (
    <span className={`status status--${status.toLowerCase()}`} aria-label={`Status: ${status}`}>
      <span className="status__dot" aria-hidden="true" />
      {status}
    </span>
  )
}
