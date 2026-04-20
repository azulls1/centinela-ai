import { useEffect, useState, useRef, useMemo, useCallback } from 'react'
import { CameraFeed } from '../components/CameraFeed'
import { DetectionPanel } from '../components/DetectionPanel'
import { MAX_ACTIVE_CAMERAS, useAppStore } from '../store/appStore'
import { insertEvent } from '../lib/supabase'
import { loadModels } from '../lib/ml/processors'
import { motion } from 'framer-motion'
import {
  Video,
  PanelRightClose,
  PanelRightOpen,
  RefreshCw,
  Camera,
  Wifi,
  WifiOff,
  Plus,
  Settings2,
  MapPin,
  Tag,
  Gauge,
  Monitor,
  Trash2,
} from 'lucide-react'
import { SessionStartModal } from '../components/SessionStartModal'
import { heartbeatSession, initDemoSession } from '../lib/sessions'
import { Toggle } from '../components/Toggle'
import { ExternalCameraForm } from '../components/ExternalCameraForm'
import {
  createExternalCamera,
  fetchExternalCameras,
  removeExternalCamera as removeExternalCameraApi,
  startExternalCamera,
  stopExternalCamera,
} from '../lib/externalCameras'
import type { CameraConfig, DemoSessionRecord, ExternalCamera, ExternalCameraPayload } from '../types'
import { logWarn } from '../utils/logger'

const logError = (message: string, error?: unknown) => {
  console.error(`[LivePage] ${message}`, error)
}

/** FPS status dot: green >= 24, amber >= 15, red < 15 */
function FpsStatusDot({ fps }: { fps: number }) {
  const color =
    fps >= 24 ? 'bg-emerald-500' : fps >= 15 ? 'bg-amber-500' : 'bg-red-500'
  return (
    <span
      className={`inline-block w-2.5 h-2.5 rounded-full ${color}`}
      title={`${fps.toFixed(1)} FPS`}
    />
  )
}

const _RESOLUTION_LABELS: Record<CameraConfig['resolution'], string> = {
  low: 'SD 640x480',
  medium: 'HD 1280x720',
  high: 'Full HD 1920x1080',
}

const MODEL_LABELS: Record<keyof CameraConfig['models'], string> = {
  personDetection: 'Personas',
  faceDetection: 'Rostros',
  emotionDetection: 'Emociones',
  movementDetection: 'Movimiento',
  objectDetection: 'Objetos',
}

interface DeviceOption {
  deviceId: string
  label: string
  groupId?: string
}

/**
 * Pagina principal - Live + gestion completa de camaras
 * Camara se activa automaticamente al iniciar sesion
 * Panel de gestion de camaras integrado (colapsable)
 */
