import { create } from 'zustand'
import {
  AggregatedDetections,
  AppConfig,
  CameraConfig,
  CameraDetectionSnapshot,
  CameraDetectionState,
  CameraModelSettings,
  CameraRuntimeState,
  DetectionState,
  Event,
  CameraQualityPreset,
  PerformancePreset,
  ExternalCamera,
  DemoSessionRecord,
} from '../types'
import { logWarn } from '../utils/logger'
import { adminLoginRequest } from '../lib/sessions'

type AvailableCameraDevice = {
  deviceId: string
  label: string
  groupId?: string
}

export const MAX_ACTIVE_CAMERAS = 3

export const SESSION_STORAGE_KEY = 'vhi-session-info'
export const THEME_STORAGE_KEY = 'vhi-theme'

export type ThemeMode = 'light' | 'dark' | 'system'

const DEFAULT_CAMERA_MODELS: CameraModelSettings = {
  personDetection: true,
  faceDetection: true,
  emotionDetection: true,
  movementDetection: true,
  objectDetection: true,
}

type PerformancePresetDefinition = {
  resolution: CameraQualityPreset
  targetFPS: number
  models: CameraModelSettings
}

const PERFORMANCE_PRESETS: Record<PerformancePreset, PerformancePresetDefinition> = {
  performance: {
    resolution: 'low',
    targetFPS: 20,
    models: {
      personDetection: true,
      faceDetection: true,
      emotionDetection: false,
      movementDetection: true,
      objectDetection: false,
    },
  },
  balanced: {
    resolution: 'medium',
    targetFPS: 24,
    models: {
      personDetection: true,
      faceDetection: true,
      emotionDetection: true,
      movementDetection: true,
      objectDetection: true,
    },
  },
  quality: {
    resolution: 'high',
    targetFPS: 30,
    models: {
      personDetection: true,
      faceDetection: true,
      emotionDetection: true,
      movementDetection: true,
      objectDetection: true,
    },
  },
}

const PERFORMANCE_PRESET_ORDER: PerformancePreset[] = ['performance', 'balanced', 'quality']

const initialConfig: AppConfig = {
  personDetection: { enabled: true, threshold: 0.5, fps: 7 },
  faceDetection: { enabled: true, threshold: 0.6, fps: 10 },
  emotionDetection: { enabled: true, threshold: 0.6, fps: 5 },
  poseDetection: { enabled: false, threshold: 0.6, fps: 5 },
  handDetection: { enabled: false, threshold: 0.6, fps: 5 },
  movementDetection: { enabled: true, threshold: 0.45, fps: 10 },
  objectDetection: { enabled: true, threshold: 0.45, fps: 7 },
  anonymizeData: false,
  saveImages: false,
  cameraResolution: 'medium',
}

const createEmptySnapshot = (): CameraDetectionSnapshot => ({
  persons: 0,
  faces: 0,
  emotions: [],
  activity: null,
  healthStatus: null,
  objects: [],
})

const createEmptyCameraDetection = (cameraId: string): CameraDetectionState => ({
  cameraId,
  isProcessing: false,
  currentFPS: 0,
  detections: createEmptySnapshot(),
  lastEvent: null,
  lastUpdated: null,
})

const createLegacyDetection = (): DetectionState => ({
  isProcessing: false,
  currentFPS: 0,
  detections: {
    persons: 0,
    faces: 0,
    emotions: [],
    activity: null,
    healthStatus: null,
    objects: [],
  },
  lastEvent: null,
})

const generateCameraId = () => {
  if (typeof globalThis !== 'undefined' && globalThis.crypto?.randomUUID) {
    return globalThis.crypto.randomUUID()
  }
  return `camera-${Math.random().toString(36).slice(2, 10)}`
}

const applyPresetToCamera = (
  camera: CameraConfig,
  preset: PerformancePreset,
  definition: PerformancePresetDefinition
): CameraConfig => ({
  ...camera,
  resolution: definition.resolution,
  targetFPS: definition.targetFPS,
  models: { ...definition.models },
  appliedPreset: preset,
})

const getPresetIndex = (preset: PerformancePreset) => PERFORMANCE_PRESET_ORDER.indexOf(preset)

