import { useCallback, useEffect, useState } from 'react'
import { ApiError, createValidation, getValidation, listValidations } from './api'
import { History } from './components/History'
import { UploadPanel } from './components/UploadPanel'
import { ValidationDetail } from './components/ValidationDetail'
import type { Validation } from './types'

function messageFor(error: unknown): string {
  if (error instanceof ApiError) {
    if (error.status === 503) return 'Validation is temporarily unavailable. The operations team has been notified; please try again shortly.'
    return error.message
  }
  if (error instanceof Error && error.name !== 'AbortError') return error.message
  return 'Could not reach the validation service. Check the connection and try again.'
}

export default function App() {
  const [history, setHistory] = useState<Validation[]>([])
  const [selected, setSelected] = useState<Validation | null>(null)
  const [loadingHistory, setLoadingHistory] = useState(true)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [notice, setNotice] = useState<string | null>(null)

  const refreshHistory = useCallback(async (signal?: AbortSignal) => {
    const items = await listValidations(signal)
    setHistory(items)
    return items
  }, [])

  useEffect(() => {
    const controller = new AbortController()
    refreshHistory(controller.signal)
      .then(async (items) => {
        if (items[0]) setSelected(await getValidation(items[0].id, controller.signal))
      })
      .catch((cause) => {
        if ((cause as Error).name !== 'AbortError') setError(messageFor(cause))
      })
      .finally(() => setLoadingHistory(false))
    return () => controller.abort()
  }, [refreshHistory])

  const upload = async (file: File) => {
    setBusy(true)
    setError(null)
    setNotice(null)
    try {
      const result = await createValidation(file)
      setSelected(result)
      setHistory((items) => [result, ...items.filter((item) => item.id !== result.id)])
      setNotice(`${file.name} was validated and added to history.`)
    } catch (cause) {
      setError(messageFor(cause))
    } finally {
      setBusy(false)
    }
  }

  const selectHistory = async (id: string) => {
    setError(null)
    try {
      setSelected(await getValidation(id))
      document.querySelector('main')?.scrollIntoView({ behavior: 'smooth', block: 'start' })
    } catch (cause) {
      setError(messageFor(cause))
    }
  }

  return (
    <div className="app-shell">
      <header className="topbar">
        <a className="brand" href="#top" aria-label="Credit Risk Validation Tracker home">
          <span className="brand__mark" aria-hidden="true"><i /><i /><i /></span>
          <span><strong>CRVT</strong><small>Credit Risk Validation Tracker</small></span>
        </a>
        <nav aria-label="Primary navigation">
          <a href="#workspace">Workspace</a>
          <a href="#history-title">History</a>
          <a href="/docs" target="_blank" rel="noreferrer">API docs <span aria-hidden="true">↗</span></a>
        </nav>
        <span className="environment"><i /> Demo environment</span>
      </header>

      <main id="top">
        <section className="hero" id="workspace">
          <div className="hero__copy">
            <div className="eyebrow eyebrow--light">Model validation workspace</div>
            <h1>Evidence you can<br /><em>act on.</em></h1>
            <p>Turn synthetic credit-risk data into a transparent, reproducible view of quality, calibration, and model performance.</p>
            <div className="hero__features" aria-label="Product qualities">
              <span><i>01</i> Deterministic</span><span><i>02</i> Auditable</span><span><i>03</i> Observable</span>
            </div>
          </div>
          <UploadPanel busy={busy} onUpload={upload} />
        </section>

        <div className="content-shell">
          {error ? <div className="alert alert--error" role="alert"><strong>Something needs attention</strong><span>{error}</span><button onClick={() => setError(null)} aria-label="Dismiss error">×</button></div> : null}
          {notice ? <div className="alert alert--success" role="status"><strong>Validation complete</strong><span>{notice}</span><button onClick={() => setNotice(null)} aria-label="Dismiss message">×</button></div> : null}

          <div className="workspace-grid">
            <History items={history} activeId={selected?.id} loading={loadingHistory} onSelect={selectHistory} />
            <div className="result-area">
              {selected ? (
                <ValidationDetail validation={selected} />
              ) : (
                <section className="welcome-state">
                  <div className="welcome-state__graphic" aria-hidden="true">
                    <span /><span /><span /><i />
                  </div>
                  <div className="eyebrow">Ready to validate</div>
                  <h2>Your evidence workspace starts here</h2>
                  <p>Upload a well-formed synthetic CSV above. The calculation engine will check its quality and return an auditable assessment.</p>
                  <div className="schema">
                    <code>observation_id</code><code>predicted_pd</code><code>default_flag</code>
                  </div>
                </section>
              )}
            </div>
          </div>
        </div>
      </main>

      <footer><span>Credit Risk Validation Tracker</span><span>Educational demonstration · Synthetic data only</span></footer>
    </div>
  )
}
