import type { ApiErrorPayload, Validation, ValidationStatus } from './types'

const API_ROOT = (import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_URL || '/api/v1').replace(/\/$/, '')

export class ApiError extends Error {
  readonly status: number

  constructor(message: string, status: number) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}

function errorMessage(payload: ApiErrorPayload, fallback: string): string {
  if (typeof payload.detail === 'string') return payload.detail
  if (Array.isArray(payload.detail)) {
    const messages = payload.detail.map((item) => item.msg).filter(Boolean)
    if (messages.length) return messages.join('; ')
  }
  if (payload.detail && !Array.isArray(payload.detail) && typeof payload.detail === 'object' && payload.detail.message) return payload.detail.message
  return payload.message || fallback
}

async function parseResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    let payload: ApiErrorPayload = {}
    try {
      payload = (await response.json()) as ApiErrorPayload
    } catch {
      // Preserve an actionable status-based fallback if the upstream sent no JSON.
    }
    throw new ApiError(errorMessage(payload, `Request failed (${response.status})`), response.status)
  }
  return (await response.json()) as T
}

function statusOf(value: unknown): ValidationStatus {
  const status = String(value || '').toUpperCase()
  return status === 'PASS' || status === 'WARNING' || status === 'FAIL' ? status : 'WARNING'
}

function numberOf(value: unknown): number {
  const parsed = Number(value)
  return Number.isFinite(parsed) ? parsed : 0
}

// Keeps the UI resilient to a list envelope while preserving one canonical app type.
export function normalizeValidation(raw: Record<string, unknown>): Validation {
  const quality = (raw.quality || {}) as Record<string, unknown>
  const policy = raw.policy as Record<string, unknown> | undefined
  const calibration = Array.isArray(raw.calibration) ? raw.calibration : []
  const findings = Array.isArray(raw.findings) ? raw.findings : []

  return {
    id: String(raw.id ?? ''),
    created_at: String(raw.created_at ?? new Date(0).toISOString()),
    filename: String(raw.filename ?? 'dataset.csv'),
    status: statusOf(raw.status),
    record_count: numberOf(raw.record_count),
    average_pd: numberOf(raw.average_pd),
    observed_default_rate: numberOf(raw.observed_default_rate),
    brier_score: numberOf(raw.brier_score),
    calibration_gap: numberOf(raw.calibration_gap),
    quality: {
      row_count: numberOf(quality.row_count),
      null_count: numberOf(quality.null_count),
      duplicate_count: numberOf(quality.duplicate_count),
      format_error_count: numberOf(quality.format_error_count),
      out_of_range_count: numberOf(quality.out_of_range_count),
    },
    calibration: calibration.map((item) => {
      const bucket = item as Record<string, unknown>
      return {
        decile: numberOf(bucket.decile),
        record_count: numberOf(bucket.record_count),
        average_pd: numberOf(bucket.average_pd),
        observed_default_rate: numberOf(bucket.observed_default_rate),
      }
    }),
    findings: findings.map((item) => {
      const finding = item as Record<string, unknown>
      return {
        code: String(finding.code ?? 'FINDING'),
        severity: statusOf(finding.severity),
        message: String(finding.message ?? 'Review this validation finding.'),
        actual: numberOf(finding.actual),
        threshold: finding.threshold == null ? null : numberOf(finding.threshold),
      }
    }),
    policy: policy ? {
      disclaimer: String(policy.disclaimer ?? ''),
      pass_brier_max: numberOf(policy.pass_brier_max),
      warning_brier_max: numberOf(policy.warning_brier_max),
      pass_calibration_gap_max: numberOf(policy.pass_calibration_gap_max),
      warning_calibration_gap_max: numberOf(policy.warning_calibration_gap_max),
      warning_duplicate_rate_max: numberOf(policy.warning_duplicate_rate_max),
    } : undefined,
    trace_id: raw.trace_id ? String(raw.trace_id) : undefined,
  }
}

export async function listValidations(signal?: AbortSignal): Promise<Validation[]> {
  const payload = await parseResponse<unknown>(await fetch(`${API_ROOT}/validations`, { signal }))
  const rows = Array.isArray(payload)
    ? payload
    : ((payload as { items?: unknown[]; validations?: unknown[] }).items ||
      (payload as { validations?: unknown[] }).validations ||
      [])
  return rows.map((row) => normalizeValidation(row as Record<string, unknown>))
}

export async function getValidation(id: string, signal?: AbortSignal): Promise<Validation> {
  const payload = await parseResponse<Record<string, unknown>>(
    await fetch(`${API_ROOT}/validations/${encodeURIComponent(id)}`, { signal }),
  )
  return normalizeValidation(payload)
}

export async function createValidation(file: File): Promise<Validation> {
  const body = new FormData()
  body.append('file', file)
  const payload = await parseResponse<Record<string, unknown>>(
    await fetch(`${API_ROOT}/validations`, { method: 'POST', body }),
  )
  return normalizeValidation(payload)
}
