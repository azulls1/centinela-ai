import type { AdminSessionsResponse, DemoSessionRecord } from '../types'
import { withRetry, withTimeout } from './resilience'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:9301/api'

export type AdminAlertType = 'limit' | 'warning' | 'info' | 'error'

export interface AdminAlert {
  id: string
  type: AdminAlertType
  message: string
  createdAt: string
  action?: string
}

export interface BannedSessionsResponse {
  sessions: DemoSessionRecord[]
  total: number
  limit: number
  offset: number
}

export interface FetchBannedSessionsOptions {
  limit?: number
  offset?: number
  startDate?: string
  endDate?: string
}

export interface SessionInitPayload {
  sessionId: string
  name?: string
  email?: string
  plan?: string
  metadata?: Record<string, unknown>
}

export interface SessionHeartbeatPayload {
  sessionId: string
  camerasActive: number
  fpsAverage?: number | null
  tokensUsed?: number | null
  status?: string | null
}

export interface AdminLoginPayload {
  username: string
  password: string
}

export interface AdminLoginResult {
  token: string
  username: string
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const response = await withRetry(
    () => withTimeout(
      () => fetch(`${API_BASE_URL}${path}`, {
        headers: {
          'Content-Type': 'application/json',
          ...(options.headers ?? {}),
        },
        ...options,
      }),
      10000
    ),
    { maxRetries: 2 }
  )

  if (!response.ok) {
    const text = await response.text()
    throw new Error(text || response.statusText)
  }

  return (await response.json()) as T
}

export async function initDemoSession(payload: SessionInitPayload): Promise<DemoSessionRecord> {
  return withRetry(
    () => withTimeout(
      () => request<DemoSessionRecord>('/sessions/init', {
        method: 'POST',
        body: JSON.stringify({
          session_id: payload.sessionId,
          name: payload.name ?? null,
          email: payload.email ?? null,
          plan: payload.plan ?? null,
          metadata: payload.metadata ?? {},
        }),
      }),
      15000
    ),
    { maxRetries: 2 }
  )
}

export async function heartbeatSession(payload: SessionHeartbeatPayload): Promise<DemoSessionRecord> {
  const body: Record<string, unknown> = {
    session_id: payload.sessionId,
    cameras_active: payload.camerasActive,
    fps_average: payload.fpsAverage ?? null,
    tokens_used: payload.tokensUsed ?? null,
  }

  if (payload.status !== undefined) {
    body.status = payload.status
  }

  return withRetry(
    () => withTimeout(
      () => request<DemoSessionRecord>('/sessions/heartbeat', {
        method: 'POST',
        body: JSON.stringify(body),
      }),
      10000
    ),
    { maxRetries: 2 }
  )
}

export async function fetchAdminSessions(adminToken: string, status?: string): Promise<AdminSessionsResponse> {
  return withRetry(
    () => withTimeout(
      async () => {
        const url = new URL(`${API_BASE_URL}/sessions/admin`)
        if (status) {
          url.searchParams.set('status', status)
        }

        const response = await fetch(url.toString(), {
          headers: {
            'Content-Type': 'application/json',
            'x-admin-token': adminToken,
          },
        })

        if (!response.ok) {
          const text = await response.text()
          throw new Error(text || response.statusText)
        }

        return (await response.json()) as AdminSessionsResponse
      },
      15000
    ),
    { maxRetries: 2 }
  )
}

export async function fetchAdminAlerts(adminToken: string): Promise<AdminAlert[]> {
  const response = await fetch(`${API_BASE_URL}/sessions/admin/alerts`, {
    headers: {
      'Content-Type': 'application/json',
      'x-admin-token': adminToken,
    },
  })

  if (!response.ok) {
    const text = await response.text()
    throw new Error(text || response.statusText)
  }

  const raw = (await response.json()) as Array<{
    id: string
    type: AdminAlertType
    message: string
    created_at: string
    action?: string | null
  }>

  return raw.map((alert) => ({
    id: alert.id,
    type: alert.type,
    message: alert.message,
    createdAt: alert.created_at,
    action: alert.action ?? undefined,
  }))
}

export async function adminSessionAction(
  adminToken: string,
  sessionId: string,
  action: 'disconnect' | 'ban' | 'limit',
  reason?: string
): Promise<DemoSessionRecord> {
  return request<DemoSessionRecord>(`/sessions/admin/${sessionId}/${action}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'x-admin-token': adminToken,
    },
    body: JSON.stringify({ reason: reason ?? null }),
  })
}

export async function fetchBannedSessions(
  adminToken: string,
  options: FetchBannedSessionsOptions = {}
): Promise<BannedSessionsResponse> {
  const url = new URL(`${API_BASE_URL}/sessions/admin/banned`)
  if (typeof options.limit === 'number') {
    url.searchParams.set('limit', String(options.limit))
  }
  if (typeof options.offset === 'number') {
    url.searchParams.set('offset', String(options.offset))
  }
  if (options.startDate) {
    url.searchParams.set('start_date', options.startDate)
  }
  if (options.endDate) {
    url.searchParams.set('end_date', options.endDate)
  }

  const response = await fetch(url.toString(), {
    headers: {
      'Content-Type': 'application/json',
      'x-admin-token': adminToken,
    },
  })

  if (!response.ok) {
    const text = await response.text()
    throw new Error(text || response.statusText)
  }

  return (await response.json()) as BannedSessionsResponse
}

export async function adminLoginRequest(payload: AdminLoginPayload): Promise<AdminLoginResult> {
  return request<AdminLoginResult>('/sessions/admin/auth/login', {
    method: 'POST',
    body: JSON.stringify({
      username: payload.username,
      password: payload.password,
    }),
  })
}
