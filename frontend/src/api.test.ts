import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createValidation, listValidations, normalizeValidation } from './api'
import { validation } from './test/fixtures'

describe('API client', () => {
  beforeEach(() => vi.restoreAllMocks())

  it('normalizes a validation resource', () => {
    const result = normalizeValidation(validation)
    expect(result.status).toBe('WARNING')
    expect(result.brier_score).toBe(0.0642)
    expect(result.calibration).toHaveLength(2)
  })

  it('reads list envelopes from the live history endpoint', async () => {
    const fetchMock = vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response(JSON.stringify({ items: [validation] }), { status: 200 }),
    )
    const result = await listValidations()
    expect(fetchMock).toHaveBeenCalledWith('/api/v1/validations', { signal: undefined })
    expect(result[0].filename).toBe('synthetic_pd.csv')
  })

  it('uploads CSV as multipart data', async () => {
    const fetchMock = vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response(JSON.stringify(validation), { status: 201 }),
    )
    await createValidation(new File(['id,pd'], 'risk.csv', { type: 'text/csv' }))
    const [, request] = fetchMock.mock.calls[0]
    expect(request?.method).toBe('POST')
    expect(request?.body).toBeInstanceOf(FormData)
    expect((request?.body as FormData).get('file')).toBeInstanceOf(File)
  })

  it('returns actionable API errors', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response(JSON.stringify({ detail: 'Missing required column: predicted_pd' }), { status: 422 }),
    )
    await expect(createValidation(new File(['bad'], 'bad.csv'))).rejects.toEqual(
      expect.objectContaining({ status: 422, message: 'Missing required column: predicted_pd' }),
    )
  })
})