const createCameraConfig = (partial: Partial<CameraConfig>): CameraConfig => ({
  id: partial.id ?? generateCameraId(),
  sourceType: partial.sourceType ?? 'browser',
  deviceId: partial.deviceId,
  streamUrl: partial.streamUrl,
  label: partial.label ?? 'Cámara sin nombre',
  location: partial.location,
  enabled: partial.enabled ?? false,
  resolution: partial.resolution ?? 'medium',
  targetFPS: partial.targetFPS ?? 30,
  models: partial.models ? { ...partial.models } : { ...DEFAULT_CAMERA_MODELS },
  appliedPreset: partial.appliedPreset,
  hlsUrl: partial.hlsUrl,
  externalId: partial.externalId,
})

const computeAggregatedDetections = (
  activeCameraIds: string[],
  cameraDetections: Record<string, CameraDetectionState>
): AggregatedDetections => {
  let totalPersons = 0
  let totalFaces = 0
  let totalObjects = 0
  let camerasProcessing = 0
  let totalFPS = 0
  const activeDetections: Record<string, CameraDetectionState> = {}

  activeCameraIds.forEach((cameraId) => {
    const detection = cameraDetections[cameraId]
    if (!detection) return

    activeDetections[cameraId] = detection
    totalPersons += detection.detections.persons
    totalFaces += detection.detections.faces
    totalObjects += detection.detections.objects.length
    totalFPS += detection.currentFPS
    if (detection.isProcessing) {
      camerasProcessing += 1
    }
  })

  const camerasActive = activeCameraIds.length
  const averageFPS = camerasActive > 0 ? totalFPS / camerasActive : 0

  return {
    totalPersons,
    totalFaces,
    totalObjects,
    camerasActive,
    camerasProcessing,
    byCamera: activeDetections,
    averageFPS,
  }
}

const computeLegacyDetectionState = (
  activeCameraIds: string[],
  cameraDetections: Record<string, CameraDetectionState>
): DetectionState => {
  if (activeCameraIds.length === 0) {
    return createLegacyDetection()
  }

  if (activeCameraIds.length === 1) {
    const detection = cameraDetections[activeCameraIds[0]] ?? createEmptyCameraDetection(activeCameraIds[0])
    return {
      isProcessing: detection.isProcessing,
      currentFPS: detection.currentFPS,
      detections: {
        persons: detection.detections.persons,
        faces: detection.detections.faces,
        emotions: detection.detections.emotions,
        activity: detection.detections.activity,
        healthStatus: detection.detections.healthStatus,
        objects: detection.detections.objects,
      },
      lastEvent: detection.lastEvent,
    }
  }

  // Agregado simple cuando hay múltiples cámaras
  let persons = 0
  let faces = 0
  const emotions = new Set<string>()
  const objects: DetectionState['detections']['objects'] = []
  let currentFPS = 0
  let processingCount = 0

  activeCameraIds.forEach((cameraId) => {
    const detection = cameraDetections[cameraId]
    if (!detection) return

    persons += detection.detections.persons
    faces += detection.detections.faces
    detection.detections.emotions.forEach((emotion) => emotions.add(emotion))
    objects.push(...detection.detections.objects.slice(0, 4))
    currentFPS += detection.currentFPS
    if (detection.isProcessing) {
      processingCount += 1
    }
  })

  return {
    isProcessing: processingCount > 0,
    currentFPS: activeCameraIds.length > 0 ? Math.round(currentFPS / activeCameraIds.length) : 0,
    detections: {
      persons,
      faces,
      emotions: Array.from(emotions) as DetectionState['detections']['emotions'],
      activity: null,
      healthStatus: null,
      objects: objects.slice(0, 6),
    },
    lastEvent: null,
  }
}

const createExternalCameraConfig = (camera: ExternalCamera, preset: PerformancePreset): CameraConfig => {
  const definition = PERFORMANCE_PRESETS[preset]
  return {
    id: `external-${camera.id}`,
    sourceType: 'external',
    label: camera.name,
    enabled: camera.status === 'running' || camera.status === 'starting',
    resolution: definition.resolution,
    targetFPS: definition.targetFPS,
    models: { ...definition.models },
    appliedPreset: preset,
    hlsUrl: camera.hls_url ?? undefined,
    externalId: camera.id,
  }
}

