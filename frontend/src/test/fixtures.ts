export const validation = {
  id: 'validation-42',
  created_at: '2026-10-24T15:00:00Z',
  filename: 'synthetic_pd.csv',
  status: 'WARNING',
  record_count: 1000,
  average_pd: 0.073,
  observed_default_rate: 0.081,
  brier_score: 0.0642,
  calibration_gap: 0.012,
  quality: { row_count: 1000, null_count: 0, duplicate_count: 2, format_error_count: 0, out_of_range_count: 0 },
  calibration: [
    { decile: 1, record_count: 500, average_pd: 0.02, observed_default_rate: 0.024 },
    { decile: 2, record_count: 500, average_pd: 0.126, observed_default_rate: 0.138 },
  ],
  findings: [
    { code: 'DUPLICATE_IDS', severity: 'WARNING', message: 'Duplicate IDs require review.', actual: 2, threshold: 0 },
  ],
  policy: {
    disclaimer: 'Configurable demonstration policy; not a regulatory threshold.',
    pass_brier_max: 0.1,
    warning_brier_max: 0.2,
    pass_calibration_gap_max: 0.02,
    warning_calibration_gap_max: 0.05,
    warning_duplicate_rate_max: 0.01,
  },
  trace_id: 'abc123',
}
