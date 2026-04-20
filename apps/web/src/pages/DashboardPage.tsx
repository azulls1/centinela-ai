import { useEffect, useState, useMemo, useCallback, useRef } from 'react'
import { Link } from 'react-router-dom'
import { useAppStore } from '../store/appStore'
import { getEvents, getEventStats, type EventStats } from '../lib/supabase'
import { Event } from '../types'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, Area, AreaChart,
} from 'recharts'
import {
  Activity, Users, ShieldAlert, ScanFace, ChevronUp, ChevronDown,
  Filter, Eye,
} from 'lucide-react'
import { motion } from 'framer-motion'

const logError = (message: string, error?: unknown) => {
  console.error(`[Dashboard] ${message}`, error)
}

/* ------------------------------------------------------------------ */
/*  Time-range configuration                                          */
/* ------------------------------------------------------------------ */

type TimeRange = '1h' | '6h' | '24h' | '7d' | '30d'

const TIME_RANGES: { key: TimeRange; label: string; hours: number }[] = [
  { key: '1h', label: '1h', hours: 1 },
  { key: '6h', label: '6h', hours: 6 },
  { key: '24h', label: '24h', hours: 24 },
  { key: '7d', label: '7d', hours: 168 },
  { key: '30d', label: '30d', hours: 720 },
]

/** Number of chart buckets and bucket size in minutes for each range */
function bucketConfigForRange(range: TimeRange): { bucketMinutes: number; bucketCount: number; formatFn: (d: Date) => string } {
  switch (range) {
    case '1h':
      return { bucketMinutes: 5, bucketCount: 12, formatFn: (d) => d.toLocaleTimeString('es', { hour: '2-digit', minute: '2-digit' }) }
    case '6h':
      return { bucketMinutes: 30, bucketCount: 12, formatFn: (d) => d.toLocaleTimeString('es', { hour: '2-digit', minute: '2-digit' }) }
    case '24h':
      return { bucketMinutes: 60, bucketCount: 24, formatFn: (d) => d.toLocaleTimeString('es', { hour: '2-digit' }) }
    case '7d':
      return { bucketMinutes: 240, bucketCount: 42, formatFn: (d) => d.toLocaleDateString('es', { weekday: 'short', hour: '2-digit' }) }
    case '30d':
      return { bucketMinutes: 1440, bucketCount: 30, formatFn: (d) => d.toLocaleDateString('es', { day: '2-digit', month: 'short' }) }
  }
}

/* ------------------------------------------------------------------ */
/*  Skeleton components                                               */
/* ------------------------------------------------------------------ */

function SkeletonCard() {
  return (
    <div className="metric-card animate-pulse">
      <div className="metric-card__icon bg-gray-200 rounded-full" style={{ width: 36, height: 36 }} />
      <div>
        <div className="h-3 w-20 bg-gray-200 rounded mb-2" />
        <div className="h-6 w-12 bg-gray-200 rounded" />
      </div>
    </div>
  )
}

function SkeletonChart() {
  return (
    <div className="card animate-pulse">
      <div className="h-4 w-40 bg-gray-200 rounded mb-4" />
      <div className="bg-gray-100 rounded" style={{ height: 320 }} />
    </div>
  )
}

/* ------------------------------------------------------------------ */
/*  Trend indicator                                                   */
/* ------------------------------------------------------------------ */