const syncExternalCameraState = (
  state: {
    cameraConfigs: Record<string, CameraConfig>
    cameraDetections: Record<string, CameraDetectionState>
    activeCameraIds: string[]
    performancePreset: PerformancePreset
  },
  cameras: ExternalCamera[],
) => {
  const cameraConfigs = { ...state.cameraConfigs }
  const cameraDetections = { ...state.cameraDetections }
  let activeCameraIds = state.activeCameraIds.filter((id) => {
    const cfg = cameraConfigs[id]
    return !(cfg && cfg.sourceType === 'external')
  })

  const seen = new Set<string>()

  cameras.forEach((camera) => {
    const configId = `external-${camera.id}`
    seen.add(configId)
    const config = createExternalCameraConfig(camera, state.performancePreset)
    cameraConfigs[configId] = config

    if (!cameraDetections[configId]) {
      cameraDetections[configId] = createEmptyCameraDetection(configId)
    }

    if (config.enabled) {
      if (!activeCameraIds.includes(configId)) {
        activeCameraIds = [...activeCameraIds, configId]
      }
    } else {
      activeCameraIds = activeCameraIds.filter((id) => id !== configId)
    }
  })

  Object.keys(cameraConfigs).forEach((configId) => {
    const cfg = cameraConfigs[configId]
    if (cfg.sourceType === 'external' && !seen.has(configId)) {
      delete cameraConfigs[configId]
      delete cameraDetections[configId]
      activeCameraIds = activeCameraIds.filter((id) => id !== configId)
    }
  })

  return { cameraConfigs, cameraDetections, activeCameraIds }
}

const getStoredTheme = (): ThemeMode => {
  if (typeof window === 'undefined') return 'dark'
  try {
    const stored = window.localStorage.getItem(THEME_STORAGE_KEY)
    if (stored === 'light' || stored === 'dark' || stored === 'system') return stored
  } catch {
    // ignore
  }
  return 'dark' // Default to dark for surveillance use case
}

const persistTheme = (theme: ThemeMode) => {
  if (typeof window === 'undefined') return
  try {
    window.localStorage.setItem(THEME_STORAGE_KEY, theme)
  } catch {
    // ignore
  }
}

export const applyThemeToDOM = (theme: ThemeMode) => {
  if (typeof window === 'undefined') return
  const root = document.documentElement
  let isDark: boolean

  if (theme === 'system') {
    isDark = window.matchMedia('(prefers-color-scheme: dark)').matches
  } else {
    isDark = theme === 'dark'
  }

  if (isDark) {
    root.classList.add('dark')
  } else {
    root.classList.remove('dark')
  }
}

const persistSessionInfo = (session: DemoSessionRecord | null) => {
  if (typeof window === 'undefined') return
  try {
    if (session) {
      window.localStorage.setItem(SESSION_STORAGE_KEY, JSON.stringify(session))
    } else {
      window.localStorage.removeItem(SESSION_STORAGE_KEY)
    }
  } catch (error) {
    logWarn('No se pudo persistir la sesión local', error)
  }
}

interface AppStore {
  theme: ThemeMode
  setTheme: (theme: ThemeMode) => void

  privacyAccepted: boolean
  setPrivacyAccepted: (accepted: boolean) => void

  config: AppConfig
  updateConfig: (config: Partial<AppConfig>) => void

  performancePreset: PerformancePreset
  autoPerformanceManagement: boolean
  lastPerformanceAdjustment: number
  setPerformancePreset: (preset: PerformancePreset) => void
  toggleAutoPerformanceManagement: (enabled: boolean) => void

  sessionInfo: DemoSessionRecord | null
  setSessionInfo: (session: DemoSessionRecord | null) => void
  updateSessionInfo: (session: Partial<DemoSessionRecord>) => void
  clearSessionInfo: () => void

  adminAuth: {
    isAuthenticated: boolean
    username: string | null
    token: string | null
  }
  adminLogin: (username: string, password: string) => Promise<boolean>
  adminLogout: () => void

  externalCameras: ExternalCamera[]
  setExternalCameras: (cameras: ExternalCamera[]) => void
  upsertExternalCamera: (camera: ExternalCamera) => void
  removeExternalCamera: (cameraId: string) => void

  availableDevices: AvailableCameraDevice[]
  setAvailableDevices: (devices: AvailableCameraDevice[]) => void

  cameraConfigs: Record<string, CameraConfig>
  activeCameraIds: string[]
  activateCamera: (deviceId: string) => string | null
  deactivateCamera: (cameraId: string) => void
  updateCameraConfig: (cameraId: string, config: Partial<CameraConfig>) => void

