import { useState } from 'react'
import type { ExternalCameraPayload } from '../types'

interface ExternalCameraFormProps {
  onSubmit: (payload: ExternalCameraPayload) => Promise<void>
  onCancel: () => void
  loading?: boolean
}

export function ExternalCameraForm({ onSubmit, onCancel, loading = false }: ExternalCameraFormProps) {
  const [form, setForm] = useState<ExternalCameraPayload>({
    name: '',
    sourceUrl: '',
    username: '',
    password: '',
  })
  const [error, setError] = useState<string | null>(null)

  const handleChange = (field: keyof ExternalCameraPayload) => (event: React.ChangeEvent<HTMLInputElement>) => {
    setForm((prev) => ({
      ...prev,
      [field]: event.target.value,
    }))
  }

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setError(null)

    if (!form.name.trim()) {
      setError('Ingresa un nombre para identificar la cámara.')
      return
    }

    if (!form.sourceUrl.trim()) {
      setError('Ingresa la URL del stream (RTSP/HTTP).')
      return
    }

    try {
      await onSubmit({
        name: form.name.trim(),
        sourceUrl: form.sourceUrl.trim(),
        username: form.username?.trim() || undefined,
        password: form.password || undefined,
      })
      setForm({
        name: '',
        sourceUrl: '',
        username: '',
        password: '',
      })
    } catch (err: any) {
      const message = err?.message || 'No se pudo registrar la cámara.'
      setError(message)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="card card-compact p-4 mb-3">
      <div className="grid grid-cols-1 md:grid-cols-12 gap-3">
        <div className="md:col-span-4">
          <label className="label">Nombre / alias</label>
          <input
            type="text"
            className="input input-compact"
            placeholder="Ej. Cámara acceso principal"
            value={form.name}
            onChange={handleChange('name')}
            disabled={loading}
            required
          />
        </div>
        <div className="md:col-span-8">
          <label className="label">URL del stream (RTSP/HTTP)</label>
          <input
            type="text"
            className="input input-compact"
            placeholder="rtsp://usuario:password@ip:554/stream"
            value={form.sourceUrl}
            onChange={handleChange('sourceUrl')}
            disabled={loading}
            required
          />
        </div>
        <div className="md:col-span-4">
          <label className="label">Usuario (opcional)</label>
          <input
            type="text"
            className="input input-compact"
            value={form.username}
            onChange={handleChange('username')}
            disabled={loading}
            placeholder="usuario"
          />
        </div>
        <div className="md:col-span-4">
          <label className="label">Contraseña (opcional)</label>
          <input
            type="password"
            className="input input-compact"
            value={form.password}
            onChange={handleChange('password')}
            disabled={loading}
            placeholder="contraseña"
          />
        </div>
      </div>

      {error && (
        <div className="alert alert-warning mt-3" role="alert">
          {error}
        </div>
      )}

      <div className="flex gap-2 mt-3">
        <button type="submit" className="btn btn-primary" disabled={loading}>
          {loading ? 'Guardando...' : 'Registrar cámara'}
        </button>
        <button type="button" className="btn btn-secondary" onClick={onCancel} disabled={loading}>
          Cancelar
        </button>
      </div>
    </form>
  )
}

