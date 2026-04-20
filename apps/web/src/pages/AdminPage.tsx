import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { motion } from 'framer-motion'
import {
  ShieldCheck,
  Cpu,
  AlertTriangle,
  Power,
  Ban,
  Activity,
  Camera,
  EyeOff,
  Eye,
  RefreshCw,
} from 'lucide-react'
import { useAppStore } from '../store/appStore'
import {
  fetchAdminSessions,
  adminSessionAction,
  fetchAdminAlerts,
  fetchBannedSessions,
  type AdminAlert,
} from '../lib/sessions'
import type { DemoSessionRecord } from '../types'
import { logWarn } from '../utils/logger'

type SessionStatus = 'active' | 'limit' | 'banned' | 'idle'

interface AdminSession {
  id: string
  user: string
  email: string
  organization?: string
  plan?: string
  cameras: number
  startedAt: string
  lastSeen: string
  durationMinutes: number
  status: SessionStatus
  tokensUsed: number
  fpsAverage: number
  notes?: string
}

const statusLabels: Record<SessionStatus, { label: string; badge: string }> = {
  active: { label: 'Activo', badge: 'badge-active' },
  limit: { label: 'Límite cercano', badge: 'badge-warning' },
  banned: { label: 'Baneado', badge: 'badge-error' },
  idle: { label: 'Inactivo', badge: 'badge-info' },
}

const ADMIN_ACTION_REASONS: Record<'disconnect' | 'ban' | 'limit', string> = {
  disconnect: 'Acción manual desde panel administrativo',
  ban: 'Bloqueo manual aplicado desde panel',
  limit: 'Se aplicó límite de recursos desde panel',
}

