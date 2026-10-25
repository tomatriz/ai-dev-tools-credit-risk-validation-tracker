import { useRef, useState, type ChangeEvent, type DragEvent } from 'react'

interface UploadPanelProps {
  busy: boolean
  onUpload: (file: File) => Promise<void>
}

export function UploadPanel({ busy, onUpload }: UploadPanelProps) {
  const [file, setFile] = useState<File | null>(null)
  const [dragging, setDragging] = useState(false)
  const inputRef = useRef<HTMLInputElement>(null)

  const choose = (candidate?: File) => {
    if (candidate) setFile(candidate)
  }

  const onChange = (event: ChangeEvent<HTMLInputElement>) => choose(event.target.files?.[0])
  const onDrop = (event: DragEvent<HTMLDivElement>) => {
    event.preventDefault()
    setDragging(false)
    choose(event.dataTransfer.files?.[0])
  }

  return (
    <section className="upload-card" aria-labelledby="upload-title">
      <div className="eyebrow">New validation</div>
      <h2 id="upload-title">Assess a PD dataset</h2>
      <p>
        Upload a synthetic CSV with <code>observation_id</code>, <code>predicted_pd</code>, and{' '}
        <code>default_flag</code>.
      </p>

      <div
        className={`dropzone ${dragging ? 'dropzone--active' : ''}`}
        onDragEnter={(event) => {
          event.preventDefault()
          setDragging(true)
        }}
        onDragOver={(event) => event.preventDefault()}
        onDragLeave={() => setDragging(false)}
        onDrop={onDrop}
      >
        <input
          ref={inputRef}
          className="visually-hidden"
          id="csv-file"
          aria-label="Choose CSV file"
          type="file"
          accept=".csv,text/csv"
          onChange={onChange}
          disabled={busy}
        />
        <button type="button" className="dropzone__icon" onClick={() => inputRef.current?.click()} disabled={busy}>
          <svg viewBox="0 0 24 24" aria-hidden="true">
            <path d="M12 16V4m0 0L7.5 8.5M12 4l4.5 4.5M5 14v4a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-4" />
          </svg>
          <span className="visually-hidden">Choose CSV file</span>
        </button>
        <div>
          <strong>{file ? file.name : 'Drop a CSV here'}</strong>
          <span>{file ? `${(file.size / 1024).toFixed(1)} KB selected` : 'or choose a file from your computer'}</span>
        </div>
      </div>

      <button
        className="button button--primary"
        type="button"
        disabled={!file || busy}
        onClick={() => file && onUpload(file)}
      >
        {busy ? <span className="spinner" aria-hidden="true" /> : null}
        {busy ? 'Running validation…' : 'Run validation'}
      </button>
      <p className="policy-note">
        <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 8v4m0 4h.01M10.3 3.8 2.2 18a2 2 0 0 0 1.7 3h16.2a2 2 0 0 0 1.7-3L13.7 3.8a2 2 0 0 0-3.4 0Z" /></svg>
        Results use configurable demonstration policy, not regulatory thresholds.
      </p>
    </section>
  )
}