  cameraRuntime: Record<string, CameraRuntimeState>
  updateCameraRuntime: (cameraId: string, runtime: Partial<CameraRuntimeState>) => void

  cameraDetections: Record<string, CameraDetectionState>
  updateCameraDetection: (cameraId: string, detection: Partial<CameraDetectionState>) => void
  resetCameraDetection: (cameraId: string) => void

  aggregatedDetections: AggregatedDetections

  detectionState: DetectionState // Legacy (usado por componentes existentes)

  events: Event[]
  addEvent: (event: Event) => void
  clearEvents: () => void
}

export const useAppStore = create<AppStore>((set, get) => ({
  theme: getStoredTheme(),
  setTheme: (theme) => {
    persistTheme(theme)
    applyThemeToDOM(theme)
    set({ theme })
  },

  privacyAccepted: false,
  config: initialConfig,

  performancePreset: 'balanced',
  autoPerformanceManagement: false,
  lastPerformanceAdjustment: 0,

  sessionInfo: null,

  adminAuth: {
    isAuthenticated: false,
    username: null,
    token: null,
  },

  externalCameras: [],

  availableDevices: [],
  cameraConfigs: {},
  activeCameraIds: [],
  cameraRuntime: {},
  cameraDetections: {},
  aggregatedDetections: computeAggregatedDetections([], {}),

  detectionState: createLegacyDetection(),

  events: [],

  setPrivacyAccepted: (accepted) => set({ privacyAccepted: accepted }),

  updateConfig: (newConfig) => 
    set((state) => ({ 
      config: { ...state.config, ...newConfig },
    })),

  setPerformancePreset: (preset) =>
    set((state) => {
      if (state.performancePreset === preset) {
        return state
      }

      const definition = PERFORMANCE_PRESETS[preset]
      const cameraConfigs = { ...state.cameraConfigs }
      state.activeCameraIds.forEach((cameraId) => {
        const existing = cameraConfigs[cameraId]
        if (!existing) return
        cameraConfigs[cameraId] = applyPresetToCamera(existing, preset, definition)
      })

      return {
        cameraConfigs,
        performancePreset: preset,
        lastPerformanceAdjustment: Date.now(),
      }
    }),

  setSessionInfo: (session) => {
    persistSessionInfo(session)
    set({ sessionInfo: session })
  },

  updateSessionInfo: (session) =>
    set((state) => {
      if (!state.sessionInfo) {
        return state
      }
      const updated = { ...state.sessionInfo, ...session }
      persistSessionInfo(updated)
      return { sessionInfo: updated }
    }),

  clearSessionInfo: () => {
    persistSessionInfo(null)
    set({ sessionInfo: null })
  },

  toggleAutoPerformanceManagement: (enabled) =>
    set(() => ({
      autoPerformanceManagement: enabled,
      lastPerformanceAdjustment: enabled ? Date.now() : 0,
    })),

  adminLogin: async (username, password) => {
    try {
      const response = await adminLoginRequest({ username, password })
      set({
        adminAuth: {
          isAuthenticated: true,
          username: response.username,
          token: response.token || null,
        },
      })
      return true
    } catch (error) {
      logWarn('Autenticación administrativa fallida', error)
      set({
        adminAuth: {
          isAuthenticated: false,
          username: null,
          token: null,
        },
      })
      return false
    }
  },

  adminLogout: () =>
    set({
      adminAuth: {
        isAuthenticated: false,
        username: null,
        token: null,
      },
    }),

  setExternalCameras: (cameras) =>
    set((state) => {
      const { cameraConfigs, cameraDetections, activeCameraIds } = syncExternalCameraState(state, cameras)
      const aggregatedDetections = computeAggregatedDetections(activeCameraIds, cameraDetections)
      const detectionState = computeLegacyDetectionState(activeCameraIds, cameraDetections)
      return {
        externalCameras: cameras,
        cameraConfigs,
        cameraDetections,
        activeCameraIds,
        aggregatedDetections,
        detectionState,
      }
    }),

  upsertExternalCamera: (camera) =>
    set((state) => {
      const cameras = state.externalCameras.filter((item) => item.id !== camera.id)
      cameras.push(camera)
      const { cameraConfigs, cameraDetections, activeCameraIds } = syncExternalCameraState(state, cameras)
      const aggregatedDetections = computeAggregatedDetections(activeCameraIds, cameraDetections)
      const detectionState = computeLegacyDetectionState(activeCameraIds, cameraDetections)
      return {
        externalCameras: cameras,
        cameraConfigs,
        cameraDetections,
        activeCameraIds,
        aggregatedDetections,
        detectionState,
      }
    }),

  removeExternalCamera: (cameraId) =>
    set((state) => {
      const cameras = state.externalCameras.filter((item) => item.id !== cameraId)
      const { cameraConfigs, cameraDetections, activeCameraIds } = syncExternalCameraState(state, cameras)
      const aggregatedDetections = computeAggregatedDetections(activeCameraIds, cameraDetections)
      const detectionState = computeLegacyDetectionState(activeCameraIds, cameraDetections)
      return {
        externalCameras: cameras,
        cameraConfigs,
        cameraDetections,
        activeCameraIds,
        aggregatedDetections,
        detectionState,
      }
    }),

  setAvailableDevices: (devices) =>
    set(() => ({
      availableDevices: devices,
    })),

  activateCamera: (deviceId) => {
    const state = get()
    if (state.activeCameraIds.length >= MAX_ACTIVE_CAMERAS) {
      return null
    }

    const existingCameraId = Object.values(state.cameraConfigs).find(
      (camera) => camera.deviceId === deviceId
    )?.id

    const cameraId = existingCameraId ?? generateCameraId()
    const deviceLabel =
      state.availableDevices.find((device) => device.deviceId === deviceId)?.label ?? `Cámara ${state.activeCameraIds.length + 1}`

    set((current) => {
      const presetDefinition = PERFORMANCE_PRESETS[current.performancePreset]
      const cameraConfig = existingCameraId
        ? {
            ...current.cameraConfigs[cameraId],
            enabled: true,
          }
        : applyPresetToCamera(
            createCameraConfig({
              id: cameraId,
              sourceType: 'browser',
              deviceId,
              label: deviceLabel,
              enabled: true,
            }),
            current.performancePreset,
            presetDefinition
          )

      const cameraConfigs = {
        ...current.cameraConfigs,
        [cameraId]: cameraConfig,
      }

      const activeCameraIds = current.activeCameraIds.includes(cameraId)
        ? current.activeCameraIds
        : [...current.activeCameraIds, cameraId]

      const cameraDetections = {
        ...current.cameraDetections,
        [cameraId]: current.cameraDetections[cameraId] ?? createEmptyCameraDetection(cameraId),
      }

      const aggregatedDetections = computeAggregatedDetections(activeCameraIds, cameraDetections)
      const detectionState = computeLegacyDetectionState(activeCameraIds, cameraDetections)

      return {
        cameraConfigs,
        activeCameraIds,
        cameraDetections,
        aggregatedDetections,
        detectionState,
      }
    })

    return cameraId
  },

  deactivateCamera: (cameraId) =>
    set((state) => {
      if (!state.cameraConfigs[cameraId]) {
        return state
      }

      const cameraConfigs = {
        ...state.cameraConfigs,
        [cameraId]: {
          ...state.cameraConfigs[cameraId],
          enabled: false,
        },
      }

      const activeCameraIds = state.activeCameraIds.filter((id) => id !== cameraId)
      const cameraDetections = {
        ...state.cameraDetections,
        [cameraId]: createEmptyCameraDetection(cameraId),
      }

      const aggregatedDetections = computeAggregatedDetections(activeCameraIds, cameraDetections)
      const detectionState = computeLegacyDetectionState(activeCameraIds, cameraDetections)

      return {
        cameraConfigs,
        activeCameraIds,
        cameraDetections,
        aggregatedDetections,
        detectionState,
      }
    }),

  updateCameraConfig: (cameraId, config) =>
    set((state) => {
      if (!state.cameraConfigs[cameraId]) {
        return state
      }

      const manualOverride =
        config.resolution !== undefined ||
        config.targetFPS !== undefined ||
        config.models !== undefined

      const updatedConfig: CameraConfig = {
        ...state.cameraConfigs[cameraId],
        ...config,
        models: config.models
          ? { ...state.cameraConfigs[cameraId].models, ...config.models }
          : state.cameraConfigs[cameraId].models,
        appliedPreset: manualOverride ? undefined : state.cameraConfigs[cameraId].appliedPreset,
      }

      return {
        cameraConfigs: {
          ...state.cameraConfigs,
          [cameraId]: updatedConfig,
        },
      }
    }),

  updateCameraRuntime: (cameraId, runtime) =>
    set((state) => ({
      cameraRuntime: {
        ...state.cameraRuntime,
        [cameraId]: {
          cameraId,
          isStreaming: runtime.isStreaming ?? state.cameraRuntime[cameraId]?.isStreaming ?? false,
          isVideoReady: runtime.isVideoReady ?? state.cameraRuntime[cameraId]?.isVideoReady ?? false,
          lastError: runtime.lastError ?? state.cameraRuntime[cameraId]?.lastError ?? null,
        },
      },
    })),

  updateCameraDetection: (cameraId, detection) =>
    set((state) => {
      const previous = state.cameraDetections[cameraId] ?? createEmptyCameraDetection(cameraId)

      const mergedDetections =
        detection.detections !== undefined
          ? {
              ...previous.detections,
              ...detection.detections,
            }
          : previous.detections

      const updated: CameraDetectionState = {
        ...previous,
        ...detection,
        cameraId,
        detections: mergedDetections,
        lastUpdated: detection.lastUpdated ?? new Date().toISOString(),
      }

      const cameraDetections = {
        ...state.cameraDetections,
        [cameraId]: updated,
      }

      const aggregatedDetections = computeAggregatedDetections(state.activeCameraIds, cameraDetections)
      const detectionState = computeLegacyDetectionState(state.activeCameraIds, cameraDetections)

       let cameraConfigs = state.cameraConfigs
       let performancePreset = state.performancePreset
       let lastPerformanceAdjustment = state.lastPerformanceAdjustment

       if (
         state.autoPerformanceManagement &&
         aggregatedDetections.camerasActive > 0
       ) {
         const now = Date.now()
         const averageFPS = aggregatedDetections.averageFPS
         const currentIndex = getPresetIndex(performancePreset)
         let targetPreset = performancePreset

         if (
           averageFPS < 18 &&
           currentIndex > 0 &&
           now - state.lastPerformanceAdjustment > 6000
         ) {
           targetPreset = PERFORMANCE_PRESET_ORDER[currentIndex - 1]
         } else if (
           averageFPS > 36 &&
           currentIndex < PERFORMANCE_PRESET_ORDER.length - 1 &&
           now - state.lastPerformanceAdjustment > 12000
         ) {
           targetPreset = PERFORMANCE_PRESET_ORDER[currentIndex + 1]
         }

         if (targetPreset !== performancePreset) {
           const definition = PERFORMANCE_PRESETS[targetPreset]
           const updatedConfigs = { ...state.cameraConfigs }
           state.activeCameraIds.forEach((id) => {
             const existing = updatedConfigs[id]
             if (!existing) return
             updatedConfigs[id] = applyPresetToCamera(existing, targetPreset, definition)
           })
           cameraConfigs = updatedConfigs
           performancePreset = targetPreset
           lastPerformanceAdjustment = now
         }
       }

       const nextState: Partial<AppStore> = {
         cameraDetections,
         aggregatedDetections,
         detectionState,
       }

       if (cameraConfigs !== state.cameraConfigs) {
         nextState.cameraConfigs = cameraConfigs
       }

       if (performancePreset !== state.performancePreset) {
         nextState.performancePreset = performancePreset
       }

       if (lastPerformanceAdjustment !== state.lastPerformanceAdjustment) {
         nextState.lastPerformanceAdjustment = lastPerformanceAdjustment
       }

       return nextState
    }),

  resetCameraDetection: (cameraId) =>
    set((state) => {
      if (!(cameraId in state.cameraDetections)) {
        return state
      }

      const cameraDetections = {
        ...state.cameraDetections,
        [cameraId]: createEmptyCameraDetection(cameraId),
      }

      const aggregatedDetections = computeAggregatedDetections(state.activeCameraIds, cameraDetections)
      const detectionState = computeLegacyDetectionState(state.activeCameraIds, cameraDetections)

      return {
        cameraDetections,
        aggregatedDetections,
        detectionState,
      }
    }),

  addEvent: (event) => 
    set((state) => ({ 
      events: [event, ...state.events].slice(0, 100),
    })),

  clearEvents: () => set({ events: [] }),
}))

