export type ValidationStatus = 'PASS' | 'WARNING' | 'FAIL'

export interface DataQuality {
  row_count: number
  null_count: number
  duplicate_count: number
  format_error_count: number
  out_of_range_count: number
}

export interface CalibrationBucket {
  decile: number
  record_count: number
  average_pd: number
  observed_default_rate: number
}

export interface Finding {
  code: string
  severity: ValidationStatus
  message: string
  actual: number
  threshold: number | null
}

export interface DemonstrationPolicy {
  disclaimer: string
  pass_brier_max: number
  warning_brier_max: number
  pass_calibration_gap_max: number
  warning_calibration_gap_max: number
  warning_duplicate_rate_max: number
}

export interface Validation {
  id: string
  created_at: string
  filename: string
  status: ValidationStatus
  record_count: number
  average_pd: number
  observed_default_rate: number
  brier_score: number
  calibration_gap: number
  quality: DataQuality
  calibration: CalibrationBucket[]
  findings: Finding[]
  policy?: DemonstrationPolicy
  trace_id?: string
}

export interface ApiErrorPayload {
  detail?: string | Array<{ msg?: string }> | { message?: string; code?: string }
  message?: string
}
