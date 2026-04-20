import { useEffect, useMemo, useState } from 'react'
import { MAX_ACTIVE_CAMERAS, useAppStore } from '../store/appStore'
import { Toggle } from './Toggle'
import { ExternalCameraForm } from './ExternalCameraForm'
import {
  createExternalCamera,
  fetchExternalCameras,
  removeExternalCamera as removeExternalCameraApi,
  startExternalCamera,
  stopExternalCamera,
} from '../lib/externalCameras'
import type { CameraConfig, ExternalCamera, ExternalCameraPayload } from '../types'

interface DeviceOption {
  deviceId: string
  label: string
  groupId?: string
}

export function CameraManager() {
  const availableDevices = useAppStore((state) => state.availableDevices)
  const setAvailableDevices = useAppStore((state) => state.setAvailableDevices)
  const cameraConfigs = useAppStore((state) => state.cameraConfigs)
  const activeCameraIds = useAppStore((state) => state.activeCameraIds)
  const activateCamera = useAppStore((state) => state.activateCamera)
  const deactivateCamera = useAppStore((state) => state.deactivateCamera)
  const updateCameraConfig = useAppStore((state) => state.updateCameraConfig)
  const externalCameras = useAppStore((state) => state.externalCameras)
  const setExternalCamerasStore = useAppStore((state) => state.setExternalCameras)
  const upsertExternalCamera = useAppStore((state) => state.upsertExternalCamera)
  const removeExternalCameraStore = useAppStore((state) => state.removeExternalCamera)

  const [loadingDevices, setLoadingDevices] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [limitWarning, setLimitWarning] = useState(false)
  const [loadingExternal, setLoadingExternal] = useState(false)
  const [externalError, setExternalError] = useState<string | null>(null)
  const [showExternalForm, setShowExternalForm] = useState(false)
  const [externalFormLoading, setExternalFormLoading] = useState(false)
  const [externalActionLoading, setExternalActionLoading] = useState<string | null>(null)

  const deviceEntries = useMemo<DeviceOption[]>(() => {
    return availableDevices.map((device) => ({
      deviceId: device.deviceId,
      label: device.label || 'Cámara sin identificar',
      groupId: device.groupId,
    }))
  }, [availableDevices])

  const activeCameraCount = useMemo(() => {
    return activeCameraIds.filter((id) => {
      const cfg = cameraConfigs[id]
      return cfg?.enabled
    }).length
  }, [activeCameraIds, cameraConfigs])

  const isLimitReached = activeCameraCount >= MAX_ACTIVE_CAMERAS

  const refreshDevices = async (requestPermissions = false) => {
    if (!navigator.mediaDevices?.enumerateDevices) {
      setError('El navegador no soporta enumeración de dispositivos multimedia.')
      return
    }

    try {
      setLoadingDevices(true)
      setError(null)

      if (requestPermissions) {
        try {
          const permissionStream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false })
          permissionStream.getTracks().forEach((track) => track.stop())
        } catch (permissionError) {
          setError('Permisos de cámara denegados. Autoriza el acceso para listar cámaras.')
          setLoadingDevices(false)
          return
        }
      }

      const devices = await navigator.mediaDevices.enumerateDevices()
      const videoInputs = devices
        .filter((device) => device.kind === 'videoinput')
        .map((device) => ({
          deviceId: device.deviceId,
          label: device.label,
          groupId: device.groupId,
        }))

      setAvailableDevices(videoInputs)
      if (videoInputs.length === 0) {
        setError('No se detectaron cámaras. Conecta un dispositivo o agrega una cámara externa.')
      }
    } catch (err) {
      setError('Ocurrió un error al listar las cámaras.')
    } finally {
      setLoadingDevices(false)
    }
  }

  useEffect(() => {
    refreshDevices()
    const handleDeviceChange = () => {
      refreshDevices()
    }
    navigator.mediaDevices?.addEventListener('devicechange', handleDeviceChange)
    return () => {
      navigator.mediaDevices?.removeEventListener('devicechange', handleDeviceChange)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  useEffect(() => {
    let mounted = true

    const loadExternalCameras = async () => {
      try {
        setLoadingExternal(true)
        const cameras = await fetchExternalCameras()
        if (mounted) {
          setExternalCamerasStore(cameras)
          setExternalError(null)
        }
      } catch (err: any) {
        if (mounted) {
          const message = err?.message || 'No se pudieron cargar las cámaras externas.'
          setExternalError(message)
        }
      } finally {
        if (mounted) {
          setLoadingExternal(false)
        }
      }
    }

    loadExternalCameras()
    return () => {
      mounted = false
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const findCameraByDeviceId = (deviceId: string): CameraConfig | undefined =>
    Object.values(cameraConfigs).find((camera) => camera.deviceId === deviceId)

  const handleToggle = (deviceId: string, enabled: boolean) => {
    if (enabled) {
      setLimitWarning(false)
      const cameraId = activateCamera(deviceId)
      if (!cameraId) {
        setLimitWarning(true)
      }
    } else {
      const camera = findCameraByDeviceId(deviceId)
      if (camera) {
        deactivateCamera(camera.id)
      }
    }
  }

  const handleLabelChange = (cameraId: string, label: string) => {
    updateCameraConfig(cameraId, { label })
  }

  const handleLocationChange = (cameraId: string, location: string) => {
    updateCameraConfig(cameraId, { location })
  }

  const handleResolutionChange = (cameraId: string, resolution: CameraConfig['resolution']) => {
    updateCameraConfig(cameraId, { resolution })
  }

  const handleFpsChange = (cameraId: string, fps: number) => {
    updateCameraConfig(cameraId, { targetFPS: fps })
  }

  const getExternalConfig = (cameraId: string) => cameraConfigs[`external-${cameraId}`]

  const handleCreateExternal = async (payload: ExternalCameraPayload) => {
    try {
      setExternalFormLoading(true)
      const camera = await createExternalCamera(payload)
      upsertExternalCamera(camera)
      setExternalError(null)
      setShowExternalForm(false)
      setLimitWarning(false)
    } catch (err: any) {
      const message = err?.message || 'No se pudo registrar la cámara externa.'
      setExternalError(message)
      throw err
    } finally {
      setExternalFormLoading(false)
    }
  }

  const handleExternalToggle = async (camera: ExternalCamera, enabled: boolean) => {
    const config = getExternalConfig(camera.id)
    const isActive = config?.enabled ?? false

    if (enabled) {
      if (!isActive && isLimitReached) {
        setLimitWarning(true)
        return
      }
      try {
        setExternalActionLoading(camera.id)
        const updated = await startExternalCamera(camera.id)
        upsertExternalCamera(updated)
        setExternalError(null)
        setLimitWarning(false)
      } catch (err: any) {
        const message = err?.message || 'No se pudo iniciar la cámara externa.'
        setExternalError(message)
      } finally {
        setExternalActionLoading(null)
      }
    } else {
      try {
        setExternalActionLoading(camera.id)
        const updated = await stopExternalCamera(camera.id)
        upsertExternalCamera(updated)
        setLimitWarning(false)
      } catch (err: any) {
        const message = err?.message || 'No se pudo detener la cámara externa.'
        setExternalError(message)
      } finally {
        setExternalActionLoading(null)
      }
    }
  }

  const handleExternalRemove = async (camera: ExternalCamera) => {
    try {
      setExternalActionLoading(camera.id)
      await removeExternalCameraApi(camera.id)
      removeExternalCameraStore(camera.id)
      setExternalError(null)
      setLimitWarning(false)
    } catch (err: any) {
      const message = err?.message || 'No se pudo eliminar la cámara externa.'
      setExternalError(message)
    } finally {
      setExternalActionLoading(null)
    }
  }

  return (
    <section className="card mb-4">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-3 mb-3">
        <div>
          <h3 className="text-forest font-semibold mb-1">
            Gestión de Cámaras
          </h3>
        <p className="text-moss text-sm mb-0">
          Activa hasta <span className="text-forest font-semibold">{MAX_ACTIVE_CAMERAS}</span> cámaras simultáneas. Configura nombre,
          ubicación y calidad por dispositivo.
        </p>
        </div>
        <div className="flex gap-2">
          <button
            type="button"
            className="btn btn-secondary"
            onClick={() => refreshDevices(true)}
            disabled={loadingDevices}
          >
            {loadingDevices ? 'Actualizando...' : 'Detectar cámaras'}
          </button>
        </div>
      </div>

      {error && (
        <div className="alert alert-warning">
          {error}
        </div>
      )}

      {limitWarning && (
        <div className="alert alert-info">
          Límite máximo de {MAX_ACTIVE_CAMERAS} cámaras activas alcanzado. Desactiva una cámara para agregar otra.
        </div>
      )}

      <div className="flex flex-col gap-3">
        {deviceEntries.length === 0 && (
          <div className="text-moss text-sm">
            No hay cámaras disponibles. Conecta una cámara o autoriza el acceso.
          </div>
        )}

        {deviceEntries.map((device) => {
          const cameraConfig = findCameraByDeviceId(device.deviceId)
          const isActive = cameraConfig ? activeCameraIds.includes(cameraConfig.id) : false

          return (
            <div
              key={device.deviceId || device.label}
              className="card card-compact p-4"
            >
              <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-3">
                <div>
                  <h6 className="text-forest font-semibold mb-1">
                    {cameraConfig?.label ?? device.label ?? 'Cámara sin identificar'}
                  </h6>
                  <p className="text-moss text-sm mb-1">
                    {device.label || 'Identificador no disponible'}
                  </p>
                  <div className="tag">
                    {device.deviceId ? device.deviceId.slice(0, 12) : 'sin-id'}
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <span className="text-moss text-sm">
                    {isActive ? 'Activa' : 'Inactiva'}
                  </span>
                  <Toggle
                    enabled={isActive}
                    onChange={(value) => handleToggle(device.deviceId, value)}
                    disabled={!isActive && isLimitReached}
                  />
                </div>
              </div>

              {cameraConfig && (
                <div className="mt-3 pt-3 border-t border-gray-200">
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
                    <div>
                      <label className="label">Nombre / Alias</label>
                      <input
                        type="text"
                        className="input input-compact"
                        value={cameraConfig.label}
                        onChange={(event) => handleLabelChange(cameraConfig.id, event.target.value)}
                        placeholder="Ej. Cámara Entrada"
                      />
                    </div>
                    <div>
                      <label className="label">Ubicación</label>
                      <input
                        type="text"
                        className="input input-compact"
                        value={cameraConfig.location ?? ''}
                        onChange={(event) => handleLocationChange(cameraConfig.id, event.target.value)}
                        placeholder="Ej. Recepción"
                      />
                    </div>
                    <div>
                      <label className="label">Resolución</label>
                      <select
                        className="select"
                        value={cameraConfig.resolution}
                        onChange={(event) =>
                          handleResolutionChange(cameraConfig.id, event.target.value as CameraConfig['resolution'])
                        }
                      >
                        <option value="low">Baja (360p)</option>
                        <option value="medium">Media (480p)</option>
                        <option value="high">Alta (720p)</option>
                      </select>
                    </div>
                    <div>
                      <label className="label">FPS objetivo</label>
                      <input
                        type="number"
                        min={10}
                        max={60}
                        step={5}
                        className="input input-compact"
                        value={cameraConfig.targetFPS}
                        onChange={(event) => handleFpsChange(cameraConfig.id, Number(event.target.value))}
                      />
                    </div>
                  </div>
                </div>
              )}
            </div>
          )
        })}
      </div>

      <div className="mt-4 pt-3 border-t border-gray-200">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-3 mb-3">
          <div>
            <h6 className="text-forest font-semibold mb-2">Cámaras externas (RTSP / IP)</h6>
            <p className="text-moss text-sm mb-0">
              Conecta cámaras IP o RTSP mediante el gateway integrado. Se convierten a HLS para analizarlas con la IA en tiempo real.
            </p>
          </div>
          <button
            className="btn btn-secondary"
            type="button"
            onClick={() => setShowExternalForm((value) => !value)}
          >
            {showExternalForm ? 'Cerrar formulario' : 'Añadir cámara externa'}
          </button>
        </div>

        {externalError && (
          <div className="alert alert-warning mb-3">
            {externalError}
          </div>
        )}

        {showExternalForm && (
          <ExternalCameraForm
            onSubmit={handleCreateExternal}
            onCancel={() => setShowExternalForm(false)}
            loading={externalFormLoading}
          />
        )}

        {loadingExternal ? (
          <div className="text-moss text-sm">Cargando cámaras externas…</div>
        ) : externalCameras.length === 0 ? (
          <div className="text-moss text-sm">
            No hay cámaras externas registradas. Añade una URL RTSP o HTTP para comenzar el streaming.
          </div>
        ) : (
          <div className="flex flex-col gap-3">
            {externalCameras.map((camera) => {
              const cameraConfig = getExternalConfig(camera.id)
              const isActive = cameraConfig?.enabled ?? false
              const actionLoading = externalActionLoading === camera.id

              return (
                <div key={camera.id} className="card card-compact p-4">
                  <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-3">
                    <div>
                      <h6 className="text-forest font-semibold mb-1">{camera.name}</h6>
                      <p className="text-moss text-sm mb-1 truncate" style={{ maxWidth: '420px' }}>
                        {camera.source_url}
                      </p>
                      <span className="tag capitalize">
                        {camera.status}
                      </span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-moss text-sm">
                        {isActive ? 'Activa' : camera.status === 'starting' ? 'Conectando…' : 'Inactiva'}
                      </span>
                      <Toggle
                        enabled={isActive}
                        onChange={(value) => handleExternalToggle(camera, value)}
                        disabled={(!isActive && isLimitReached) || actionLoading}
                      />
                    </div>
                  </div>
                  <div className="flex justify-between items-center text-moss text-sm mt-2">
                    <span>{camera.hls_url ? 'Stream listo para análisis.' : 'Esperando señal del gateway.'}</span>
                    {camera.hls_url && (
                      <a
                        href={camera.hls_url}
                        target="_blank"
                        rel="noreferrer"
                        className="text-pine hover:text-forest"
                      >
                        Abrir HLS
                      </a>
                    )}
                  </div>
                  <div className="flex gap-2 mt-3">
                    <button
                      type="button"
                      className="btn btn-danger"
                      onClick={() => handleExternalRemove(camera)}
                      disabled={actionLoading}
                    >
                      Eliminar
                    </button>
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </div>
    </section>
  )
}
