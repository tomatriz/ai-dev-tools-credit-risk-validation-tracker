import { beforeEach, describe, expect, it, vi } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import App from './App'
import { validation } from './test/fixtures'

function jsonResponse(body: unknown, status = 200) {
  return Promise.resolve(new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json' } }))
}

describe('validation dashboard', () => {
  beforeEach(() => vi.restoreAllMocks())

  it('loads persistent history and renders validation evidence', async () => {
    vi.spyOn(globalThis, 'fetch')
      .mockImplementationOnce(() => jsonResponse({ items: [validation], total: 1, limit: 20, offset: 0 }))
      .mockImplementationOnce(() => jsonResponse(validation))
    render(<App />)

    expect(await screen.findByRole('heading', { name: 'synthetic_pd.csv' })).toBeInTheDocument()
    expect(screen.getByText('1,000')).toBeInTheDocument()
    expect(screen.getByText('7.30%')).toBeInTheDocument()
    expect(screen.getByRole('img', { name: /calibration by risk decile/i })).toBeInTheDocument()
    expect(screen.getByText('Duplicate IDs require review.')).toBeInTheDocument()
  })

  it('uploads a selected CSV and shows the completed result', async () => {
    const fetchMock = vi.spyOn(globalThis, 'fetch')
      .mockImplementationOnce(() => jsonResponse([]))
      .mockImplementationOnce(() => jsonResponse(validation, 201))
    const user = userEvent.setup()
    render(<App />)
    await screen.findByText('No validations yet')

    const file = new File(['observation_id,predicted_pd,default_flag\n1,0.1,0'], 'synthetic_pd.csv', { type: 'text/csv' })
    await user.upload(screen.getByLabelText('Choose CSV file'), file)
    await user.click(screen.getByRole('button', { name: 'Run validation' }))

    expect(await screen.findByText(/was validated and added to history/i)).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'synthetic_pd.csv' })).toBeInTheDocument()
    const [, request] = fetchMock.mock.calls[1]
    expect(request?.method).toBe('POST')
  })

  it('surfaces user-impacting service failures', async () => {
    vi.spyOn(globalThis, 'fetch')
      .mockImplementationOnce(() => jsonResponse([]))
      .mockImplementationOnce(() => jsonResponse({ detail: 'Incident simulation active' }, 503))
    const user = userEvent.setup()
    render(<App />)
    await screen.findByText('No validations yet')
    const file = new File(['header'], 'risk.csv', { type: 'text/csv' })
    await user.upload(screen.getByLabelText('Choose CSV file'), file)
    await user.click(screen.getByRole('button', { name: 'Run validation' }))

    expect(await screen.findByRole('alert')).toHaveTextContent('temporarily unavailable')
  })

  it('reopens a history item through its detail endpoint', async () => {
    const second = { ...validation, id: 'validation-99', filename: 'older.csv' }
    const fetchMock = vi.spyOn(globalThis, 'fetch')
      .mockImplementationOnce(() => jsonResponse([validation, second]))
      .mockImplementationOnce(() => jsonResponse(validation))
      .mockImplementationOnce(() => jsonResponse(second))
    const user = userEvent.setup()
    render(<App />)
    await screen.findByRole('heading', { name: 'synthetic_pd.csv' })
    await user.click(screen.getByRole('button', { name: /older.csv/i }))
    await waitFor(() => expect(fetchMock).toHaveBeenLastCalledWith('/api/v1/validations/validation-99', { signal: undefined }))
    expect(await screen.findByRole('heading', { name: 'older.csv' })).toBeInTheDocument()
  })
})
