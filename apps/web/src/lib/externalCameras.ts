import type { ExternalCamera, ExternalCameraPayload } from '../types'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:9301/api'

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const fallback = await response.text()
    throw new Error(fallback || response.statusText)
  }
  return response.json() as Promise<T>
}

export async function fetchExternalCameras(): Promise<ExternalCamera[]> {
  const response = await fetch(`${API_BASE_URL}/external-cameras`)
  return handleResponse<ExternalCamera[]>(response)
}

export async function createExternalCamera(payload: ExternalCameraPayload): Promise<ExternalCamera> {
  const response = await fetch(`${API_BASE_URL}/external-cameras`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      name: payload.name,
      source_url: payload.sourceUrl,
      username: payload.username || null,
      password: payload.password || null,
    }),
  })
  return handleResponse<ExternalCamera>(response)
}

export async function startExternalCamera(cameraId: string): Promise<ExternalCamera> {
  const response = await fetch(`${API_BASE_URL}/external-cameras/${cameraId}/start`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
  })
  return handleResponse<ExternalCamera>(response)
}

export async function stopExternalCamera(cameraId: string, deleteStream = false): Promise<ExternalCamera> {
  const response = await fetch(`${API_BASE_URL}/external-cameras/${cameraId}/stop`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ delete_stream: deleteStream }),
  })
  return handleResponse<ExternalCamera>(response)
}

export async function removeExternalCamera(cameraId: string): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/external-cameras/${cameraId}`, {
    method: 'DELETE',
  })
  if (!response.ok) {
    throw new Error(`No se pudo eliminar la cámara externa: ${response.statusText}`)
  }
}