export function AdminPage() {
  const { adminAuth, adminLogin, adminLogout } = useAppStore((state) => ({
    adminAuth: state.adminAuth,
    adminLogin: state.adminLogin,
    adminLogout: state.adminLogout,
  }))
  const isAuthenticated = adminAuth.isAuthenticated
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [showPassword, setShowPassword] = useState(false)
  const [loginLoading, setLoginLoading] = useState(false)

  const [sessions, setSessions] = useState<AdminSession[]>([])
  const [sessionsLoading, setSessionsLoading] = useState(false)
  const [sessionsError, setSessionsError] = useState<string | null>(null)
  const [lastRefresh, setLastRefresh] = useState<string | null>(null)
  const [actionLoading, setActionLoading] = useState<string | null>(null)
  const [alerts, setAlerts] = useState<AdminAlert[]>([])
  const [alertsError, setAlertsError] = useState<string | null>(null)
  const [bannedSessions, setBannedSessions] = useState<DemoSessionRecord[]>([])
  const [bannedTotal, setBannedTotal] = useState(0)
  const [bannedLimit, setBannedLimit] = useState(5)
  const [bannedOffset, setBannedOffset] = useState(0)
  const [bannedStartDate, setBannedStartDate] = useState('')
  const [bannedEndDate, setBannedEndDate] = useState('')
  const [bannedLoading, setBannedLoading] = useState(false)
  const [bannedError, setBannedError] = useState<string | null>(null)
  const [sessionsRefreshing, setSessionsRefreshing] = useState(false)
  const [alertsRefreshing, setAlertsRefreshing] = useState(false)
  const [bannedRefreshing, setBannedRefreshing] = useState(false)
  const hasFetchedSessionsRef = useRef(false)
  const bannedInitialFetchRef = useRef(false)

  const mapSessionRecord = useCallback((record: DemoSessionRecord): AdminSession => {
    const rawStatus = (record.status || '').toLowerCase()
    const validStatuses: SessionStatus[] = ['active', 'limit', 'banned', 'idle']
    const status: SessionStatus = validStatuses.includes(rawStatus as SessionStatus)
      ? (rawStatus as SessionStatus)
      : 'idle'
    const startedAt = record.started_at ? new Date(record.started_at) : null
    const lastPing = record.last_ping_at ? new Date(record.last_ping_at) : null
    const endDate = lastPing ?? new Date()
    const durationMinutes =
      startedAt && endDate
        ? Math.max(0, Math.round((endDate.getTime() - startedAt.getTime()) / 60000))
        : 0

    const metadata = (record.metadata ?? {}) as Record<string, unknown>
    const organization =
      typeof metadata.organization === 'string' && metadata.organization.length > 0
        ? metadata.organization
        : record.plan ?? 'Visitante'

    return {
      id: record.session_id,
      user: record.name || (record.email ? record.email.split('@')[0] : 'Visitante'),
      email: record.email || '—',
      organization,
      plan: record.plan ?? undefined,
      cameras: record.cameras_active ?? 0,
      startedAt: record.started_at ?? '',
      lastSeen: record.last_ping_at ?? '',
      durationMinutes,
      status,
      tokensUsed: record.tokens_used ?? 0,
      fpsAverage: record.fps_average ?? 0,
      notes: record.admin_note ?? undefined,
    }
  }, [])

  const formatDateTime = useCallback((iso: string) => {
    if (!iso) return '—'
    const date = new Date(iso)
    if (Number.isNaN(date.getTime())) return '—'
    return `${date.toLocaleDateString()} ${date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`
  }, [])

  const handleFetchSessions = useCallback(
    async (options?: { showSpinner?: boolean }) => {
      const showSpinner = options?.showSpinner ?? false
      const useSpinner = showSpinner || !hasFetchedSessionsRef.current

      if (!adminAuth.token) {
        setSessionsError('Configura la variable VITE_ADMIN_API_TOKEN para consultar sesiones en vivo.')
        setAlerts([])
        setAlertsError('Token administrativo no disponible.')
        if (useSpinner) {
          setSessionsLoading(false)
          setAlertsRefreshing(false)
        } else {
          setSessionsRefreshing(false)
          setAlertsRefreshing(false)
        }
        return
      }

      if (useSpinner) {
        setSessionsLoading(true)
      } else {
        setSessionsRefreshing(true)
      }

      try {
        const data = await fetchAdminSessions(adminAuth.token)
        const visibleSessions = data.sessions.filter((record) => {
          const status = (record.status || '').toLowerCase()
          return status === 'active' || status === 'limit' || status === 'banned'
        })
        const mapped = visibleSessions.map(mapSessionRecord)
        setSessions(mapped)
        setLastRefresh(data.generated_at)
        setSessionsError(null)

        setAlertsRefreshing(!useSpinner)

        try {
          const fetchedAlerts = await fetchAdminAlerts(adminAuth.token)
          const deduped = fetchedAlerts.reduce<AdminAlert[]>((acc, alert) => {
            if (!acc.find((item) => item.id === alert.id)) {
              acc.push(alert)
            }
            return acc
          }, [])
          const limited = deduped.slice(0, 5)
          setAlerts(limited)
          setAlertsError(null)
        } catch (alertsFetchError) {
          logWarn('No se pudieron obtener las alertas administrativas', alertsFetchError)
          const message =
            alertsFetchError instanceof Error
              ? alertsFetchError.message
              : 'No se pudieron cargar las alertas administrativas.'
          setAlertsError(message)
        } finally {
          setAlertsRefreshing(false)
        }
      } catch (error) {
        const message =
          error instanceof Error ? error.message : 'No se pudieron cargar las sesiones activas.'
        setSessionsError(message)
        setAlerts([])
      } finally {
        if (useSpinner) {
          setSessionsLoading(false)
        } else {
          setSessionsRefreshing(false)
        }
        hasFetchedSessionsRef.current = true
      }
    },
    [adminAuth.token, mapSessionRecord]
  )

  const fetchBannedList = useCallback(
    async (options?: { showSpinner?: boolean }) => {
      const showSpinner = options?.showSpinner ?? false
      const useSpinner = showSpinner || !bannedInitialFetchRef.current

      if (!adminAuth.token) {
        setBannedSessions([])
        setBannedTotal(0)
        setBannedError('Token administrativo no configurado.')
        if (useSpinner) {
          setBannedLoading(false)
        } else {
          setBannedRefreshing(false)
        }
        return
      }

      if (useSpinner) {
        setBannedLoading(true)
      } else {
        setBannedRefreshing(true)
      }

      try {
        const response = await fetchBannedSessions(adminAuth.token, {
          limit: bannedLimit,
          offset: bannedOffset,
          startDate: bannedStartDate ? new Date(`${bannedStartDate}T00:00:00Z`).toISOString() : undefined,
          endDate: bannedEndDate ? new Date(`${bannedEndDate}T23:59:59.999Z`).toISOString() : undefined,
        })
        setBannedSessions(response.sessions)
        setBannedTotal(response.total)
        setBannedError(null)
      } catch (error) {
        const message =
          error instanceof Error ? error.message : 'No se pudieron obtener los usuarios bloqueados.'
        setBannedError(message)
        setBannedSessions([])
        setBannedTotal(0)
      } finally {
        if (useSpinner) {
          setBannedLoading(false)
        } else {
          setBannedRefreshing(false)
        }
        bannedInitialFetchRef.current = true
      }
    },
    [adminAuth.token, bannedLimit, bannedOffset, bannedStartDate, bannedEndDate]
  )

  const handleAdminAction = useCallback(
    async (sessionId: string, action: 'disconnect' | 'ban' | 'limit') => {
      if (!adminAuth.token) {
        setSessionsError('Token administrativo no configurado.')
        return
      }

      setActionLoading(`${sessionId}-${action}`)
      setSessionsError(null)
      try {
        await adminSessionAction(adminAuth.token, sessionId, action, ADMIN_ACTION_REASONS[action])
        await handleFetchSessions()
        await fetchBannedList()
      } catch (error) {
        const message =
          error instanceof Error ? error.message : 'No se pudo aplicar la acción seleccionada.'
        setSessionsError(message)
      } finally {
        setActionLoading(null)
      }
    },
    [adminAuth.token, handleFetchSessions, fetchBannedList]
  )

  useEffect(() => {
    if (!isAuthenticated) {
      setSessions([])
      setSessionsError(null)
      setLastRefresh(null)
       setAlerts([])
       setAlertsError(null)
      setBannedSessions([])
      setBannedTotal(0)
      setBannedOffset(0)
      setBannedError(null)
      hasFetchedSessionsRef.current = false
      bannedInitialFetchRef.current = false
      return
    }

    handleFetchSessions({ showSpinner: true })
    const interval = window.setInterval(() => handleFetchSessions({ showSpinner: false }), 20000)
    return () => window.clearInterval(interval)
  }, [isAuthenticated, handleFetchSessions])

  useEffect(() => {
    if (!isAuthenticated) {
      return
    }
    fetchBannedList({ showSpinner: !bannedInitialFetchRef.current })
  }, [
    isAuthenticated,
    bannedLimit,
    bannedOffset,
    bannedStartDate,
    bannedEndDate,
    fetchBannedList,
  ])

  const summary = useMemo(() => {
    const activeSessions = sessions.filter((s) => s.status === 'active').length
    const totalCameras = sessions.reduce((acc, session) => acc + session.cameras, 0)
    const limitSessions = sessions.filter((s) => s.status === 'limit').length
    const bannedSessions = sessions.filter((s) => s.status === 'banned').length

    const totalTokens = sessions.reduce((acc, session) => acc + session.tokensUsed, 0)

    return {
      activeSessions,
      totalCameras,
      limitSessions,
      bannedSessions,
      totalTokens,
    }
  }, [sessions])

  const handleLogin = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setLoginLoading(true)
    const success = await adminLogin(username.trim(), password)
    setLoginLoading(false)
    if (!success) {
      setError('Credenciales inválidas. Verifica usuario y contraseña.')
      return
    }
    setError(null)
    setUsername('')
    setPassword('')
  }

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen flex items-center justify-center page-shell page-shell--fluid">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="card admin-login-card"
        >
          <div className="text-center mb-4">
            <ShieldCheck size={36} className="text-primary mb-3" />
            <h2 className="text-forest font-semibold mb-2">Acceso administrativo</h2>
            <p className="text-moss text-sm mb-0">
              Este panel es exclusivo para el equipo de IAGENTEK. Ingresa las credenciales provistas.
            </p>
          </div>
          <form className="flex flex-col gap-3" onSubmit={handleLogin}>
            <div>
              <label className="label">Usuario</label>
              <input
                type="text"
                className="input"
                value={username}
                onChange={(event) => setUsername(event.target.value)}
                placeholder="Usuario administrativo"
                autoComplete="username"
                required
              />
            </div>
            <div>
              <label className="label">Contraseña</label>
              <div className="relative">
                <input
                  type={showPassword ? 'text' : 'password'}
                  className="input pr-5"
                  value={password}
                  onChange={(event) => setPassword(event.target.value)}
                  placeholder="Contraseña"
                  autoComplete="current-password"
                  required
                />
                <button
                  type="button"
                  className="absolute top-1/2 right-0 -translate-y-1/2 pr-3 text-moss hover:text-forest bg-transparent border-0 cursor-pointer"
                  onClick={() => setShowPassword((prev) => !prev)}
                  aria-label={showPassword ? 'Ocultar contraseña' : 'Mostrar contraseña'}
                >
                  {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                </button>
              </div>
            </div>
            {error && <div className="alert alert-error">{error}</div>}
            <button type="submit" className="btn btn-primary w-full text-lg" disabled={loginLoading}>
              {loginLoading ? 'Validando…' : 'Ingresar'}
            </button>
          </form>
        </motion.div>
      </div>
    )
  }

  return (
    <div className="page-shell page-shell--fluid py-4 admin-container">
      <motion.header
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.45 }}
        className="admin-header bg-gray-50 border border-gray-100 rounded-lg"
      >
        <div className="admin-header-info">
          <h1 className="text-xl text-forest font-semibold mb-1 flex items-center gap-2">
            <ShieldCheck size={24} /> Administrator Console
          </h1>
          <p className="text-moss mb-0 text-sm">
            Visualiza uso en tiempo real, controla límites de la demo y protege tus recursos del VPS.
          </p>
        </div>
        <div className="admin-header-actions">
          <button type="button" className="btn btn-secondary">
            Exportar reporte
          </button>
          <button type="button" className="btn btn-ghost text-amber-600">
            Modo demo público
          </button>
          <button type="button" className="btn btn-danger" onClick={adminLogout}>
            Cerrar sesión
          </button>
        </div>
      </motion.header>
      <div className="admin-divider"></div>

      <motion.section
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.45, delay: 0.05 }}
        className="admin-kpi-grid"
      >
        <div className="admin-kpi-card">
          <div className="admin-kpi-icon gradient-blue">
            <Activity size={20} />
          </div>
          <div>
            <span className="admin-kpi-label">Sesiones activas</span>
            <strong className="admin-kpi-value">{summary.activeSessions}</strong>
          </div>
        </div>
        <div className="admin-kpi-card">
          <div className="admin-kpi-icon gradient-cyan">
            <Camera size={20} />
          </div>
          <div>
            <span className="admin-kpi-label">Cámaras conectadas</span>
            <strong className="admin-kpi-value">{summary.totalCameras}</strong>
          </div>
        </div>
        <div className="admin-kpi-card">
          <div className="admin-kpi-icon gradient-red">
            <AlertTriangle size={20} />
          </div>
          <div>
            <span className="admin-kpi-label">Sesiones al límite</span>
            <strong className="admin-kpi-value">{summary.limitSessions}</strong>
          </div>
        </div>
        <div className="admin-kpi-card">
          <div className="admin-kpi-icon gradient-purple">
            <Ban size={20} />
          </div>
          <div>
            <span className="admin-kpi-label">Bloqueadas</span>
            <strong className="admin-kpi-value">{summary.bannedSessions}</strong>
          </div>
        </div>
        <div className="admin-kpi-card">
          <div className="admin-kpi-icon gradient-green">
            <Cpu size={20} />
          </div>
          <div>
            <span className="admin-kpi-label">Tokens usados</span>
            <strong className="admin-kpi-value">{summary.totalTokens.toLocaleString()}</strong>
          </div>
        </div>
      </motion.section>

      <div className="admin-content-grid">
        <motion.section
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.45, delay: 0.1 }}
          className="card admin-section"
        >
          <div className="admin-section-header">
            <div>
              <h4 className="text-forest font-semibold mb-1">Sesiones en tiempo real</h4>
              <p className="text-moss text-sm mb-0">
                Monitorea quién está usando la demo, su consumo y las cámaras activas.
              </p>
            </div>
            <div className="flex items-center gap-3">
              {lastRefresh && (
                <span className="text-moss text-sm">
                  Actualizado: {formatDateTime(lastRefresh)}
                </span>
              )}
              {sessionsRefreshing && (
                <span className="text-moss text-sm flex items-center gap-1">
                  <span className="h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" role="status" />
                  Actualizando…
                </span>
              )}
              <button
                type="button"
                className="btn btn-secondary inline-flex items-center gap-2"
                onClick={() => handleFetchSessions({ showSpinner: true })}
                disabled={sessionsLoading || sessionsRefreshing}
              >
                <RefreshCw size={14} />
                {sessionsLoading ? 'Actualizando…' : 'Actualizar'}
              </button>
            </div>
          </div>

          <div className="table-responsive admin-table-wrapper">
            <table className="admin-table">
              <thead>
                <tr>
                  <th>Usuario</th>
                  <th>Organización</th>
                  <th>Cámaras</th>
                  <th>Duración</th>
                  <th>FPS prom.</th>
                  <th>Tokens</th>
                  <th>Estado</th>
                  <th className="text-right">Acciones</th>
                </tr>
              </thead>
              <tbody>
                {sessionsError && (
                  <tr>
                    <td colSpan={8}>
                      <div className="alert alert-error">{sessionsError}</div>
                    </td>
                  </tr>
                )}
                {sessions.length === 0 && !sessionsLoading && !sessionsError && (
                  <tr>
                    <td colSpan={8} className="text-center text-moss py-4">
                      No hay sesiones activas registradas.
                    </td>
                  </tr>
                )}
                {sessions.map((session) => (
                  <tr key={session.id}>
                    <td>
                      <div className="flex flex-col">
                        <span className="font-semibold text-forest truncate">{session.user}</span>
                        <span className="text-sm text-moss truncate">{session.email}</span>
                      </div>
                    </td>
                    <td>
                      <span className="badge badge-info">
                        {session.organization ?? 'Visitante'}
                      </span>
                    </td>
                    <td>
                      <span className="font-semibold text-forest">{session.cameras}</span>
                    </td>
                    <td>
                      <div className="flex flex-col">
                        <span className="text-forest">{session.durationMinutes} min</span>
                        <span className="text-sm text-moss">
                          Último ping: {formatDateTime(session.lastSeen)}
                        </span>
                      </div>
                    </td>
                    <td>{session.fpsAverage.toFixed(1)}</td>
                    <td>{session.tokensUsed.toLocaleString()}</td>
                    <td>
                      <span
                        className={`badge ${
                          (statusLabels[session.status] ?? statusLabels.idle).badge
                        }`}
                      >
                        {(statusLabels[session.status] ?? statusLabels.idle).label}
                      </span>
                    </td>
                    <td>
                      <div className="flex justify-end gap-2">
                        <button
                          type="button"
                          className="btn btn-danger flex items-center gap-1"
                          onClick={() => handleAdminAction(session.id, 'disconnect')}
                          disabled={actionLoading === `${session.id}-disconnect`}
                        >
                          <Power size={14} /> Desconectar
                        </button>
                        <button
                          type="button"
                          className="btn btn-secondary flex items-center gap-1"
                          onClick={() => handleAdminAction(session.id, 'limit')}
                          disabled={actionLoading === `${session.id}-limit`}
                        >
                          <EyeOff size={14} /> Limitar
                        </button>
                        <button
                          type="button"
                          className="btn btn-ghost text-amber-600 flex items-center gap-1"
                          onClick={() => handleAdminAction(session.id, 'ban')}
                          disabled={actionLoading === `${session.id}-ban`}
                        >
                          <Ban size={14} /> Banear
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
                {sessionsLoading && (
                  <tr>
                    <td colSpan={8} className="text-center text-moss py-4">
                      Cargando sesiones…
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </motion.section>

        <motion.section
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.45, delay: 0.2 }}
          className="card admin-sidebar-section"
        >
          <div className="admin-section-header">
            <h5 className="text-forest mb-0 flex items-center gap-2">
              <AlertTriangle size={18} className="text-warning" />
              Alertas recientes
            </h5>
            <button type="button" className="btn btn-secondary">
              Registrar acción
            </button>
          </div>
          {alertsRefreshing && (
            <div className="text-moss text-sm mb-2 flex items-center gap-2">
              <span className="h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" role="status" />
              Actualizando alertas…
            </div>
          )}
          <div className="admin-alert-list">
            {alertsError && (
              <div className="alert alert-warning">{alertsError}</div>
            )}
            {!alertsError && alerts.length === 0 && (
              <div className="text-moss text-sm text-center py-3">
                No hay alertas recientes. Mantén la supervisión periódica.
              </div>
            )}
            {alerts.map((alert) => {
              const badgeClass =
                alert.type === 'limit'
                  ? 'badge-warning'
                  : alert.type === 'warning'
                  ? 'badge-error'
                  : alert.type === 'error'
                  ? 'badge-error'
                  : 'badge-info'
              const badgeLabel =
                alert.type === 'limit'
                  ? 'Límite'
                  : alert.type === 'warning'
                  ? 'Atención'
                  : alert.type === 'error'
                  ? 'Error'
                  : 'Info'

              return (
                <div key={alert.id} className="admin-alert-item bg-gray-50 border border-gray-100 rounded-lg p-3">
                  <div className="flex justify-between items-start gap-3">
                    <div>
                      <span className={`badge ${badgeClass} uppercase text-sm mb-2 inline-block`}>{badgeLabel}</span>
                      <p className="text-forest mb-1">{alert.message}</p>
                      <span className="text-sm text-moss">
                        {formatDateTime(alert.createdAt)}
                      </span>
                    </div>
                    {alert.action && (
                      <button type="button" className="btn btn-secondary">
                        {alert.action}
                      </button>
                    )}
                  </div>
                </div>
              )
            })}
          </div>
        </motion.section>

        <motion.section
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.45, delay: 0.3 }}
          className="card admin-sidebar-section"
        >
          <div className="admin-section-header">
            <h5 className="text-forest mb-0 flex items-center gap-2">
              <ShieldCheck size={18} className="text-success" />
              Usuarios bloqueados
            </h5>
            <div className="flex flex-wrap items-center gap-2">
              <select
                className="select w-auto"
                value={bannedLimit}
                onChange={(event) => {
                  bannedInitialFetchRef.current = false
                  setBannedLimit(Number(event.target.value))
                  setBannedOffset(0)
                }}
              >
                {[5, 10, 20, 50].map((option) => (
                  <option key={option} value={option}>
                    Mostrar {option}
                  </option>
                ))}
              </select>
              <button
                type="button"
                className="btn btn-secondary"
                onClick={() => {
                  fetchBannedList({ showSpinner: true })
                }}
                disabled={bannedLoading || bannedRefreshing}
              >
                Refrescar
              </button>
            </div>
          </div>
          <div className="flex flex-wrap gap-2 mb-3">
            <div className="flex flex-col">
              <label className="text-moss text-sm">Desde</label>
              <input
                type="date"
                className="input input-compact"
                value={bannedStartDate}
                onChange={(event) => {
                  bannedInitialFetchRef.current = false
                  setBannedStartDate(event.target.value)
                  setBannedOffset(0)
                }}
              />
            </div>
            <div className="flex flex-col">
              <label className="text-moss text-sm">Hasta</label>
              <input
                type="date"
                className="input input-compact"
                value={bannedEndDate}
                onChange={(event) => {
                  bannedInitialFetchRef.current = false
                  setBannedEndDate(event.target.value)
                  setBannedOffset(0)
                }}
              />
            </div>
            <div className="flex items-end">
              <button
                type="button"
                className="btn btn-secondary"
                onClick={() => {
                  fetchBannedList({ showSpinner: true })
                }}
                disabled={bannedLoading || bannedRefreshing}
              >
                Aplicar filtros
              </button>
            </div>
          </div>
          {bannedRefreshing && !bannedLoading && (
            <div className="text-moss text-sm mb-2 flex items-center gap-2">
              <span className="h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" role="status" />
              Actualizando usuarios bloqueados…
            </div>
          )}
          {bannedError && <div className="alert alert-warning">{bannedError}</div>}
          {bannedLoading && (
            <div className="text-moss text-sm text-center py-3">Cargando usuarios bloqueados…</div>
          )}
          {!bannedLoading && !bannedError && bannedSessions.length === 0 && (
            <div className="text-moss text-sm text-center py-3">
              No se encontraron usuarios bloqueados con los filtros actuales.
            </div>
          )}
          <div className="flex flex-col gap-3">
            {bannedSessions.map((session) => (
              <div
                key={session.session_id}
                className="admin-ban-card bg-gray-50 border border-gray-100 rounded-lg p-3"
              >
                <div className="flex justify-between items-start gap-3">
                  <div>
                    <span className="text-forest font-semibold block">
                      {session.name || session.email || session.session_id}
                    </span>
                    <span className="text-moss text-sm block">Correo: {session.email ?? '—'}</span>
                    <span className="text-moss text-sm block">
                      Motivo: {session.admin_note ?? 'No especificado'}
                    </span>
                    <span className="text-moss text-sm block">
                      Último registro: {formatDateTime(session.last_ping_at ?? '')}
                    </span>
                  </div>
                  <button type="button" className="btn btn-secondary">
                    Rehabilitar
                  </button>
                </div>
              </div>
            ))}
          </div>
          {!bannedLoading && bannedSessions.length > 0 && (
            <div className="flex justify-between items-center mt-3 text-moss text-sm">
              <span>
                Mostrando {Math.min(bannedLimit, bannedSessions.length)} de {bannedTotal} usuario(s) bloqueado(s)
              </span>
              <div className="flex gap-2">
                <button
                  type="button"
                  className="btn btn-secondary"
                  disabled={bannedOffset === 0 || bannedLoading || bannedRefreshing}
                  onClick={() => {
                    bannedInitialFetchRef.current = false
                    setBannedOffset((prev) => Math.max(0, prev - bannedLimit))
                  }}
                >
                  Anteriores
                </button>
                <button
                  type="button"
                  className="btn btn-secondary"
                  disabled={bannedOffset + bannedLimit >= bannedTotal || bannedLoading || bannedRefreshing}
                  onClick={() => {
                    bannedInitialFetchRef.current = false
                    setBannedOffset((prev) => prev + bannedLimit)
                  }}
                >
                  Siguientes
                </button>
              </div>
            </div>
          )}
        </motion.section>
      </div>
    </div>
  )
}