export function LivePage() {
  const [modelsLoading, setModelsLoading] = useState(false)
  const detectionState = useAppStore((state) => state.detectionState)
  const aggregatedDetections = useAppStore((state) => state.aggregatedDetections)
  const cameraDetections = useAppStore((state) => state.cameraDetections)
  const activeCameraIds = useAppStore((state) => state.activeCameraIds)
  const cameraConfigs = useAppStore((state) => state.cameraConfigs)
  const addEvent = useAppStore((state) => state.addEvent)
  const activateCamera = useAppStore((state) => state.activateCamera)
  const deactivateCamera = useAppStore((state) => state.deactivateCamera)
  const updateCameraConfig = useAppStore((state) => state.updateCameraConfig)
  const availableDevices = useAppStore((state) => state.availableDevices)
  const setAvailableDevices = useAppStore((state) => state.setAvailableDevices)
  const externalCameras = useAppStore((state) => state.externalCameras)
  const setExternalCamerasStore = useAppStore((state) => state.setExternalCameras)
  const upsertExternalCamera = useAppStore((state) => state.upsertExternalCamera)
  const removeExternalCameraStore = useAppStore((state) => state.removeExternalCamera)

  const { sessionInfo, setSessionInfo, updateSessionInfo, clearSessionInfo } = useAppStore((state) => ({
    sessionInfo: state.sessionInfo,
    setSessionInfo: state.setSessionInfo,
    updateSessionInfo: state.updateSessionInfo,
    clearSessionInfo: state.clearSessionInfo,
  }))
  const [sessionModalOpen, setSessionModalOpen] = useState(false)
  const [sessionSubmitting, setSessionSubmitting] = useState(false)
  const [sessionError, setSessionError] = useState<string | null>(null)
  const [endingSession, setEndingSession] = useState(false)
  const [rightPanelVisible, setRightPanelVisible] = useState(true)
  const [cameraError, setCameraError] = useState<string | null>(null)

  // Camera management panel state
  const [loadingDevices, setLoadingDevices] = useState(false)
  const [deviceError, setDeviceError] = useState<string | null>(null)
  const [limitWarning, setLimitWarning] = useState(false)
  const [expandedCamera, setExpandedCamera] = useState<string | null>(null)
  const [loadingExternal, setLoadingExternal] = useState(false)
  const [externalError, setExternalError] = useState<string | null>(null)
  const [showExternalForm, setShowExternalForm] = useState(false)
  const [externalFormLoading, setExternalFormLoading] = useState(false)
  const [externalActionLoading, setExternalActionLoading] = useState<string | null>(null)

  const fps = useMemo(() => detectionState.currentFPS, [detectionState.currentFPS])
  const [processingDisplay, setProcessingDisplay] = useState<'scanning' | 'ready'>('ready')
  const processingTimeoutRef = useRef<number | undefined>(undefined)
  const modelsInitializedRef = useRef(false)
  const cameraAutoActivatedRef = useRef(false)

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
  const refreshDevices = useCallback(async (requestPermissions = false) => {
    if (!navigator.mediaDevices?.enumerateDevices) {
      setDeviceError('El navegador no soporta enumeracion de dispositivos multimedia.')
      return
    }

    try {
      setLoadingDevices(true)
      setDeviceError(null)

      if (requestPermissions) {
        try {
          const permissionStream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false })
          permissionStream.getTracks().forEach((track) => track.stop())
        } catch (_permissionError) {
          setDeviceError('Permisos de camara denegados. Autoriza el acceso para listar camaras.')
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
        setDeviceError('No se detectaron camaras. Conecta un dispositivo o agrega una camara externa.')
      }
    } catch (_err) {
      setDeviceError('Ocurrio un error al listar las camaras.')
    } finally {
      setLoadingDevices(false)
    }
  }, [setAvailableDevices])

  useEffect(() => {
    setSessionModalOpen(!sessionInfo)
  }, [sessionInfo])

  // ---- Auto-enumerate and activate camera when session starts ----
  useEffect(() => {
    if (!sessionInfo?.session_id || cameraAutoActivatedRef.current) return
    if (activeCameraIds.length > 0) {
      cameraAutoActivatedRef.current = true
      return
    }

    let cancelled = false

    const autoActivateCamera = async () => {
      if (!navigator.mediaDevices?.enumerateDevices) {
        setCameraError('El navegador no soporta acceso a camaras.')
        return
      }

      try {
        const permissionStream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false })
        permissionStream.getTracks().forEach((track) => track.stop())
        if (cancelled) return

        const devices = await navigator.mediaDevices.enumerateDevices()
        const videoInputs = devices
          .filter((device) => device.kind === 'videoinput')
          .map((device) => ({ deviceId: device.deviceId, label: device.label, groupId: device.groupId }))
        if (cancelled) return

        setAvailableDevices(videoInputs)

        if (videoInputs.length === 0) {
          setCameraError('No se detectaron camaras. Conecta un dispositivo.')
          return
        }

        const cameraId = activateCamera(videoInputs[0].deviceId)
        if (cameraId) {
          cameraAutoActivatedRef.current = true
          setCameraError(null)
        }
      } catch (err: any) {
        if (cancelled) return
        if (err?.name === 'NotAllowedError' || err?.name === 'PermissionDeniedError') {
          setCameraError('Permisos de camara denegados. Autoriza el acceso en tu navegador.')
        } else {
          setCameraError('No se pudo acceder a las camaras.')
        }
      }
    }

    autoActivateCamera()

    const handleDeviceChange = () => {
      navigator.mediaDevices.enumerateDevices().then((devices) => {
        const videoInputs = devices
          .filter((d) => d.kind === 'videoinput')
          .map((d) => ({ deviceId: d.deviceId, label: d.label, groupId: d.groupId }))
        setAvailableDevices(videoInputs)
      }).catch(() => {})
    }
    navigator.mediaDevices?.addEventListener('devicechange', handleDeviceChange)
    return () => {
      cancelled = true
      navigator.mediaDevices?.removeEventListener('devicechange', handleDeviceChange)
    }
  }, [sessionInfo?.session_id, activeCameraIds.length, activateCamera, setAvailableDevices])

  useEffect(() => {
    if (!sessionInfo) cameraAutoActivatedRef.current = false
  }, [sessionInfo])

  // ---- Load external cameras ----
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
        if (mounted) setExternalError(err?.message || 'No se pudieron cargar las camaras externas.')
      } finally {
        if (mounted) setLoadingExternal(false)
      }
    }
    loadExternalCameras()
    return () => { mounted = false }
  }, [setExternalCamerasStore])

  // ---- Local camera handlers ----
  const findCameraByDeviceId = useCallback((deviceId: string): CameraConfig | undefined =>
    Object.values(cameraConfigs).find((camera) => camera.deviceId === deviceId)
  , [cameraConfigs])

  const handleToggle = useCallback((deviceId: string, enabled: boolean) => {
    if (enabled) {
      setLimitWarning(false)
      const cameraId = activateCamera(deviceId)
      if (!cameraId) setLimitWarning(true)
    } else {
      const camera = findCameraByDeviceId(deviceId)
      if (camera) deactivateCamera(camera.id)
    }
  }, [activateCamera, deactivateCamera, findCameraByDeviceId])

  const handleLabelChange = useCallback((cameraId: string, label: string) => {
    updateCameraConfig(cameraId, { label })
  }, [updateCameraConfig])

  const handleLocationChange = useCallback((cameraId: string, location: string) => {
    updateCameraConfig(cameraId, { location })
  }, [updateCameraConfig])

  const handleResolutionChange = useCallback((cameraId: string, resolution: CameraConfig['resolution']) => {
    updateCameraConfig(cameraId, { resolution })
  }, [updateCameraConfig])

  const handleFpsChange = useCallback((cameraId: string, fpsValue: number) => {
    updateCameraConfig(cameraId, { targetFPS: fpsValue })
  }, [updateCameraConfig])

  const handleModelToggle = useCallback((cameraId: string, model: keyof CameraConfig['models'], value: boolean) => {
    const current = cameraConfigs[cameraId]?.models
    if (!current) return
    updateCameraConfig(cameraId, { models: { ...current, [model]: value } })
  }, [cameraConfigs, updateCameraConfig])

  // ---- External camera handlers ----
  const getExternalConfig = useCallback((cameraId: string) => cameraConfigs[`external-${cameraId}`], [cameraConfigs])

  const handleCreateExternal = useCallback(async (payload: ExternalCameraPayload) => {
    try {
      setExternalFormLoading(true)
      const camera = await createExternalCamera(payload)
      upsertExternalCamera(camera)
      setExternalError(null)
      setShowExternalForm(false)
      setLimitWarning(false)
    } catch (err: any) {
      setExternalError(err?.message || 'No se pudo registrar la camara externa.')
      throw err
    } finally {
      setExternalFormLoading(false)
    }
  }, [upsertExternalCamera])

  const handleExternalToggle = useCallback(async (camera: ExternalCamera, enabled: boolean) => {
    const config = getExternalConfig(camera.id)
    const isActive = config?.enabled ?? false
    if (enabled) {
      if (!isActive && isLimitReached) { setLimitWarning(true); return }
      try {
        setExternalActionLoading(camera.id)
        const updated = await startExternalCamera(camera.id)
        upsertExternalCamera(updated)
        setExternalError(null)
        setLimitWarning(false)
      } catch (err: any) {
        setExternalError(err?.message || 'No se pudo iniciar la camara externa.')
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
        setExternalError(err?.message || 'No se pudo detener la camara externa.')
      } finally {
        setExternalActionLoading(null)
      }
    }
  }, [getExternalConfig, isLimitReached, upsertExternalCamera])

  const handleExternalRemove = useCallback(async (camera: ExternalCamera) => {
    try {
      setExternalActionLoading(camera.id)
      await removeExternalCameraApi(camera.id)
      removeExternalCameraStore(camera.id)
      setExternalError(null)
      setLimitWarning(false)
    } catch (err: any) {
      setExternalError(err?.message || 'No se pudo eliminar la camara externa.')
    } finally {
      setExternalActionLoading(null)
    }
  }, [removeExternalCameraStore])

  const handleRetryCamera = useCallback(async () => {
    setCameraError(null)
    cameraAutoActivatedRef.current = false
    try {
      const permissionStream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false })
      permissionStream.getTracks().forEach((track) => track.stop())
      const devices = await navigator.mediaDevices.enumerateDevices()
      const videoInputs = devices
        .filter((device) => device.kind === 'videoinput')
        .map((device) => ({ deviceId: device.deviceId, label: device.label, groupId: device.groupId }))
      setAvailableDevices(videoInputs)
      if (videoInputs.length > 0) {
        const cameraId = activateCamera(videoInputs[0].deviceId)
        if (cameraId) cameraAutoActivatedRef.current = true
      } else {
        setCameraError('No se detectaron camaras.')
      }
    } catch (err: any) {
      setCameraError(err?.name === 'NotAllowedError' ? 'Permisos de camara denegados.' : 'No se pudo acceder a las camaras.')
    }
  }, [activateCamera, setAvailableDevices])

  // ---- Session handlers ----
  const handleSessionSubmit = useCallback(
    async ({ name, email, organization, plan, purpose }: {
      name: string; email: string; organization?: string; plan: string; purpose?: string
    }) => {
      if (!globalThis.crypto?.randomUUID) {
        setSessionError('El navegador no soporta UUIDs seguros. Actualiza tu navegador.')
        return
      }
      setSessionSubmitting(true)
      setSessionError(null)
      const sessionId = globalThis.crypto.randomUUID()
      const optimisticRecord: DemoSessionRecord = {
        session_id: sessionId, name, email, plan,
        metadata: { organization, purpose } as Record<string, unknown>,
        status: 'initializing', started_at: new Date().toISOString(),
        last_ping_at: new Date().toISOString(), cameras_active: 0, fps_average: 0, tokens_used: 0,
      }
      setSessionInfo(optimisticRecord)
      setSessionModalOpen(false)
      try {
        const record = await initDemoSession({ sessionId, name, email, plan, metadata: { organization, purpose } })
        setSessionInfo(record)
      } catch (error) {
        setSessionError(error instanceof Error ? error.message : 'No se pudo iniciar la sesion.')
        setSessionModalOpen(true)
        clearSessionInfo()
        modelsInitializedRef.current = false
      } finally {
        setSessionSubmitting(false)
      }
    }, [clearSessionInfo, setSessionInfo])

  const handleEndSession = useCallback(async () => {
    if (!sessionInfo?.session_id || endingSession) return
    setEndingSession(true)
    setSessionError(null)
    try {
      await heartbeatSession({
        sessionId: sessionInfo.session_id, camerasActive: activeCameraIds.length,
        fpsAverage: Number.isFinite(aggregatedDetections.averageFPS) ? Number(aggregatedDetections.averageFPS.toFixed(2)) : 0,
        tokensUsed: sessionInfo.tokens_used ?? 0, status: 'terminated',
      })
    } catch (error) {
      setSessionError(error instanceof Error ? error.message : 'No se pudo cerrar la sesion.')
      setEndingSession(false)
      return
    }
    clearSessionInfo()
    setSessionModalOpen(true)
    setEndingSession(false)
    modelsInitializedRef.current = false
  }, [sessionInfo?.session_id, sessionInfo?.tokens_used, activeCameraIds.length, aggregatedDetections.averageFPS, clearSessionInfo, endingSession])

  // ---- Heartbeat ----
  useEffect(() => {
    if (!sessionInfo?.session_id) return
    let cancelled = false
    const sendHeartbeat = async () => {
      if (cancelled) return
      try {
        const statusOverride = sessionInfo.status === 'initializing' ? 'active' : undefined
        const response = await heartbeatSession({
          sessionId: sessionInfo.session_id, camerasActive: activeCameraIds.length,
          fpsAverage: Number.isFinite(aggregatedDetections.averageFPS) ? Number(aggregatedDetections.averageFPS.toFixed(2)) : 0,
          status: statusOverride,
        })
        if (!cancelled && response) {
          const newStatus = (response.status ?? sessionInfo.status ?? '').toLowerCase()
          updateSessionInfo({ status: response.status ?? sessionInfo.status, last_ping_at: response.last_ping_at, cameras_active: response.cameras_active, fps_average: response.fps_average, tokens_used: response.tokens_used })
          if (newStatus === 'terminated' || newStatus === 'banned') {
            setSessionError(newStatus === 'terminated' ? 'La sesion fue cerrada por un administrador.' : 'Tu acceso fue bloqueado.')
            clearSessionInfo(); setSessionModalOpen(true); return
          }
          if (newStatus === 'limit') setSessionError('Has alcanzado el limite asignado.')
        }
      } catch (error) {
        logWarn('Error enviando heartbeat', error)
        setSessionError('Perdimos la conexion con el servidor.')
      }
    }
    sendHeartbeat()
    const interval = window.setInterval(sendHeartbeat, 15000)
    return () => { cancelled = true; window.clearInterval(interval) }
  }, [sessionInfo?.session_id, sessionInfo?.status, activeCameraIds.length, aggregatedDetections.averageFPS, updateSessionInfo, clearSessionInfo])

  // ---- Processing display ----
  useEffect(() => {
    if (aggregatedDetections.camerasProcessing > 0) {
      if (processingTimeoutRef.current !== undefined) { window.clearTimeout(processingTimeoutRef.current); processingTimeoutRef.current = undefined }
      setProcessingDisplay('scanning')
    } else if (processingDisplay !== 'ready') {
      processingTimeoutRef.current = window.setTimeout(() => { setProcessingDisplay('ready'); processingTimeoutRef.current = undefined }, 900)
    }
    return () => { if (processingTimeoutRef.current !== undefined) { window.clearTimeout(processingTimeoutRef.current); processingTimeoutRef.current = undefined } }
  }, [aggregatedDetections.camerasProcessing, processingDisplay])

  // ---- Load ML models after session starts ----
  useEffect(() => {
    if (!sessionInfo?.session_id || sessionInfo.status === 'initializing' || modelsInitializedRef.current) return
    let cancelled = false
    const init = async () => {
      try {
        setModelsLoading(true)
        await loadModels()
        if (!cancelled) modelsInitializedRef.current = true
      } catch (error) {
        logError('Error cargando modelos', error)
      } finally {
        if (!cancelled) setModelsLoading(false)
      }
    }
    init()
    return () => { cancelled = true }
  }, [sessionInfo?.session_id, sessionInfo?.status])

  // ---- Save events ----
  const lastSavedEventRef = useRef<Record<string, string>>({})
  const saveEventTimeoutRef = useRef<Record<string, number | undefined>>({})

  useEffect(() => {
    activeCameraIds.forEach((cameraId) => {
      const detection = cameraDetections[cameraId]
      if (!detection) return
      const existingTimeout = saveEventTimeoutRef.current[cameraId]
      if (existingTimeout !== undefined) { window.clearTimeout(existingTimeout); saveEventTimeoutRef.current[cameraId] = undefined }
      const hasSignificantDetection = detection.detections.persons > 0 || detection.detections.faces > 0 || detection.detections.objects.length > 0
      if (!hasSignificantDetection) return
      const currentStateHash = JSON.stringify({ persons: detection.detections.persons, faces: detection.detections.faces, objects: detection.detections.objects.length })
      if (currentStateHash === lastSavedEventRef.current[cameraId]) return
      saveEventTimeoutRef.current[cameraId] = window.setTimeout(async () => {
        const eventType = detection.detections.objects.length > 0 ? 'object_detected' : detection.detections.faces > 0 ? 'face_detected' : 'person_detected'
        const event = await insertEvent(eventType, {
          eventType, confidence: 0.8, timestamp: new Date().toISOString(),
          persons: detection.detections.persons, faces: detection.detections.faces,
          emotions: detection.detections.emotions, activity: detection.detections.activity,
          healthStatus: detection.detections.healthStatus, objects: detection.detections.objects,
          label: cameraConfigs[cameraId]?.label, location: cameraConfigs[cameraId]?.location,
        }, cameraId, sessionInfo?.session_id ?? null)
        if (event) { addEvent(event); lastSavedEventRef.current[cameraId] = currentStateHash }
      }, 10000)
    })
    return () => {
      Object.values(saveEventTimeoutRef.current).forEach((timeout) => { if (timeout !== undefined) window.clearTimeout(timeout) })
      saveEventTimeoutRef.current = {}
    }
  }, [cameraDetections, activeCameraIds, cameraConfigs, addEvent, sessionInfo?.session_id])

  // =====================================================
  // RENDER
  // =====================================================
  return (
    <div className="page-shell page-shell--fluid py-4">
      {/* Compact toolbar */}
      {sessionInfo && (
        <div className="live-toolbar">
          <div className="live-toolbar__left">
            <span className="text-moss text-sm">
              {sessionInfo.name || sessionInfo.email || 'Sin identificar'}
            </span>
          </div>
          <div className="live-toolbar__center">
            <span className="live-pill">
              <Video size={14} />
              {activeCameraIds.length} camara{activeCameraIds.length !== 1 ? 's' : ''} activa{activeCameraIds.length !== 1 ? 's' : ''}
            </span>
            <span className="live-pill">
              <FpsStatusDot fps={fps} />
              Rendimiento
            </span>
            {modelsLoading ? (
              <span className="live-pill">
                <span className="inline-block h-3 w-3 animate-spin rounded-full border-2 border-current border-t-transparent" />
                Cargando modelos...
              </span>
            ) : (
              <span className="live-pill">Modelos IA activos</span>
            )}
          </div>
          <div className="live-toolbar__right">
            <button
              type="button"
              className="live-toggle-panel-btn"
              onClick={() => setRightPanelVisible((v) => !v)}
              title={rightPanelVisible ? 'Ocultar panel' : 'Mostrar panel'}
            >
              {rightPanelVisible ? <PanelRightClose size={18} /> : <PanelRightOpen size={18} />}
            </button>
            <button
              type="button"
              className="btn btn-secondary btn-sm"
              onClick={handleEndSession}
              disabled={endingSession}
            >
              {endingSession ? 'Finalizando...' : 'Finalizar demo'}
            </button>
          </div>
        </div>
      )}

      {/* ===== CAMERA MANAGEMENT PANEL ===== */}
      {sessionInfo && (
        <div className="card mb-4">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-forest font-semibold text-base flex items-center gap-2 mb-0">
              <Camera size={18} />
              Gestion de Camaras
              <span className="badge badge-active text-xs">{activeCameraCount}/{MAX_ACTIVE_CAMERAS}</span>
            </h3>
          </div>

          {limitWarning && (
            <div className="alert alert-info mb-3">
              Limite maximo de {MAX_ACTIVE_CAMERAS} camaras activas alcanzado. Desactiva una para agregar otra.
            </div>
          )}
          {deviceError && <div className="alert alert-warning mb-3">{deviceError}</div>}

          {/* --- Local Cameras --- */}
          <div className="mb-4">
            <div className="flex items-center justify-between mb-2">
              <h4 className="text-forest font-semibold text-sm flex items-center gap-2 mb-0">
                <Camera size={16} />
                Camaras Locales
              </h4>
              <button
                type="button"
                className="btn btn-secondary btn-sm flex items-center gap-1.5"
                onClick={() => refreshDevices(true)}
                disabled={loadingDevices}
              >
                <RefreshCw size={12} className={loadingDevices ? 'animate-spin' : ''} />
                {loadingDevices ? 'Detectando...' : 'Detectar'}
              </button>
            </div>

            {deviceEntries.length === 0 ? (
              <p className="text-moss text-sm">No hay camaras locales. Conecta una webcam o autoriza el acceso.</p>
            ) : (
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-3">
                {deviceEntries.map((device) => {
                  const cameraConfig = findCameraByDeviceId(device.deviceId)
                  const isActive = cameraConfig ? activeCameraIds.includes(cameraConfig.id) : false
                  const isExpanded = expandedCamera === (cameraConfig?.id ?? device.deviceId)

                  return (
                    <div key={device.deviceId || device.label} className="border border-gray-200 rounded-lg p-3">
                      <div className="flex justify-between items-center gap-3">
                        <div className="min-w-0 flex-1">
                          <div className="flex items-center gap-2">
                            {isActive ? <Wifi size={12} className="text-emerald-500" /> : <WifiOff size={12} className="text-gray-400" />}
                            <span className="text-forest font-medium text-sm truncate">
                              {cameraConfig?.label ?? device.label}
                            </span>
                          </div>
                        </div>
                        <div className="flex items-center gap-2 flex-shrink-0">
                          {cameraConfig && (
                            <button type="button" className="text-moss hover:text-forest" onClick={() => setExpandedCamera(isExpanded ? null : (cameraConfig?.id ?? device.deviceId))}>
                              <Settings2 size={14} />
                            </button>
                          )}
                          <Toggle
                            enabled={isActive}
                            onChange={(value) => handleToggle(device.deviceId, value)}
                            disabled={!isActive && isLimitReached}
                          />
                        </div>
                      </div>

                      {cameraConfig && isExpanded && (
                        <div className="mt-3 pt-3 border-t border-gray-200">
                          <div className="grid grid-cols-2 gap-2 mb-3">
                            <div>
                              <label className="label text-xs flex items-center gap-1"><Tag size={10} />Nombre</label>
                              <input type="text" className="input input-compact text-sm" value={cameraConfig.label} onChange={(e) => handleLabelChange(cameraConfig.id, e.target.value)} placeholder="Ej. Entrada" />
                            </div>
                            <div>
                              <label className="label text-xs flex items-center gap-1"><MapPin size={10} />Ubicacion</label>
                              <input type="text" className="input input-compact text-sm" value={cameraConfig.location ?? ''} onChange={(e) => handleLocationChange(cameraConfig.id, e.target.value)} placeholder="Ej. Recepcion" />
                            </div>
                            <div>
                              <label className="label text-xs flex items-center gap-1"><Monitor size={10} />Resolucion</label>
                              <select className="select text-sm" value={cameraConfig.resolution} onChange={(e) => handleResolutionChange(cameraConfig.id, e.target.value as CameraConfig['resolution'])}>
                                <option value="low">SD 640x480</option>
                                <option value="medium">HD 1280x720</option>
                                <option value="high">Full HD 1920x1080</option>
                              </select>
                            </div>
                            <div>
                              <label className="label text-xs flex items-center gap-1"><Gauge size={10} />FPS</label>
                              <input type="number" min={10} max={60} step={5} className="input input-compact text-sm" value={cameraConfig.targetFPS} onChange={(e) => handleFpsChange(cameraConfig.id, Number(e.target.value))} />
                            </div>
                          </div>
                          <div>
                            <label className="label text-xs mb-1">Modelos de deteccion</label>
                            <div className="flex flex-wrap gap-2">
                              {(Object.keys(MODEL_LABELS) as (keyof CameraConfig['models'])[]).map((model) => (
                                <label key={model} className="flex items-center gap-1.5 text-xs text-moss cursor-pointer">
                                  <input type="checkbox" className="accent-forest" checked={cameraConfig.models[model]} onChange={(e) => handleModelToggle(cameraConfig.id, model, e.target.checked)} />
                                  {MODEL_LABELS[model]}
                                </label>
                              ))}
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                  )
                })}
              </div>
            )}
          </div>

          {/* --- External Cameras --- */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <h4 className="text-forest font-semibold text-sm flex items-center gap-2 mb-0">
                <Wifi size={16} />
                Camaras Externas (IP/RTSP)
              </h4>
              <button
                type="button"
                className="btn btn-primary btn-sm flex items-center gap-1.5"
                onClick={() => setShowExternalForm((v) => !v)}
              >
                <Plus size={12} />
                {showExternalForm ? 'Cerrar' : 'Anadir'}
              </button>
            </div>

            {externalError && <div className="alert alert-warning mb-2 text-sm">{externalError}</div>}

            {showExternalForm && (
              <div className="mb-3">
                <ExternalCameraForm onSubmit={handleCreateExternal} onCancel={() => setShowExternalForm(false)} loading={externalFormLoading} />
              </div>
            )}

            {loadingExternal ? (
              <p className="text-moss text-sm">Cargando camaras externas...</p>
            ) : externalCameras.length === 0 ? (
              <p className="text-moss text-sm">No hay camaras externas. Anade una URL RTSP o HTTP.</p>
            ) : (
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-3">
                {externalCameras.map((camera) => {
                  const extConfig = getExternalConfig(camera.id)
                  const isActive = extConfig?.enabled ?? false
                  const actionLoading = externalActionLoading === camera.id
                  const configId = `external-${camera.id}`
                  const isExpanded = expandedCamera === configId

                  return (
                    <div key={camera.id} className="border border-gray-200 rounded-lg p-3">
                      <div className="flex justify-between items-center gap-3">
                        <div className="min-w-0 flex-1">
                          <div className="flex items-center gap-2">
                            {isActive ? <Wifi size={12} className="text-emerald-500" /> : <WifiOff size={12} className="text-gray-400" />}
                            <span className="text-forest font-medium text-sm truncate">{camera.name}</span>
                            <span className="tag text-xs capitalize">{camera.status}</span>
                          </div>
                          <p className="text-moss text-xs truncate mt-0.5" style={{ maxWidth: '280px' }}>{camera.source_url}</p>
                        </div>
                        <div className="flex items-center gap-2 flex-shrink-0">
                          {extConfig && (
                            <button type="button" className="text-moss hover:text-forest" onClick={() => setExpandedCamera(isExpanded ? null : configId)}>
                              <Settings2 size={14} />
                            </button>
                          )}
                          <Toggle
                            enabled={isActive}
                            onChange={(value) => handleExternalToggle(camera, value)}
                            disabled={(!isActive && isLimitReached) || actionLoading}
                          />
                        </div>
                      </div>

                      {extConfig && isExpanded && (
                        <div className="mt-3 pt-3 border-t border-gray-200">
                          <div className="grid grid-cols-2 gap-2 mb-3">
                            <div>
                              <label className="label text-xs flex items-center gap-1"><Monitor size={10} />Resolucion</label>
                              <select className="select text-sm" value={extConfig.resolution} onChange={(e) => handleResolutionChange(configId, e.target.value as CameraConfig['resolution'])}>
                                <option value="low">SD 640x480</option>
                                <option value="medium">HD 1280x720</option>
                                <option value="high">Full HD 1920x1080</option>
                              </select>
                            </div>
                            <div>
                              <label className="label text-xs flex items-center gap-1"><Gauge size={10} />FPS</label>
                              <input type="number" min={10} max={60} step={5} className="input input-compact text-sm" value={extConfig.targetFPS} onChange={(e) => handleFpsChange(configId, Number(e.target.value))} />
                            </div>
                          </div>
                          <div className="mb-3">
                            <label className="label text-xs mb-1">Modelos de deteccion</label>
                            <div className="flex flex-wrap gap-2">
                              {(Object.keys(MODEL_LABELS) as (keyof CameraConfig['models'])[]).map((model) => (
                                <label key={model} className="flex items-center gap-1.5 text-xs text-moss cursor-pointer">
                                  <input type="checkbox" className="accent-forest" checked={extConfig.models[model]} onChange={(e) => handleModelToggle(configId, model, e.target.checked)} />
                                  {MODEL_LABELS[model]}
                                </label>
                              ))}
                            </div>
                          </div>
                          <button type="button" className="btn btn-danger btn-sm flex items-center gap-1.5" onClick={() => handleExternalRemove(camera)} disabled={actionLoading}>
                            <Trash2 size={12} />
                            Eliminar
                          </button>
                        </div>
                      )}
                    </div>
                  )
                })}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Indicador de carga */}
      {modelsLoading && (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="card flex items-center gap-3 mb-4" role="alert">
          <div className="h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" role="status">
            <span className="sr-only">Cargando...</span>
          </div>
          <span className="text-moss">Inicializando modelos de IA...</span>
        </motion.div>
      )}

      {/* Layout principal: 2 columnas */}
      <div className={`live-grid ${rightPanelVisible ? '' : 'live-grid--full'}`}>
        <motion.main
          initial={{ opacity: 0, y: 18 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.1 }}
          className="live-main"
        >
          {/* Camera feeds */}
          <div className="live-camera-board">
            <div className="live-camera-grid">
              {activeCameraIds.length === 0 ? (
                <div className="live-empty-card text-center">
                  {!sessionInfo ? (
                    <p className="text-moss">Inicia una sesion para activar la camara automaticamente.</p>
                  ) : cameraError ? (
                    <div>
                      <p className="text-red-500 mb-3">{cameraError}</p>
                      <button type="button" className="btn btn-primary flex items-center gap-2 mx-auto" onClick={handleRetryCamera}>
                        <RefreshCw size={14} />
                        Reintentar
                      </button>
                      {availableDevices.length > 1 && (
                        <div className="mt-4">
                          <p className="text-moss text-sm mb-2">O selecciona una camara:</p>
                          <div className="flex flex-col gap-2">
                            {availableDevices.map((device) => (
                              <button key={device.deviceId} type="button" className="btn btn-secondary btn-sm text-left"
                                onClick={() => { const id = activateCamera(device.deviceId); if (id) cameraAutoActivatedRef.current = true }}>
                                {device.label || 'Camara sin identificar'}
                              </button>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  ) : (
                    <div className="flex items-center justify-center gap-3 py-8">
                      <div className="h-5 w-5 animate-spin rounded-full border-2 border-forest border-t-transparent" />
                      <span className="text-moss">Conectando camara...</span>
                    </div>
                  )}
                </div>
              ) : (
                activeCameraIds.map((cameraId) => <CameraFeed key={cameraId} cameraId={cameraId} />)
              )}
            </div>
          </div>

          {detectionState.detections.objects.length > 0 && (
            <motion.div initial={{ opacity: 0, y: 18 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6, delay: 0.35 }} className="card live-objects-card">
              <div className="flex items-center justify-between mb-3">
                <h5 className="text-forest mb-0 flex items-center gap-2">Objetos Detectados</h5>
                <span className="badge badge-info">{detectionState.detections.objects.length}</span>
              </div>
              <div className="neo-object-tags">
                {detectionState.detections.objects.map((obj, idx) => (
                  <motion.span key={`${obj.label}-${idx}`} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: idx * 0.05 }} className="neo-object-tag">
                    {obj.label}
                    <small className="text-moss">{Math.round(obj.confidence * 100)}%</small>
                  </motion.span>
                ))}
              </div>
            </motion.div>
          )}
        </motion.main>

        {rightPanelVisible && (
          <motion.aside initial={{ opacity: 0, x: 22 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: 22 }} transition={{ duration: 0.55, delay: 0.15 }} className="live-sidebar live-sidebar--right">
            <DetectionPanel />
          </motion.aside>
        )}
      </div>
      <SessionStartModal show={sessionModalOpen} onSubmit={handleSessionSubmit} isSubmitting={sessionSubmitting} error={sessionError} />
    </div>
  )
}