function TrendBadge({ current, previous }: { current: number; previous: number }) {
  if (previous === 0 && current === 0) return null
  const isUp = current >= previous
  const pct = previous === 0 ? (current > 0 ? 100 : 0) : Math.round(((current - previous) / previous) * 100)
  return (
    <span className={`inline-flex items-center gap-0.5 text-xs font-medium ${isUp ? 'text-emerald-600' : 'text-red-500'}`}>
      {isUp ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
      {Math.abs(pct)}%
    </span>
  )
}

/* ------------------------------------------------------------------ */
/*  Confidence bar                                                    */
/* ------------------------------------------------------------------ */

function ConfidenceBar({ value }: { value: number }) {
  const pct = Math.round(value * 100)
  const color = value >= 0.8 ? '#22c55e' : value >= 0.6 ? '#f59e0b' : '#ef4444'
  return (
    <div className="flex items-center gap-2">
      <div className="flex-1 h-2 rounded-full overflow-hidden" style={{ maxWidth: 80, backgroundColor: 'var(--color-border)' }}>
        <div className="h-full rounded-full" style={{ width: `${pct}%`, backgroundColor: color }} />
      </div>
      <span className="text-xs text-moss">{pct}%</span>
    </div>
  )
}

/* ------------------------------------------------------------------ */
/*  Event type options for filter                                     */
/* ------------------------------------------------------------------ */

const EVENT_TYPE_OPTIONS = [
  { value: '', label: 'Todos' },
  { value: 'person_detected', label: 'Persona' },
  { value: 'face_detected', label: 'Rostro' },
  { value: 'emotion_detected', label: 'Emocion' },
  { value: 'movement_detected', label: 'Movimiento' },
  { value: 'object_detected', label: 'Objeto' },
  { value: 'health_alert', label: 'Alerta salud' },
  { value: 'pose_detected', label: 'Postura' },
  { value: 'hand_detected', label: 'Mano' },
  { value: 'activity_change', label: 'Actividad' },
]

const TABLE_PAGE_SIZE = 20

/* ------------------------------------------------------------------ */
/*  DashboardPage                                                     */
/* ------------------------------------------------------------------ */

/**
 * Dashboard page with time-range selector, KPI cards, charts, and event table.
 */
export function DashboardPage() {
  const sessionId = useAppStore((state) => state.sessionInfo?.session_id ?? null)
  const theme = useAppStore((state) => state.theme)
  const isDark = theme === 'dark' || (theme === 'system' && typeof window !== 'undefined' && window.matchMedia('(prefers-color-scheme: dark)').matches)

  // Theme-aware chart colors
  const chartAxisColor = isDark ? '#7d8f9a' : '#94a3b8'
  const chartGridColor = isDark ? 'rgba(127, 160, 138, 0.12)' : 'rgba(148, 163, 184, 0.25)'
  const chartStrokeColor = isDark ? '#7fa08a' : '#04202C'
  const tooltipStyle = isDark
    ? { backgroundColor: '#1a2332', border: '1px solid #2d3f54', borderRadius: '12px', color: '#e4e8ec' }
    : { backgroundColor: 'white', border: '1px solid #EFF0EE', borderRadius: '12px' }

  // Data
  const [events, setEvents] = useState<Event[]>([])
  const [stats, setStats] = useState<EventStats>({ total: 0, byType: {}, hourly: [] })
  const [prevStats, setPrevStats] = useState<EventStats>({ total: 0, byType: {}, hourly: [] })

  // UI state
  const [loading, setLoading] = useState(true)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)
  const [refreshing, setRefreshing] = useState(false)
  const [initialLoaded, setInitialLoaded] = useState(false)
  const initialLoadedRef = useRef(false)

  // Time range
  const [timeRange, setTimeRange] = useState<TimeRange>('24h')

  // Table filters
  const [tableFilter, setTableFilter] = useState('')
  const [tableLimit, setTableLimit] = useState(TABLE_PAGE_SIZE)

  const hoursForRange = useMemo(() => TIME_RANGES.find((r) => r.key === timeRange)!.hours, [timeRange])

  /* ---- Data loader ---- */
  const loadData = useCallback(
    async (showSpinner: boolean, hours: number) => {
      if (!sessionId) return

      const shouldShowSpinner = showSpinner || !initialLoadedRef.current
      if (shouldShowSpinner) {
        setLoading(true)
      } else {
        setRefreshing(true)
      }

      try {
        // Fetch current period and previous period for trend comparison
        const [eventsData, statsData, prevStatsData] = await Promise.all([
          getEvents(200, undefined, sessionId),
          getEventStats(hours, sessionId),
          getEventStats(hours * 2, sessionId), // double window to derive previous period
        ])
        setEvents(eventsData)
        setStats(statsData)
        setPrevStats(prevStatsData)
        setErrorMessage(null)
        initialLoadedRef.current = true
        setInitialLoaded(true)
      } catch (error) {
        logError('Error cargando datos del dashboard', error)
        setErrorMessage('No se pudieron cargar los datos del dashboard. Intenta nuevamente mas tarde.')
      } finally {
        if (shouldShowSpinner) setLoading(false)
        else setRefreshing(false)
      }
    },
    [sessionId],
  )

  // Reset table pagination when filter changes
  useEffect(() => { setTableLimit(TABLE_PAGE_SIZE) }, [tableFilter])

  // Load data on mount and when time range or session changes
  useEffect(() => {
    if (!sessionId) {
      setEvents([])
      setStats({ total: 0, byType: {}, hourly: [] })
      setPrevStats({ total: 0, byType: {}, hourly: [] })
      setLoading(false)
      setRefreshing(false)
      setInitialLoaded(false)
      initialLoadedRef.current = false
      return
    }

    initialLoadedRef.current = false
    setInitialLoaded(false)
    loadData(true, hoursForRange)

    const interval = setInterval(() => loadData(false, hoursForRange), 30000)
    return () => clearInterval(interval)
  }, [sessionId, hoursForRange, loadData])

  /* ---- Derived data ---- */

  // Filter events by time range on the client
  const eventsInRange = useMemo(() => {
    const cutoff = Date.now() - hoursForRange * 3600_000
    return events.filter((e) => new Date(e.created_at).getTime() >= cutoff)
  }, [events, hoursForRange])

  // KPI counts
  const personCount = useMemo(() => (stats.byType['person_detected'] ?? 0) as number, [stats])
  const faceCount = useMemo(() => (stats.byType['face_detected'] ?? 0) as number, [stats])
  const alertCount = useMemo(() => (stats.byType['health_alert'] ?? 0) as number, [stats])
  const totalCount = stats.total

  // Previous-period KPI counts (prevStats covers 2x window; subtract current to get previous)
  const prevPersonCount = useMemo(() => Math.max(0, ((prevStats.byType['person_detected'] ?? 0) as number) - personCount), [prevStats, personCount])
  const prevFaceCount = useMemo(() => Math.max(0, ((prevStats.byType['face_detected'] ?? 0) as number) - faceCount), [prevStats, faceCount])
  const prevAlertCount = useMemo(() => Math.max(0, ((prevStats.byType['health_alert'] ?? 0) as number) - alertCount), [prevStats, alertCount])
  const prevTotalCount = useMemo(() => Math.max(0, prevStats.total - totalCount), [prevStats, totalCount])

  const metricCards = [
    { label: 'Personas detectadas', value: personCount, prev: prevPersonCount, icon: <Users size={22} /> },
    { label: 'Rostros detectados', value: faceCount, prev: prevFaceCount, icon: <ScanFace size={22} /> },
    { label: 'Alertas', value: alertCount, prev: prevAlertCount, icon: <ShieldAlert size={22} /> },
    { label: 'Eventos totales', value: totalCount, prev: prevTotalCount, icon: <Activity size={22} /> },
  ]

  // Bar chart: events by type
  const chartData = useMemo(
    () =>
      Object.entries(stats.byType).map(([type, count]) => ({
        type: type.replace(/_/g, ' ').replace(/\b\w/g, (l) => l.toUpperCase()),
        count: count as number,
      })),
    [stats.byType],
  )

  // People-over-time area chart
  const personTimeData = useMemo(() => {
    const { bucketMinutes, bucketCount, formatFn } = bucketConfigForRange(timeRange)
    const personEvents = eventsInRange.filter((e) => e.event_type === 'person_detected')
    const now = new Date()

    const result: { label: string; personas: number }[] = []
    for (let i = bucketCount - 1; i >= 0; i--) {
      const bucketEnd = new Date(now.getTime() - i * bucketMinutes * 60_000)
      const bucketStart = new Date(bucketEnd.getTime() - bucketMinutes * 60_000)
      const count = personEvents.filter((e) => {
        const t = new Date(e.created_at).getTime()
        return t >= bucketStart.getTime() && t < bucketEnd.getTime()
      }).length
      result.push({ label: formatFn(bucketEnd), personas: count })
    }
    return result
  }, [eventsInRange, timeRange])

  // Table data: filtered + paginated
  const filteredEvents = useMemo(() => {
    let list = eventsInRange
    if (tableFilter) list = list.filter((e) => e.event_type === tableFilter)
    return list
  }, [eventsInRange, tableFilter])

  const visibleEvents = useMemo(() => filteredEvents.slice(0, tableLimit), [filteredEvents, tableLimit])
  const hasMoreEvents = filteredEvents.length > tableLimit

  /* ---- Empty / no-session state ---- */

  if (!sessionId) {
    return (
      <div className="page-shell container-xxl py-8">
        <div className="card flex flex-col items-center justify-center gap-4" style={{ minHeight: 280 }}>
          <p className="text-moss text-center mb-0">No hay datos en el rango seleccionado</p>
          <Link
            to="/live"
            className="inline-flex items-center gap-2 px-5 py-2 rounded-full font-semibold text-sm transition"
            style={{ backgroundColor: '#5B7065', color: '#fff' }}
          >
            <Eye size={16} />
            Ir a Monitor en Vivo
          </Link>
        </div>
      </div>
    )
  }

  /* ---- Loading skeleton ---- */

  if (loading) {
    return (
      <div className="page-shell container-xxl py-4">
        {/* Skeleton time-range pills */}
        <div className="flex gap-2 mb-4">
          {TIME_RANGES.map((r) => (
            <div key={r.key} className="h-8 w-12 bg-gray-200 rounded-full animate-pulse" />
          ))}
        </div>
        {/* Skeleton KPI cards */}
        <div className="metric-grid mb-4">
          {[1, 2, 3, 4].map((i) => <SkeletonCard key={i} />)}
        </div>
        {/* Skeleton charts */}
        <div className="neo-grid neo-grid--charts">
          <SkeletonChart />
          <SkeletonChart />
        </div>
      </div>
    )
  }

  /* ---- Main render ---- */

  return (
    <div className="page-shell container-xxl py-4">
      {/* Time-range selector */}
      <motion.div
        initial={{ opacity: 0, y: -8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
        className="flex items-center gap-2 mb-4"
      >
        {TIME_RANGES.map((r) => (
          <button
            key={r.key}
            onClick={() => setTimeRange(r.key)}
            className="px-4 py-1.5 rounded-full text-sm font-semibold transition-colors"
            style={
              timeRange === r.key
                ? { backgroundColor: '#5B7065', color: '#fff' }
                : { backgroundColor: isDark ? '#1e2a3a' : '#EFF0EE', color: isDark ? '#9EADA3' : '#5B7065' }
            }
          >
            {r.label}
          </button>
        ))}

        {initialLoaded && refreshing && (
          <span className="ml-auto flex items-center gap-2 text-moss text-sm">
            <span className="h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" role="status" />
            Actualizando...
          </span>
        )}
      </motion.div>

      {/* Error banner */}
      {errorMessage && (
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
          className="alert alert-warning mb-4"
        >
          {errorMessage}
        </motion.div>
      )}

      {/* KPI metric cards */}
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.1 }}
        className="metric-grid mb-4"
      >
        {metricCards.map(({ label, value, prev, icon }) => (
          <motion.div
            key={label}
            whileHover={{ scale: 1.03 }}
            whileTap={{ scale: 0.98 }}
            className="metric-card"
          >
            <div className="metric-card__icon">{icon}</div>
            <div>
              <div className="metric-card__label">{label}</div>
              <div className="flex items-center gap-2">
                <span className="metric-card__value">{value}</span>
                <TrendBadge current={value} previous={prev} />
              </div>
            </div>
          </motion.div>
        ))}
      </motion.div>

      {/* Charts row */}
      <div className="neo-grid neo-grid--charts">
        {/* People over time chart */}
        <motion.div
          initial={{ opacity: 0, y: 18 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.15 }}
          className="card"
        >
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-forest font-semibold mb-0">Personas detectadas en el tiempo</h3>
            <span className="badge badge-info">{timeRange}</span>
          </div>
          {personTimeData.some((d) => d.personas > 0) ? (
            <ResponsiveContainer width="100%" height={320}>
              <AreaChart data={personTimeData}>
                <defs>
                  <linearGradient id="personGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#5B7065" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#5B7065" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke={chartGridColor} />
                <XAxis dataKey="label" stroke={chartAxisColor} tick={{ fontSize: 11 }} interval="preserveStartEnd" />
                <YAxis stroke={chartAxisColor} allowDecimals={false} />
                <Tooltip
                  contentStyle={tooltipStyle}
                />
                <Area
                  type="monotone"
                  dataKey="personas"
                  stroke={chartStrokeColor}
                  strokeWidth={2.5}
                  fill="url(#personGrad)"
                  dot={{ fill: chartStrokeColor, r: 3 }}
                  activeDot={{ r: 5 }}
                />
              </AreaChart>
            </ResponsiveContainer>
          ) : (
            <div className="flex items-center justify-center text-moss" style={{ height: 320 }}>
              Sin detecciones de personas en este rango
            </div>
          )}
        </motion.div>

        {/* Events by type bar chart */}
        <motion.div
          initial={{ opacity: 0, y: 18 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="card"
        >
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-forest font-semibold mb-0">Eventos por tipo</h3>
            <span className="badge badge-info">{chartData.length} categorias</span>
          </div>
          {chartData.length > 0 ? (
            <ResponsiveContainer width="100%" height={320}>
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke={chartGridColor} />
                <XAxis dataKey="type" stroke={chartAxisColor} tick={{ fontSize: 11 }} />
                <YAxis stroke={chartAxisColor} />
                <Tooltip
                  contentStyle={tooltipStyle}
                />
                <Bar dataKey="count" fill="#5B7065" radius={[12, 12, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="flex items-center justify-center text-moss" style={{ height: 320 }}>
              Sin eventos en este rango
            </div>
          )}
        </motion.div>
      </div>

      {/* Events table */}
      <motion.div
        initial={{ opacity: 0, y: 18 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.25 }}
        className="card mt-4"
      >
        <div className="flex flex-wrap items-center justify-between gap-3 mb-3">
          <h3 className="text-forest font-semibold mb-0">Eventos recientes</h3>
          <div className="flex items-center gap-2">
            <Filter size={14} className="text-moss" />
            <select
              value={tableFilter}
              onChange={(e) => setTableFilter(e.target.value)}
              className="text-sm border rounded-lg px-2 py-1 focus:outline-none focus:ring-1 focus:ring-[#5B7065]"
              style={{
                backgroundColor: isDark ? '#1e2a3a' : '#fff',
                borderColor: isDark ? '#2d3f54' : '#E0E2DE',
                color: isDark ? '#e4e8ec' : '#04202C',
              }}
            >
              {EVENT_TYPE_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value}>{opt.label}</option>
              ))}
            </select>
            <span className="badge badge-info text-xs">{filteredEvents.length} resultados</span>
          </div>
        </div>

        {visibleEvents.length > 0 ? (
          <>
            <div className="overflow-x-auto">
              <table className="table">
                <thead className="uppercase text-sm text-moss border-b border-gray-100">
                  <tr>
                    <th scope="col">Tipo</th>
                    <th scope="col">Camara</th>
                    <th scope="col">Confianza</th>
                    <th scope="col">Fecha</th>
                  </tr>
                </thead>
                <tbody>
                  {visibleEvents.map((event) => (
                    <tr key={event.id} className="border-b border-gray-100">
                      <td className="text-forest capitalize">
                        {event.event_type.replace(/_/g, ' ')}
                      </td>
                      <td className="text-moss text-sm">
                        {event.camera_id ?? '-'}
                      </td>
                      <td>
                        <ConfidenceBar value={event.payload.confidence || 0} />
                      </td>
                      <td className="text-moss text-sm">
                        {new Date(event.created_at).toLocaleString('es', {
                          dateStyle: 'medium',
                          timeStyle: 'short',
                        })}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            {hasMoreEvents && (
              <div className="flex justify-center mt-3">
                <button
                  onClick={() => setTableLimit((l) => l + TABLE_PAGE_SIZE)}
                  className="px-5 py-2 rounded-full text-sm font-semibold transition-colors"
                  style={{ backgroundColor: isDark ? '#1e2a3a' : '#EFF0EE', color: isDark ? '#9EADA3' : '#5B7065' }}
                >
                  Ver mas ({filteredEvents.length - tableLimit} restantes)
                </button>
              </div>
            )}
          </>
        ) : (
          <div className="flex flex-col items-center justify-center gap-4 py-8">
            <p className="text-moss text-center mb-0">No hay datos en el rango seleccionado</p>
            <Link
              to="/live"
              className="inline-flex items-center gap-2 px-5 py-2 rounded-full font-semibold text-sm transition"
              style={{ backgroundColor: '#5B7065', color: '#fff' }}
            >
              <Eye size={16} />
              Ir a Monitor en Vivo
            </Link>
          </div>
        )}
      </motion.div>
    </div>
  )
}
