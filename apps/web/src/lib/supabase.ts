import type { Event } from '../types'
import { logWarn, logError } from '../utils/logger'
import { resilientFetch, withRetry } from './resilience'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:9301/api'
const DEFAULT_USER_ID = 'anonymous'

interface BackendEventStats {
  total: number
  by_type: Record<string, number>
  by_camera?: Record<string, number>
  period_hours?: number
  start_date?: string
  end_date?: string
  hourly?: Array<{ bucket: string; count: number }>
}

async function apiRequest<T>(path: string, options: RequestInit = {}): Promise<T> {
  const response = await withRetry(
    () => resilientFetch(`${API_BASE_URL}${path}`, {
      headers: {
        'Content-Type': 'application/json',
        ...(options.headers ?? {}),
      },
      ...options,
    }, { timeout: 10000, retries: 2, breaker: 'supabase' }),
    { maxRetries: 2 }
  )

  if (!response.ok) {
    const text = await response.text()
    throw new Error(text || response.statusText)
  }

  if (response.status === 204) {
    return undefined as unknown as T
  }

  const contentType = response.headers.get('content-type') ?? ''
  if (!contentType.includes('application/json')) {
    return undefined as unknown as T
  }

  return (await response.json()) as T
}

/**
 * Insertar un evento en Supabase
 * @param eventType - Tipo de evento
 * @param payload - Payload del evento
 * @returns El evento insertado o null si hay error
 */
// Cache para evitar múltiples inserciones simultáneas
let lastInsertTime = 0
const MIN_INSERT_INTERVAL = 5000 // 5 segundos mínimo entre inserciones

export async function insertEvent(
  eventType: string,
  payload: any,
  cameraId?: string,
  sessionId?: string | null
): Promise<Event | null> {
  try {
    // Throttle: evitar inserciones muy frecuentes
    const now = Date.now()
    if (now - lastInsertTime < MIN_INSERT_INTERVAL) {
      return null // Ignorar si es muy pronto
    }
    lastInsertTime = now

    // Insertar el evento en la tabla vishum_events
    const eventPayload = { ...payload }
    if (sessionId) {
      eventPayload.session_id = sessionId
    }
    const resolvedCameraId = cameraId ?? eventPayload.cameraId ?? 'default_camera'
    delete eventPayload.cameraId

    const body = {
      event_type: eventType,
      payload: eventPayload,
      camera_id: resolvedCameraId,
      user_id: DEFAULT_USER_ID,
    }

    const data = await apiRequest<Event>('/events', {
      method: 'POST',
      body: JSON.stringify(body),
    })

    return data
  } catch (error: any) {
    logWarn('No se pudo insertar el evento', error)
    return null
  }
}

/**
 * Obtener eventos desde Supabase
 * @param limit - Límite de eventos a obtener
 * @param eventType - Filtrar por tipo de evento (opcional)
 * @returns Array de eventos
 */
export async function getEvents(
  limit: number = 100,
  eventType?: string,
  sessionId?: string | null
): Promise<Event[]> {
  if (!sessionId) {
    return []
  }
  try {
    const params = new URLSearchParams({
      limit: String(limit),
      user_id: DEFAULT_USER_ID,
      session_id: sessionId,
    })

    if (eventType) {
      params.set('event_type', eventType)
    }

    const data = await apiRequest<Event[]>(`/events?${params.toString()}`)
    return data ?? []
  } catch (error) {
    logError('Error obteniendo eventos desde la API', error)
    return []
  }
}

/**
 * Obtener estadísticas de eventos
 * @param hours - Horas hacia atrás para calcular estadísticas
 * @returns Objeto con estadísticas
 */
export interface EventStats {
  total: number
  byType: Record<string, number>
  hourly: Array<{ bucket: string; count: number }>
}

export async function getEventStats(hours: number = 24, sessionId?: string | null): Promise<EventStats> {
  if (!sessionId) {
    return { total: 0, byType: {}, hourly: [] }
  }
  try {
    const params = new URLSearchParams({
      hours: String(hours),
      user_id: DEFAULT_USER_ID,
      session_id: sessionId,
    })

    const data = await apiRequest<BackendEventStats>(`/events/stats/summary?${params.toString()}`)

    const hourlyData =
      data?.hourly?.map((entry) => ({
        bucket: entry.bucket,
        count: entry.count,
      })) ?? []

    return {
      total: data?.total ?? 0,
      byType: data?.by_type ?? {},
      hourly: hourlyData.sort(
        (a, b) => new Date(a.bucket).getTime() - new Date(b.bucket).getTime()
      ),
    }
  } catch (error) {
    logError('Error obteniendo estadísticas de eventos', error)
    return { total: 0, byType: {}, hourly: [] }
  }
}

