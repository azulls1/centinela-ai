import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import {
  Camera,
  Video,
  Wifi,
  WifiOff,
  Plus,
  RefreshCw,
  Settings2,
  MapPin,
  Tag,
  Gauge,
  Monitor,
  Trash2,
  ChevronRight,
} from 'lucide-react'
import { MAX_ACTIVE_CAMERAS, useAppStore } from '../store/appStore'
import { Toggle } from '../components/Toggle'
import { ExternalCameraForm } from '../components/ExternalCameraForm'
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

const RESOLUTION_LABELS: Record<CameraConfig['resolution'], string> = {
  low: 'SD 640x480',
  medium: 'HD 1280x720',
  high: 'Full HD 1920x1080',
}

const fadeInUp = {
  initial: { opacity: 0, y: 16 },
  animate: { opacity: 1, y: 0 },
}

export function CamerasPage() {
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
  const [expandedCamera, setExpandedCamera] = useState<string | null>(null)

  const deviceEntries = useMemo<DeviceOption[]>(() => {
    return availableDevices.map((device) => ({
      deviceId: device.deviceId,
      label: device.label || 'Camara sin identificar',
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

  // ---- Device enumeration ----
  const refreshDevices = async (requestPermissions = false) => {
    if (!navigator.mediaDevices?.enumerateDevices) {
      setError('El navegador no soporta enumeracion de dispositivos multimedia.')
      return
    }

    try {
      setLoadingDevices(true)
      setError(null)

      if (requestPermissions) {
        try {
          const permissionStream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false })
          permissionStream.getTracks().forEach((track) => track.stop())
        } catch (_permissionError) {
          setError('Permisos de camara denegados. Autoriza el acceso para listar camaras.')
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
        setError('No se detectaron camaras. Conecta un dispositivo o agrega una camara externa.')
      }
    } catch (_err) {
      setError('Ocurrio un error al listar las camaras.')
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

  // ---- External cameras fetch ----
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
          const message = err?.message || 'No se pudieron cargar las camaras externas.'
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

  // ---- Local camera handlers ----
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

  const handleModelToggle = (cameraId: string, model: keyof CameraConfig['models'], value: boolean) => {
    const current = cameraConfigs[cameraId]?.models
    if (!current) return
    updateCameraConfig(cameraId, { models: { ...current, [model]: value } })
  }

  // ---- External camera handlers ----
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
      const message = err?.message || 'No se pudo registrar la camara externa.'
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
        const message = err?.message || 'No se pudo iniciar la camara externa.'
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
        const message = err?.message || 'No se pudo detener la camara externa.'
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
      const message = err?.message || 'No se pudo eliminar la camara externa.'
      setExternalError(message)
    } finally {
      setExternalActionLoading(null)
    }
  }

  // ---- Derived data for active cameras summary ----
  const activeCameras = useMemo(() => {
    return activeCameraIds
      .map((id) => cameraConfigs[id])
      .filter((cfg): cfg is CameraConfig => !!cfg && cfg.enabled)
  }, [activeCameraIds, cameraConfigs])

  const MODEL_LABELS: Record<keyof CameraConfig['models'], string> = {
    personDetection: 'Personas',
    faceDetection: 'Rostros',
    emotionDetection: 'Emociones',
    movementDetection: 'Movimiento',
    objectDetection: 'Objetos',
  }

  return (
    <div className="page-shell py-4">
      {/* Hero header */}
      <motion.section
        initial={{ opacity: 0, y: -12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="card-hero mb-6"
      >
        <div>
          <span className="badge--on-dark mb-3 inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-semibold">
            Gestion de Camaras
          </span>
          <h1 className="card-hero__title font-display">Configuracion de Camaras</h1>
          <p className="card-hero__desc text-lg mb-0">
            Administra tus camaras locales e IP/RTSP. Configura nombre, ubicacion, resolucion, modelos de deteccion y FPS por dispositivo.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Link to="/" className="btn btn-secondary flex items-center gap-2">
            <Video size={16} />
            Ir a Live
            <ChevronRight size={14} />
          </Link>
        </div>
      </motion.section>

      {/* Limit / error alerts */}
      {limitWarning && (
        <motion.div {...fadeInUp} transition={{ duration: 0.3 }} className="alert alert-info mb-4">
          Limite maximo de {MAX_ACTIVE_CAMERAS} camaras activas alcanzado. Desactiva una camara para agregar otra.
        </motion.div>
      )}
      {error && (
        <motion.div {...fadeInUp} transition={{ duration: 0.3 }} className="alert alert-warning mb-4">
          {error}
        </motion.div>
      )}

      {/* ===== CAMARAS ACTIVAS (summary) ===== */}
      <motion.section
        {...fadeInUp}
        transition={{ duration: 0.5, delay: 0.1 }}
        className="mb-6"
      >
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-forest font-semibold text-lg flex items-center gap-2">
            <Monitor size={20} />
            Camaras Activas
          </h2>
          <span className="badge badge-active">
            {activeCameras.length}/{MAX_ACTIVE_CAMERAS}
          </span>
        </div>

        {activeCameras.length === 0 ? (
          <div className="card p-6 text-center text-moss">
            No hay camaras activas. Activa una camara desde las secciones de abajo.
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {activeCameras.map((cfg, index) => (
              <motion.div
                key={cfg.id}
                {...fadeInUp}
                transition={{ duration: 0.4, delay: 0.05 * index }}
                className="card p-4"
              >
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <div className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse" />
                    <h6 className="text-forest font-semibold mb-0">{cfg.label}</h6>
                  </div>
                  <span className="badge badge-active text-xs">Online</span>
                </div>
                {cfg.location && (
                  <p className="text-moss text-sm mb-1 flex items-center gap-1">
                    <MapPin size={12} />
                    {cfg.location}
                  </p>
                )}
                <div className="flex flex-wrap gap-1.5 mt-2">
                  <span className="tag text-xs">{RESOLUTION_LABELS[cfg.resolution]}</span>
                  <span className="tag text-xs">{cfg.targetFPS} FPS</span>
                  <span className="tag text-xs capitalize">{cfg.sourceType === 'external' ? 'IP/RTSP' : 'Local'}</span>
                </div>
              </motion.div>
            ))}
          </div>
        )}
      </motion.section>

      {/* ===== CAMARAS LOCALES ===== */}
      <motion.section
        {...fadeInUp}
        transition={{ duration: 0.5, delay: 0.2 }}
        className="mb-6"
      >
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-3 mb-3">
          <h2 className="text-forest font-semibold text-lg flex items-center gap-2">
            <Camera size={20} />
            Camaras Locales
          </h2>
          <button
            type="button"
            className="btn btn-secondary flex items-center gap-2"
            onClick={() => refreshDevices(true)}
            disabled={loadingDevices}
          >
            <RefreshCw size={14} className={loadingDevices ? 'animate-spin' : ''} />
            {loadingDevices ? 'Detectando...' : 'Detectar camaras'}
          </button>
        </div>

        {deviceEntries.length === 0 ? (
          <div className="card p-6 text-center text-moss">
            No hay camaras locales disponibles. Conecta una webcam o autoriza el acceso.
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {deviceEntries.map((device, index) => {
              const cameraConfig = findCameraByDeviceId(device.deviceId)
              const isActive = cameraConfig ? activeCameraIds.includes(cameraConfig.id) : false
              const isExpanded = expandedCamera === (cameraConfig?.id ?? device.deviceId)

              return (
                <motion.div
                  key={device.deviceId || device.label}
                  {...fadeInUp}
                  transition={{ duration: 0.4, delay: 0.05 * index }}
                  className="card p-4"
                >
                  <div className="flex justify-between items-start gap-3">
                    <div className="min-w-0 flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        {isActive ? (
                          <Wifi size={14} className="text-emerald-500 flex-shrink-0" />
                        ) : (
                          <WifiOff size={14} className="text-gray-400 flex-shrink-0" />
                        )}
                        <h6 className="text-forest font-semibold mb-0 truncate">
                          {cameraConfig?.label ?? device.label ?? 'Camara sin identificar'}
                        </h6>
                      </div>
                      <p className="text-moss text-xs mb-1 truncate">
                        {device.label || 'Identificador no disponible'}
                      </p>
                      <div className="tag text-xs">
                        {device.deviceId ? device.deviceId.slice(0, 12) : 'sin-id'}
                      </div>
                    </div>

                    <div className="flex items-center gap-3 flex-shrink-0">
                      {cameraConfig && (
                        <button
                          type="button"
                          className="text-moss hover:text-forest transition-colors"
                          onClick={() =>
                            setExpandedCamera(isExpanded ? null : (cameraConfig?.id ?? device.deviceId))
                          }
                          title="Configurar"
                        >
                          <Settings2 size={16} />
                        </button>
                      )}
                      <div className="flex items-center gap-2">
                        <span className="text-moss text-sm">{isActive ? 'Activa' : 'Inactiva'}</span>
                        <Toggle
                          enabled={isActive}
                          onChange={(value) => handleToggle(device.deviceId, value)}
                          disabled={!isActive && isLimitReached}
                        />
                      </div>
                    </div>
                  </div>

                  {/* Expanded configuration panel */}
                  {cameraConfig && isExpanded && (
                    <motion.div
                      initial={{ opacity: 0, height: 0 }}
                      animate={{ opacity: 1, height: 'auto' }}
                      exit={{ opacity: 0, height: 0 }}
                      transition={{ duration: 0.3 }}
                      className="mt-4 pt-4 border-t border-gray-200"
                    >
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mb-4">
                        <div>
                          <label className="label flex items-center gap-1">
                            <Tag size={12} />
                            Nombre / Alias
                          </label>
                          <input
                            type="text"
                            className="input input-compact"
                            value={cameraConfig.label}
                            onChange={(e) => handleLabelChange(cameraConfig.id, e.target.value)}
                            placeholder="Ej. Camara Entrada"
                          />
                        </div>
                        <div>
                          <label className="label flex items-center gap-1">
                            <MapPin size={12} />
                            Ubicacion
                          </label>
                          <input
                            type="text"
                            className="input input-compact"
                            value={cameraConfig.location ?? ''}
                            onChange={(e) => handleLocationChange(cameraConfig.id, e.target.value)}
                            placeholder="Ej. Recepcion"
                          />
                        </div>
                        <div>
                          <label className="label flex items-center gap-1">
                            <Monitor size={12} />
                            Resolucion
                          </label>
                          <select
                            className="select"
                            value={cameraConfig.resolution}
                            onChange={(e) =>
                              handleResolutionChange(cameraConfig.id, e.target.value as CameraConfig['resolution'])
                            }
                          >
                            <option value="low">SD 640x480</option>
                            <option value="medium">HD 1280x720</option>
                            <option value="high">Full HD 1920x1080</option>
                          </select>
                        </div>
                        <div>
                          <label className="label flex items-center gap-1">
                            <Gauge size={12} />
                            FPS objetivo
                          </label>
                          <input
                            type="number"
                            min={10}
                            max={60}
                            step={5}
                            className="input input-compact"
                            value={cameraConfig.targetFPS}
                            onChange={(e) => handleFpsChange(cameraConfig.id, Number(e.target.value))}
                          />
                        </div>
                      </div>

                      {/* Detection model toggles */}
                      <div>
                        <label className="label mb-2">Modelos de deteccion</label>
                        <div className="flex flex-wrap gap-3">
                          {(Object.keys(MODEL_LABELS) as (keyof CameraConfig['models'])[]).map((model) => (
                            <label key={model} className="flex items-center gap-2 text-sm text-moss cursor-pointer">
                              <input
                                type="checkbox"
                                className="accent-forest"
                                checked={cameraConfig.models[model]}
                                onChange={(e) => handleModelToggle(cameraConfig.id, model, e.target.checked)}
                              />
                              {MODEL_LABELS[model]}
                            </label>
                          ))}
                        </div>
                      </div>
                    </motion.div>
                  )}
                </motion.div>
              )
            })}
          </div>
        )}
      </motion.section>

      {/* ===== CAMARAS EXTERNAS (IP/RTSP) ===== */}
      <motion.section
        {...fadeInUp}
        transition={{ duration: 0.5, delay: 0.3 }}
      >
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-3 mb-3">
          <div>
            <h2 className="text-forest font-semibold text-lg flex items-center gap-2">
              <Wifi size={20} />
              Camaras Externas (IP/RTSP)
            </h2>
            <p className="text-moss text-sm mb-0 mt-1">
              Conecta camaras IP o RTSP mediante el gateway integrado. Se convierten a HLS para analizarlas con IA en tiempo real.
            </p>
          </div>
          <button
            type="button"
            className="btn btn-primary flex items-center gap-2"
            onClick={() => setShowExternalForm((v) => !v)}
          >
            <Plus size={14} />
            {showExternalForm ? 'Cerrar formulario' : 'Anadir camara externa'}
          </button>
        </div>

        {externalError && (
          <div className="alert alert-warning mb-3">{externalError}</div>
        )}

        {showExternalForm && (
          <motion.div {...fadeInUp} transition={{ duration: 0.3 }}>
            <ExternalCameraForm
              onSubmit={handleCreateExternal}
              onCancel={() => setShowExternalForm(false)}
              loading={externalFormLoading}
            />
          </motion.div>
        )}

        {loadingExternal ? (
          <div className="card p-6 text-center text-moss">Cargando camaras externas...</div>
        ) : externalCameras.length === 0 ? (
          <div className="card p-6 text-center text-moss">
            No hay camaras externas registradas. Anade una URL RTSP o HTTP para comenzar el streaming.
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {externalCameras.map((camera, index) => {
              const cameraConfig = getExternalConfig(camera.id)
              const isActive = cameraConfig?.enabled ?? false
              const actionLoading = externalActionLoading === camera.id
              const configId = `external-${camera.id}`
              const isExpanded = expandedCamera === configId

              return (
                <motion.div
                  key={camera.id}
                  {...fadeInUp}
                  transition={{ duration: 0.4, delay: 0.05 * index }}
                  className="card p-4"
                >
                  <div className="flex justify-between items-start gap-3">
                    <div className="min-w-0 flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        {isActive ? (
                          <Wifi size={14} className="text-emerald-500 flex-shrink-0" />
                        ) : (
                          <WifiOff size={14} className="text-gray-400 flex-shrink-0" />
                        )}
                        <h6 className="text-forest font-semibold mb-0 truncate">{camera.name}</h6>
                      </div>
                      <p className="text-moss text-xs mb-1 truncate" style={{ maxWidth: '320px' }}>
                        {camera.source_url}
                      </p>
                      <div className="flex items-center gap-2">
                        <span className="tag text-xs capitalize">{camera.status}</span>
                        {camera.hls_url && (
                          <a
                            href={camera.hls_url}
                            target="_blank"
                            rel="noreferrer"
                            className="text-pine hover:text-forest text-xs underline"
                          >
                            Abrir HLS
                          </a>
                        )}
                      </div>
                    </div>

                    <div className="flex items-center gap-3 flex-shrink-0">
                      {cameraConfig && (
                        <button
                          type="button"
                          className="text-moss hover:text-forest transition-colors"
                          onClick={() => setExpandedCamera(isExpanded ? null : configId)}
                          title="Configurar"
                        >
                          <Settings2 size={16} />
                        </button>
                      )}
                      <div className="flex items-center gap-2">
                        <span className="text-moss text-sm">
                          {isActive ? 'Activa' : camera.status === 'starting' ? 'Conectando...' : 'Inactiva'}
                        </span>
                        <Toggle
                          enabled={isActive}
                          onChange={(value) => handleExternalToggle(camera, value)}
                          disabled={(!isActive && isLimitReached) || actionLoading}
                        />
                      </div>
                    </div>
                  </div>

                  {/* Expanded configuration for external cameras */}
                  {cameraConfig && isExpanded && (
                    <motion.div
                      initial={{ opacity: 0, height: 0 }}
                      animate={{ opacity: 1, height: 'auto' }}
                      exit={{ opacity: 0, height: 0 }}
                      transition={{ duration: 0.3 }}
                      className="mt-4 pt-4 border-t border-gray-200"
                    >
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mb-4">
                        <div>
                          <label className="label flex items-center gap-1">
                            <Monitor size={12} />
                            Resolucion
                          </label>
                          <select
                            className="select"
                            value={cameraConfig.resolution}
                            onChange={(e) =>
                              handleResolutionChange(configId, e.target.value as CameraConfig['resolution'])
                            }
                          >
                            <option value="low">SD 640x480</option>
                            <option value="medium">HD 1280x720</option>
                            <option value="high">Full HD 1920x1080</option>
                          </select>
                        </div>
                        <div>
                          <label className="label flex items-center gap-1">
                            <Gauge size={12} />
                            FPS objetivo
                          </label>
                          <input
                            type="number"
                            min={10}
                            max={60}
                            step={5}
                            className="input input-compact"
                            value={cameraConfig.targetFPS}
                            onChange={(e) => handleFpsChange(configId, Number(e.target.value))}
                          />
                        </div>
                      </div>

                      <div className="mb-4">
                        <label className="label mb-2">Modelos de deteccion</label>
                        <div className="flex flex-wrap gap-3">
                          {(Object.keys(MODEL_LABELS) as (keyof CameraConfig['models'])[]).map((model) => (
                            <label key={model} className="flex items-center gap-2 text-sm text-moss cursor-pointer">
                              <input
                                type="checkbox"
                                className="accent-forest"
                                checked={cameraConfig.models[model]}
                                onChange={(e) => handleModelToggle(configId, model, e.target.checked)}
                              />
                              {MODEL_LABELS[model]}
                            </label>
                          ))}
                        </div>
                      </div>

                      <button
                        type="button"
                        className="btn btn-danger flex items-center gap-2"
                        onClick={() => handleExternalRemove(camera)}
                        disabled={actionLoading}
                      >
                        <Trash2 size={14} />
                        Eliminar camara
                      </button>
                    </motion.div>
                  )}
                </motion.div>
              )
            })}
          </div>
        )}
      </motion.section>
    </div>
  )
}
