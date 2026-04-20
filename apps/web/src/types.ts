/**
 * Tipos TypeScript compartidos para toda la aplicación
 */

// Tipo de evento detectado
export type EventType = 
  | 'person_detected'           // Persona detectada
  | 'face_detected'            // Rostro detectado
  | 'emotion_detected'         // Emoción detectada
  | 'movement_detected'        // Movimiento detectado
  | 'pose_detected'            // Postura detectada
  | 'hand_detected'            // Mano detectada
  | 'object_detected'          // Objeto detectado
  | 'health_alert'             // Alerta de salud
  | 'activity_change'          // Cambio de actividad

// Emociones detectables
export type EmotionType = 
  | 'happy'                    // Feliz
  | 'sad'                      // Triste
  | 'angry'                    // Enojado
  | 'surprised'                // Sorprendido
  | 'fearful'                  // Miedoso
  | 'disgusted'                // Disgustado
  | 'neutral'                  // Neutro
  | 'focused'                  // Concentrado

// Estados de actividad
export type ActivityType = 
  | 'active'                   // Activo
  | 'inactive'                 // Inactivo
  | 'sitting'                  // Sentado
  | 'standing'                 // De pie
  | 'falling'                  // Caída
  | 'walking'                  // Caminando
  | 'unknown'                  // Desconocido

// Estado de salud estimado
export type HealthStatus = 
  | 'alert'                    // Alerta
  | 'focused'                  // Concentrado
  | 'tired'                    // Cansado
  | 'stressed'                 // Estresado
  | 'normal'                   // Normal

// Payload de evento almacenado en Supabase
export interface EventPayload {
  eventType: EventType          // Tipo de evento
  confidence: number            // Confianza (0-1)
  timestamp: string             // Timestamp ISO
  cameraId?: string             // ID de la cámara que originó el evento
  emotion?: EmotionType         // Emoción (si aplica)
  activity?: ActivityType       // Actividad (si aplica)
  healthStatus?: HealthStatus   // Estado de salud (si aplica)
  boundingBox?: {               // Caja delimitadora
    x: number
    y: number
    width: number
    height: number
  }
  landmarks?: number[][]        // Landmarks faciales (si aplica)
  objects?: Array<{             // Objetos detectados
    label: string
    confidence: number
    bbox: { x: number; y: number; width: number; height: number }
  }>
}

// Evento completo en la base de datos
export interface Event {
  id: string                    // UUID
  user_id: string               // ID de usuario
  event_type: EventType         // Tipo de evento
  payload: EventPayload         // Payload JSON
  camera_id?: string            // Cámara que generó el evento
  created_at: string            // Timestamp de creación
}

// Configuración de modelos por cámara
export interface CameraModelSettings {
  personDetection: boolean
  faceDetection: boolean
  emotionDetection: boolean
  movementDetection: boolean
  objectDetection: boolean
}

export type CameraQualityPreset = 'low' | 'medium' | 'high'

export type CameraSourceType = 'browser' | 'external'

export type PerformancePreset = 'performance' | 'balanced' | 'quality'

export interface CameraConfig {
  id: string
  sourceType: CameraSourceType
  deviceId?: string
  streamUrl?: string
  label: string
  location?: string
  enabled: boolean
  resolution: CameraQualityPreset
  targetFPS: number
  models: CameraModelSettings
  appliedPreset?: PerformancePreset
  hlsUrl?: string
  externalId?: string
}

export interface CameraRuntimeState {
  cameraId: string
  isStreaming: boolean
  isVideoReady: boolean
  lastError: string | null
}

export interface CameraDetectionSnapshot {
  persons: number
  faces: number
  emotions: EmotionType[]
  activity: ActivityType | null
  healthStatus: HealthStatus | null
  objects: Array<{
    label: string
    confidence: number
    bbox?: { x: number; y: number; width: number; height: number }
  }>
}

export interface CameraDetectionState {
  cameraId: string
  isProcessing: boolean
  currentFPS: number
  detections: CameraDetectionSnapshot
  lastEvent: Event | null
  lastUpdated: string | null
}

export interface AggregatedDetections {
  totalPersons: number
  totalFaces: number
  totalObjects: number
  camerasActive: number
  camerasProcessing: number
  byCamera: Record<string, CameraDetectionState>
  averageFPS: number
}

// Configuración de modelos
export interface ModelConfig {
  enabled: boolean              // Si el modelo está activo
  threshold: number            // Umbral de confianza (0-1)
  fps: number                   // Frecuencia de procesamiento
}

// Configuración de la aplicación
export interface AppConfig {
  // Modelos
  personDetection: ModelConfig  // Detección de personas (YOLO)
  faceDetection: ModelConfig    // Detección de rostros (MediaPipe)
  emotionDetection: ModelConfig // Detección de emociones (TF.js)
  poseDetection: ModelConfig    // Detección de pose (MediaPipe)
  handDetection: ModelConfig    // Detección de manos (MediaPipe)
  movementDetection: ModelConfig // Detección de movimiento (OpenCV)
  objectDetection: ModelConfig  // Detección de objetos (YOLO)
  
  // Configuración general
  anonymizeData: boolean        // Anonimizar datos
  saveImages: boolean           // Guardar imágenes (por defecto false)
  cameraResolution: 'low' | 'medium' | 'high' // Resolución de cámara por defecto
}

// Estado de detección en tiempo real
export interface DetectionState {
  isProcessing: boolean         // Si está procesando
  currentFPS: number            // FPS actual
  detections: {                 // Detecciones actuales
    persons: number
    faces: number
    emotions: EmotionType[]
    activity: ActivityType | null
    healthStatus: HealthStatus | null
    objects: Array<{ 
      label: string
      confidence: number
      bbox?: { x: number; y: number; width: number; height: number }
    }>
  }
  lastEvent: Event | null       // Último evento guardado
}

export interface ExternalCamera {
  id: string
  user_id: string
  name: string
  source_url: string
  auth_username?: string | null
  auth_password?: string | null
  stream_id?: string | null
  hls_url?: string | null
  status: 'running' | 'starting' | 'stopped' | 'error'
  created_at: string
}

export interface ExternalCameraPayload {
  name: string
  sourceUrl: string
  username?: string
  password?: string
}

export interface DemoSessionRecord {
  session_id: string
  name?: string | null
  email?: string | null
  plan?: string | null
  ip_address?: string | null
  user_agent?: string | null
  referer?: string | null
  cameras_active?: number | null
  fps_average?: number | null
  tokens_used?: number | null
  status?: string | null
  started_at?: string | null
  last_ping_at?: string | null
  admin_note?: string | null
  metadata?: Record<string, unknown> | null
}

export interface AdminSessionsResponse {
  sessions: DemoSessionRecord[]
  totals: Record<string, number>
  generated_at: string
}

