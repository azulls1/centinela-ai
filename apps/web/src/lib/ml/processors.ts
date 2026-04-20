import { AppConfig, DetectionState, EmotionType, ActivityType, HealthStatus } from '../../types'
import { detectObjectsWithCocoSsd, isCocoSsdLoaded } from './models/coco-ssd'
import { loadYolov8Model, detectObjectsWithYolov8, isYolov8Loaded } from './models/yolov8'
import { loadMediaPipeFaceDetector, detectFacesWithMediaPipe, isMediaPipeFaceLoaded } from './models/mediapipe-face'
import { loadEmotionModel, classifyEmotion, isEmotionModelLoaded } from './models/emotion-model'

const debugLog = (..._args: unknown[]) => {} // Keep silent for performance
const logError = (message: string, error?: unknown) => { console.error(`[ML] ${message}`, error) }
const logWarn = (message: string, error?: unknown) => { console.warn(`[ML] ${message}`, error) }

/**
 * Procesadores de ML para diferentes tipos de detección
 * Cada procesador maneja un modelo específico
 * 
 * MODELOS REALES INTEGRADOS:
 * - TensorFlow.js COCO-SSD: Detección de objetos (80 clases COCO)
 * - face-api TinyFaceDetector: Detección de rostros (TF.js, shares WebGL context)
 * - YOLOv8n: Detección de personas/objetos (ONNX Runtime)
 */

// Estado global de modelos cargados
let modelsLoaded = false // Flag para saber si los modelos están cargados
let cocoSsdModel: any = null // Modelo COCO-SSD para detección de objetos
let _faceDetectorReady: boolean = false // face-api TinyFaceDetector

interface CameraProcessingState {
  lastProcessedFrameTime: number
  processingCanvas: HTMLCanvasElement
  personDetectionHistory: Array<{ detected: boolean; timestamp: number }>
  emotionHistory: Array<{ emotion: EmotionType; timestamp: number }>
  activityHistory: Array<{ activity: ActivityType; timestamp: number }>
  healthStatusHistory: Array<{ status: HealthStatus; timestamp: number }>
  trackedObjects: Map<string, TrackedObject>
  nextObjectId: number
}

const cameraStates = new Map<string, CameraProcessingState>()

// Store previous frame for comparison (movement detection)
const previousFrames = new Map<string, ImageData>()

function createCameraState(): CameraProcessingState {
  return {
    lastProcessedFrameTime: 0,
    processingCanvas: document.createElement('canvas'),
    personDetectionHistory: [],
    emotionHistory: [],
    activityHistory: [],
    healthStatusHistory: [],
    trackedObjects: new Map(),
    nextObjectId: 0,
  }
}

function getCameraState(cameraId: string): CameraProcessingState {
  let state = cameraStates.get(cameraId)
  if (!state) {
    state = createCameraState()
    cameraStates.set(cameraId, state)
  }
  return state
}

export function resetCameraState(cameraId: string) {
  cameraStates.delete(cameraId)
}

export function resetAllCameraStates() {
  cameraStates.clear()
}

/**
 * Verificar si los modelos están cargados
 * @returns true si los modelos están listos
 */
export function isModelsLoaded(): boolean {
  return modelsLoaded
}

/**
 * Cargar todos los modelos necesarios
 * Se ejecuta en segundo plano, no bloquea la cámara
 * 
 * MODELOS REALES:
 * - COCO-SSD: ~10MB (TensorFlow.js)
 * - face-api TinyFaceDetector: ~190KB (TensorFlow.js, shares WebGL context)
 * - FaceExpressionNet: ~330KB (TensorFlow.js)
 * - YOLOv8n: ~13MB (ONNX Runtime)
 */
export async function loadModels() {
  if (modelsLoaded) return // Si ya están cargados, no hacer nada

  try {
    debugLog('🚀 Cargando modelos de ML reales...')
    debugLog('📦 Esto puede tardar unos segundos en la primera carga...')

    // Load only the models we actually use.
    // COCO-SSD is NOT loaded — YOLO handles all object detection.
    // Removing COCO-SSD frees the TF.js WebGL context for face-api.
    const [faceModel, emotionModelResult, yolov8Result] = await Promise.allSettled([
      loadMediaPipeFaceDetector(),
      loadEmotionModel(),
      loadYolov8Model(),
    ])

    // Report model loading status (always visible in console)
    const status: string[] = []

    if (faceModel.status === 'fulfilled' && faceModel.value) {
      _faceDetectorReady = true
      status.push('FaceDetector: OK')
    } else {
      status.push('FaceDetector: FAILED')
      logWarn('face-api TinyFaceDetector no disponible', faceModel.status === 'rejected' ? faceModel.reason : 'load returned false')
    }

    if (emotionModelResult.status === 'fulfilled' && emotionModelResult.value) {
      status.push('EmotionNet: OK')
    } else {
      status.push('EmotionNet: FAILED')
      logWarn('FaceExpressionNet no disponible', emotionModelResult.status === 'rejected' ? emotionModelResult.reason : 'load returned false')
    }

    if (yolov8Result.status === 'fulfilled' && yolov8Result.value) {
      status.push('YOLOv8n: OK')
    } else {
      status.push('YOLOv8n: FAILED')
      logWarn('YOLOv8n no disponible', yolov8Result.status === 'rejected' ? yolov8Result.reason : 'load returned false')
    }

    modelsLoaded = true
    console.log(`[ML] Models loaded: ${status.join(' | ')}`)
  } catch (error) {
    logError('❌ Error cargando modelos', error)
    // No lanzar error, permitir que la app continúe con simulación
    modelsLoaded = true // Marcar como cargado para no intentar de nuevo
  }
}

/**
 * Procesar un frame de video con todos los modelos activos
 * @param canvas - Canvas con el frame actual
 * @param config - Configuración de la aplicación
 * @param callback - Callback con las detecciones
 */
const MIN_FRAME_INTERVAL_MS = 150 // Mínimo 150ms entre procesamientos (~6-7 FPS ML)

export async function processFrame(
  canvas: HTMLCanvasElement,
  config: AppConfig,
  cameraId: string,
  callback: (detections: DetectionState['detections']) => void
) {
  const cameraState = getCameraState(cameraId)

  // Throttling adicional: evitar procesar frames demasiado rápido
  const now = Date.now()
  if (now - cameraState.lastProcessedFrameTime < MIN_FRAME_INTERVAL_MS) {
    return // Skip este frame
  }
  cameraState.lastProcessedFrameTime = now

  // Asegurar que los modelos estén cargados
  if (!modelsLoaded) {
    debugLog('🔄 Modelos no cargados, cargando...')
    await loadModels()
    debugLog('✅ Modelos cargados:', modelsLoaded)
  }

  // Verificar que los modelos estén realmente listos
  if (!modelsLoaded) {
    logWarn('⚠️ Modelos no disponibles después de intentar cargar')
    callback({
      persons: 0,
      faces: 0,
      emotions: [],
      activity: null,
      healthStatus: null,
      objects: [],
    })
    return
  }

  const yieldToMainThread = async (delay = 0) =>
    new Promise<void>((resolve) => setTimeout(resolve, delay))

  // Usar canvas reducido para ML (más rápido, suficiente para detección)
  const processingCanvas = cameraState.processingCanvas
  const aspectRatio = canvas.width > 0 && canvas.height > 0 ? canvas.width / canvas.height : 4 / 3
  const targetWidth = Math.min(640, canvas.width || 640)
  const targetHeight = Math.max(180, Math.round(targetWidth / aspectRatio))

  if (processingCanvas.width !== targetWidth || processingCanvas.height !== targetHeight) {
    processingCanvas.width = targetWidth
    processingCanvas.height = targetHeight
  }
  
  const mlCtx = processingCanvas.getContext('2d', { willReadFrequently: true })
  if (mlCtx && canvas.width > 0 && canvas.height > 0) {
    mlCtx.drawImage(canvas, 0, 0, targetWidth, targetHeight)
  }

  const mlCanvas = processingCanvas
  const scaleX = canvas.width / mlCanvas.width
  const scaleY = canvas.height / mlCanvas.height

  const detections: DetectionState['detections'] = {
    persons: 0,
    faces: 0,
    emotions: [],
    activity: null,
    healthStatus: null,
    objects: [],
  }

  let personObjects: DetectionState['detections']['objects'] = []
  let objectDetections: DetectionState['detections']['objects'] = []

  // ─── Single YOLO pass: avoids running inference twice (persons + objects) ───
  let yoloResults: Array<{ label: string; confidence: number; bbox: { x: number; y: number; width: number; height: number } }> | null = null
  const needsYolo = (config.personDetection.enabled || config.objectDetection.enabled) && isYolov8Loaded()
  if (needsYolo) {
    try {
      const minThreshold = Math.min(
        config.personDetection.enabled ? config.personDetection.threshold : 1,
        config.objectDetection.enabled ? config.objectDetection.threshold : 1,
      )
      yoloResults = await detectObjectsWithYolov8(mlCanvas, minThreshold)
    } catch {
      yoloResults = null
    }
    await yieldToMainThread()
  }

  try {
    // Detección de personas
  if (config.personDetection.enabled) {
    try {
      if (yoloResults) {
        const persons = yoloResults.filter(d => d.label.toLowerCase() === 'person' && d.confidence >= config.personDetection.threshold)
        detections.persons = persons.length
        personObjects = persons.map(p => ({
          label: 'Persona',
          confidence: p.confidence,
          bbox: {
            x: p.bbox.x * scaleX,
            y: p.bbox.y * scaleY,
            width: p.bbox.width * scaleX,
            height: p.bbox.height * scaleY,
          },
        }))
      } else {
        const personDetections = await detectPersons(mlCanvas, config.personDetection.threshold)
        detections.persons = personDetections.length
        personObjects = personDetections.map((p) => ({
          label: 'Persona',
          confidence: p.confidence,
          bbox: {
            x: (p.bbox[0] as number) * scaleX,
            y: (p.bbox[1] as number) * scaleY,
            width: (p.bbox[2] as number) * scaleX,
            height: (p.bbox[3] as number) * scaleY,
          },
        }))
      }
    } catch (error) {
        logError('Error en detección de personas', error)
        detections.persons = 0
    }
      // Deduplicate: keep only highest-confidence person per spatial region
      if (personObjects.length > 1) {
        personObjects.sort((a, b) => b.confidence - a.confidence)
        personObjects = [personObjects[0]] // Keep only the best detection for now
        detections.persons = 1
      }
      await yieldToMainThread()
    } else {
      detections.persons = 0
  }

    // Face & emotion detection
  if (config.faceDetection.enabled) {
    try {
        const faceDetections = await detectFaces(mlCanvas, config.faceDetection.threshold)
        detections.faces = faceDetections.length

      if (faceDetections.length > 0 && config.emotionDetection.enabled) {
          try {
            const emotions = await detectEmotions(mlCanvas, faceDetections, config.emotionDetection.threshold, cameraState)
            detections.emotions = emotions
          } catch (error) {
            logError('Error en detección de emociones', error)
            detections.emotions = []
          }
        } else {
          detections.emotions = []
      }
    } catch (error) {
        logError('Error en detección de rostros', error)
        detections.faces = 0
        detections.emotions = []
    }
      await yieldToMainThread()
    } else {
      detections.faces = 0
      detections.emotions = []
  }

    // Movement detection
  if (config.movementDetection.enabled) {
    try {
      const activity = await detectMovement(mlCanvas, config.movementDetection.threshold, cameraState)
      detections.activity = activity
    } catch (error) {
        logError('Error en detección de movimiento', error)
    }
      await yieldToMainThread()
  } else {
    detections.activity = null
  }

    // Object detection (non-person objects)
  if (config.objectDetection.enabled) {
    try {
        let rawObjects: Array<{ label: string; confidence: number; bbox: { x: number; y: number; width: number; height: number } }>
        if (yoloResults) {
          rawObjects = filterFalsePositives(
            yoloResults.filter(d => d.label.toLowerCase() !== 'person' && d.confidence >= config.objectDetection.threshold)
          )
        } else {
          rawObjects = await detectObjects(mlCanvas, config.objectDetection.threshold)
        }
        objectDetections = rawObjects.map((obj) => ({
          ...obj,
          bbox: {
            x: obj.bbox.x * scaleX,
            y: obj.bbox.y * scaleY,
            width: obj.bbox.width * scaleX,
            height: obj.bbox.height * scaleY,
          },
        }))
    } catch (error) {
        logError('Error en detección de objetos', error)
    }
    }
  } catch (error) {
    logError('Error general en pipeline de detección', error)
  }

  // Combine all detections directly — no complex tracking system
  detections.objects = [...personObjects, ...objectDetections]

  // Estimación de estado de salud (muy rápido, solo cálculo)
  if (detections.persons === 0) {
    detections.healthStatus = null
    detections.activity = null
  } else if (detections.emotions.length > 0 || detections.activity) {
    detections.healthStatus = estimateHealthStatus(detections, cameraState)
  }

  // Log de detecciones para debugging
  debugLog('✅ Detecciones resumidas', {
    personas: detections.persons,
    rostros: detections.faces,
    objetos: detections.objects.length,
    emociones: detections.emotions.length,
    actividad: detections.activity,
  })

  // Llamar callback con las detecciones
  callback(detections)
}

/**
 * Detectar personas usando YOLO
 * @param canvas - Canvas con el frame
 * @param threshold - Umbral de confianza
 * @returns Array de detecciones
 */
async function detectPersons(canvas: HTMLCanvasElement, threshold: number) {
  // Primary: YOLOv8 for person detection
  if (isYolov8Loaded()) {
    try {
      const allDetections = await detectObjectsWithYolov8(canvas, threshold)
      const persons = allDetections.filter(d => d.label.toLowerCase() === 'person')
      if (persons.length > 0) {
        return persons.map(p => ({
          bbox: [p.bbox.x, p.bbox.y, p.bbox.width, p.bbox.height] as [number, number, number, number],
          confidence: p.confidence,
        }))
      }
    } catch (error) {
      logWarn('[Processors] YOLOv8 person detection failed', error)
    }
  }

  // Fallback 2: Usar COCO-SSD para detectar personas
  if (isCocoSsdLoaded() && cocoSsdModel) {
    try {
      const objects = await detectObjectsWithCocoSsd(canvas, threshold)
      // Filtrar solo objetos tipo "person"
      const persons = objects.filter(obj => obj.label.toLowerCase() === 'person')
      
      return persons.map(obj => ({
        bbox: [
          obj.bbox.x,
          obj.bbox.y,
          obj.bbox.width,
          obj.bbox.height,
        ],
        confidence: obj.confidence,
      }))
    } catch (error) {
      logError('Error en COCO-SSD para personas', error)
      // Continuar con simulación como último recurso
    }
  }
  
  // No models available - return empty instead of fake data
  return []
}

/**
 * Detectar rostros usando face-api TinyFaceDetector
 * @param canvas - Canvas con el frame
 * @param threshold - Umbral de confianza
 * @returns Array de detecciones faciales
 */
async function detectFaces(canvas: HTMLCanvasElement, threshold: number) {
  // Use face-api TinyFaceDetector (shares TF.js WebGL context with COCO-SSD)
  if (isMediaPipeFaceLoaded()) {
    try {
      const detections = await detectFacesWithMediaPipe(canvas, threshold)
      
      return detections.map(det => ({
        landmarks: det.landmarks || [],
        confidence: det.confidence,
        bbox: [
          det.bbox[0],
          det.bbox[1],
          det.bbox[2],
          det.bbox[3],
        ],
      }))
    } catch (error) {
    logError('Error en face-api Face Detection', error)
      // Continuar con fallback
    }
  }
  
  // Fallback: Simulación simple (solo si MediaPipe no está disponible)
  // En modo conservador, retornar vacío para evitar falsos positivos
  return []
}

const EMOTION_STABILIZATION_WINDOW = 1500 // 1.5 segundos

/**
 * Detectar emociones usando FaceExpressionNet (CNN real, ~330 KB)
 *
 * Utiliza el modelo ML de @vladmandic/face-api en lugar de la heurística
 * geométrica anterior. El modelo clasifica 7 emociones básicas:
 * neutral, happy, sad, angry, fearful, disgusted, surprised.
 *
 * @param canvas - Canvas con el frame (escala ML)
 * @param faces - Rostros detectados por MediaPipe (con bbox)
 * @param threshold - Umbral de confianza mínima
 * @param state - Estado de procesamiento por cámara (para estabilización)
 * @returns Array de emociones detectadas (estabilizadas)
 */
async function detectEmotions(
  canvas: HTMLCanvasElement,
  faces: any[],
  threshold: number,
  state: CameraProcessingState
): Promise<EmotionType[]> {
  if (!faces || faces.length === 0) {
    state.emotionHistory = []
    return []
  }

  const detectedEmotions: EmotionType[] = []

  // ── ML-based emotion classification (primary path) ──
  if (isEmotionModelLoaded()) {
    for (const face of faces) {
      // Use the bounding box from MediaPipe face detection
      const bbox = face.bbox as [number, number, number, number] | undefined
      if (!bbox || bbox[2] <= 0 || bbox[3] <= 0) continue

      try {
        const prediction = await classifyEmotion(canvas, bbox, threshold)
        if (prediction) {
          detectedEmotions.push(prediction.emotion)
        }
      } catch (error) {
        logWarn('Emotion classification error for face', error)
      }
    }
  } else {
    // ── Geometric fallback (only when model failed to load) ──
    // This preserves basic functionality while the model is unavailable.
    for (const face of faces) {
      if (!face.landmarks || face.landmarks.length < 6) continue

      const landmarks = face.landmarks
      let emotion: EmotionType = 'neutral'

      const rightEye = landmarks[0]
      const leftEye = landmarks[1]
      const noseTip = landmarks[2]
      const mouthCenter = landmarks[3]

      if (rightEye && leftEye && noseTip && mouthCenter) {
        const eyeDistance = Math.sqrt(
          Math.pow(leftEye.x - rightEye.x, 2) + Math.pow(leftEye.y - rightEye.y, 2)
        )

        if (eyeDistance > 0) {
          const mouthNoseDistance = (mouthCenter.y - noseTip.y) / eyeDistance
          const eyeMidY = (rightEye.y + leftEye.y) / 2
          const noseToEyeLine = (noseTip.y - eyeMidY) / eyeDistance

          if (mouthNoseDistance > 0.85) {
            emotion = 'surprised'
          } else if (mouthNoseDistance > 0.65 && noseToEyeLine < 0.35) {
            emotion = 'happy'
          } else if (noseToEyeLine > 0.55) {
            emotion = 'sad'
          } else if (mouthNoseDistance < 0.35) {
            emotion = 'angry'
          } else {
            emotion = 'focused'
          }
        }
      }

      detectedEmotions.push(emotion)
    }
  }

  // Stabilize emotions using history (same logic for both paths)
  const now = Date.now()
  for (const emotion of detectedEmotions) {
    state.emotionHistory.push({ emotion, timestamp: now })
  }
  state.emotionHistory = state.emotionHistory.filter(
    e => now - e.timestamp < EMOTION_STABILIZATION_WINDOW
  )

  // Return most frequent emotion from recent history
  if (state.emotionHistory.length === 0) return []

  const emotionCounts = new Map<EmotionType, number>()
  for (const entry of state.emotionHistory) {
    emotionCounts.set(entry.emotion, (emotionCounts.get(entry.emotion) || 0) + 1)
  }

  const sortedEmotions = [...emotionCounts.entries()]
    .sort((a, b) => b[1] - a[1])
    .filter(([_, count]) => count >= 2) // At least 2 detections
    .map(([emotion]) => emotion)

  return sortedEmotions.length > 0 ? [sortedEmotions[0]] : detectedEmotions.slice(0, 1)
}

const ACTIVITY_STABILIZATION_WINDOW = 1800 // 1.8 segundos

/**
 * Detectar movimiento usando OpenCV.js
 * @param canvas - Canvas con el frame
 * @param threshold - Umbral de movimiento
 * @returns Tipo de actividad detectada (estabilizada)
 */
async function detectMovement(
  canvas: HTMLCanvasElement,
  threshold: number,
  state: CameraProcessingState
): Promise<ActivityType | null> {
  const ctx = canvas.getContext('2d', { willReadFrequently: true })
  if (!ctx) return null

  const currentFrame = ctx.getImageData(0, 0, canvas.width, canvas.height)
  const cameraKey = `movement-${canvas.width}x${canvas.height}`
  const prevFrame = previousFrames.get(cameraKey)

  // Store current frame for next comparison
  previousFrames.set(cameraKey, currentFrame)

  if (!prevFrame || prevFrame.width !== currentFrame.width || prevFrame.height !== currentFrame.height) {
    return null // Need at least 2 frames
  }

  // Calculate pixel difference between frames
  const pixels = currentFrame.data.length / 4
  let diffSum = 0
  const step = 4 // Sample every 4th pixel for performance

  for (let i = 0; i < currentFrame.data.length; i += 4 * step) {
    const rDiff = Math.abs(currentFrame.data[i] - prevFrame.data[i])
    const gDiff = Math.abs(currentFrame.data[i + 1] - prevFrame.data[i + 1])
    const bDiff = Math.abs(currentFrame.data[i + 2] - prevFrame.data[i + 2])
    diffSum += (rDiff + gDiff + bDiff) / 3
  }

  const sampledPixels = Math.floor(pixels / step)
  const avgDiff = diffSum / sampledPixels / 255 // Normalize to 0-1

  // Classify activity based on movement amount
  let activity: ActivityType | null = null

  if (avgDiff > threshold * 0.3) {
    activity = 'walking' // High movement
  } else if (avgDiff > threshold * 0.1) {
    activity = 'active' // Moderate movement
  } else if (avgDiff > threshold * 0.03) {
    activity = 'standing' // Low movement (small gestures)
  } else if (avgDiff > threshold * 0.005) {
    activity = 'sitting' // Very low movement
  } else {
    activity = 'inactive' // Almost no movement
  }

  // Stabilize using history
  const now = Date.now()
  if (activity) {
    state.activityHistory.push({ activity, timestamp: now })
  }
  state.activityHistory = state.activityHistory.filter(
    a => now - a.timestamp < ACTIVITY_STABILIZATION_WINDOW
  )

  if (state.activityHistory.length < 2) return activity

  // Return most frequent activity
  const activityCounts = new Map<ActivityType, number>()
  for (const entry of state.activityHistory) {
    activityCounts.set(entry.activity, (activityCounts.get(entry.activity) || 0) + 1)
  }

  let maxCount = 0
  let dominantActivity: ActivityType = activity
  for (const [act, count] of activityCounts) {
    if (count > maxCount) {
      maxCount = count
      dominantActivity = act
    }
  }

  return dominantActivity
}

// ============================================================================
// SISTEMA DE TRACKING DE OBJETOS CON PERSISTENCIA TEMPORAL
// Basado en técnicas de tracking de objetos en tiempo real (IOU tracking, Kalman filter)
// ============================================================================

/**
 * Representa un objeto siendo rastreado
 */
interface TrackedObject {
  id: string                    // ID único del objeto
  label: string                 // Tipo de objeto
  bbox: { x: number; y: number; width: number; height: number } // Bounding box
  confidence: number            // Confianza promedio
  firstSeen: number             // Timestamp de primera detección
  lastSeen: number              // Timestamp de última detección
  detectionCount: number        // Número de veces detectado
  age: number                   // Edad del objeto en frames
  isActive: boolean             // Si está activo actualmente
  smoothedBbox?: { x: number; y: number; width: number; height: number } // Bbox suavizado
}

// Tracking configuration
const MIN_DETECTIONS_TO_SHOW = 2           // Require 2 detections before showing (reduces false positives)
const MAX_AGE_WITHOUT_DETECTION = 5        // Remove stale tracked objects faster
const IOU_THRESHOLD = 0.25                 // Slightly more permissive for matching across frames
const CONFIDENCE_DECAY = 0.92              // Faster decay for inactive objects
const SMOOTHING_FACTOR = 0.65              // More responsive to position changes
const PERSISTENCE_TIME_MS = 1500           // Keep objects 1.5s after last detection (was 5s)

/**
 * Calcular Intersection over Union (IOU) entre dos bounding boxes
 */
function calculateIOU(bbox1: { x: number; y: number; width: number; height: number }, 
                      bbox2: { x: number; y: number; width: number; height: number }): number {
  const x1 = Math.max(bbox1.x, bbox2.x)
  const y1 = Math.max(bbox1.y, bbox2.y)
  const x2 = Math.min(bbox1.x + bbox1.width, bbox2.x + bbox2.width)
  const y2 = Math.min(bbox1.y + bbox1.height, bbox2.y + bbox2.height)
  
  if (x2 < x1 || y2 < y1) return 0
  
  const intersection = (x2 - x1) * (y2 - y1)
  const area1 = bbox1.width * bbox1.height
  const area2 = bbox2.width * bbox2.height
  const union = area1 + area2 - intersection
  
  return union > 0 ? intersection / union : 0
}

/**
 * Suavizar bounding box usando filtro exponencial
 */
function smoothBbox(current: { x: number; y: number; width: number; height: number },
                    previous?: { x: number; y: number; width: number; height: number }): { x: number; y: number; width: number; height: number } {
  if (!previous) return current
  
  return {
    x: previous.x * (1 - SMOOTHING_FACTOR) + current.x * SMOOTHING_FACTOR,
    y: previous.y * (1 - SMOOTHING_FACTOR) + current.y * SMOOTHING_FACTOR,
    width: previous.width * (1 - SMOOTHING_FACTOR) + current.width * SMOOTHING_FACTOR,
    height: previous.height * (1 - SMOOTHING_FACTOR) + current.height * SMOOTHING_FACTOR,
  }
}

/**
 * Asociar nuevas detecciones con objetos rastreados existentes
 */
function _associateDetections(
  newDetections: Array<{ label: string; confidence: number; bbox: any }>,
  state: CameraProcessingState
): Map<string, TrackedObject> {
  const trackedObjects = state.trackedObjects
  const now = Date.now()
    // Incrementar edad de objetos rastreados y gestionar estado
  for (const tracked of trackedObjects.values()) {
      tracked.age++
      
      const timeSinceLastDetection = now - tracked.lastSeen
      
      // Reducir confianza gradualmente cuando no se detecta
      if (timeSinceLastDetection > 1500 && tracked.isActive) {
        tracked.confidence *= CONFIDENCE_DECAY
      }

      // Desactivar despues de tiempo suficiente sin deteccion
      if (timeSinceLastDetection > 3000) {
        tracked.isActive = false
      }
      
      // Eliminar objetos que no se han visto por mucho tiempo
      if (timeSinceLastDetection > PERSISTENCE_TIME_MS * 2) {
        tracked.confidence *= 0.9 // Decaimiento acelerado
      }
  }
  
  // Para cada nueva detección, buscar objeto rastreado más cercano
  for (const detection of newDetections) {
    let bestMatch: { tracked: TrackedObject; iou: number } | null = null
    
    // Buscar objeto rastreado del mismo tipo con mejor IOU
    // Buscar tanto objetos activos como recientemente inactivos (para reactivarlos)
    for (const tracked of trackedObjects.values()) {
      if (tracked.label === detection.label) {
        // Considerar objetos activos o recientemente inactivos (últimos 1.5 segundos)
        const isRecentlyInactive = !tracked.isActive && (now - tracked.lastSeen) < 1500
        if (tracked.isActive || isRecentlyInactive) {
          const iou = calculateIOU(tracked.bbox, detection.bbox)
          if (iou > IOU_THRESHOLD && (!bestMatch || iou > bestMatch.iou)) {
            bestMatch = { tracked, iou }
          }
        }
      }
    }
    
    if (bestMatch) {
      // Actualizar objeto rastreado existente
      const tracked = bestMatch.tracked
      tracked.bbox = smoothBbox(detection.bbox, tracked.smoothedBbox || tracked.bbox)
      tracked.smoothedBbox = tracked.bbox
      tracked.confidence = (tracked.confidence * 0.7 + detection.confidence * 0.3) // Promedio ponderado
      tracked.lastSeen = now
      tracked.detectionCount++
      tracked.isActive = true
      tracked.age = 0
    } else {
      // Crear nuevo objeto rastreado
      const newTracked: TrackedObject = {
        id: `obj_${state.nextObjectId++}`,
        label: detection.label,
        bbox: detection.bbox,
        smoothedBbox: detection.bbox,
        confidence: detection.confidence,
        firstSeen: now,
        lastSeen: now,
        detectionCount: 1,
        age: 0,
        isActive: false, // No activo hasta tener suficientes detecciones
      }
      trackedObjects.set(newTracked.id, newTracked)
    }
  }
  
  // Limpiar objetos muy antiguos sin detecciones
  for (const [id, tracked] of trackedObjects.entries()) {
    if (tracked.age > MAX_AGE_WITHOUT_DETECTION && !tracked.isActive) {
      trackedObjects.delete(id)
    }
  }
  
  return trackedObjects
}

/**
 * Obtener objetos que deben mostrarse (con suficiente persistencia)
 */
function _getVisibleTrackedObjects(state: CameraProcessingState): Array<{ label: string; confidence: number; bbox: any }> {
  const trackedObjects = state.trackedObjects
  const now = Date.now()
  const visible: Array<{ label: string; confidence: number; bbox: any }> = []
  
  trackedObjects.forEach(tracked => {
    // Calcular tiempo desde última detección
    const timeSinceLastDetection = now - tracked.lastSeen
    
    // Un objeto debe mostrarse si:
    // 1. Ha sido detectado suficientes veces (persistencia inicial)
    // 2. Está activo actualmente O fue detectado recientemente (persistencia temporal)
    // 3. Tiene confianza mínima
    const hasEnoughDetections = tracked.detectionCount >= MIN_DETECTIONS_TO_SHOW
    const isCurrentlyActive = tracked.isActive
    const wasRecentlyDetected = timeSinceLastDetection < PERSISTENCE_TIME_MS
    const hasMinConfidence = tracked.confidence >= 0.60 // Reducido ligeramente para objetos rastreados
    
    const shouldShow = hasEnoughDetections && 
                      (isCurrentlyActive || wasRecentlyDetected) && 
                      hasMinConfidence
    
    if (shouldShow && tracked.smoothedBbox) {
      // Apply confidence decay for inactive objects
      let displayConfidence = tracked.confidence
      if (!isCurrentlyActive && timeSinceLastDetection > 500) {
        const decayFactor = Math.max(0.65, 1 - (timeSinceLastDetection / PERSISTENCE_TIME_MS) * 0.35)
        displayConfidence = tracked.confidence * decayFactor
      }
      
      visible.push({
        label: tracked.label,
        confidence: Math.max(0.60, displayConfidence), // Asegurar confianza mínima visible
        bbox: tracked.smoothedBbox,
      })
    }
  })
  
  // Deduplicate: keep only the highest-confidence bbox per label per spatial region
  visible.sort((a, b) => b.confidence - a.confidence)
  const final: typeof visible = []
  for (const obj of visible) {
    const isDuplicate = final.some(
      k => k.label === obj.label && calculateIOU(k.bbox, obj.bbox) > 0.2
    )
    if (!isDuplicate) final.push(obj)
  }
  return final
}

/**
 * Filtrar objetos falsos positivos con reglas simplificadas
 * Pass 1: Per-class confidence thresholds
 * Pass 2: Deduplicate keeping up to 2 spatially-separated instances per label
 * Pass 3: Limit total devices to 3
 */
function filterFalsePositives(objects: any[]): any[] {
  if (objects.length === 0) return []

  const animalLabels = ['dog', 'cat', 'horse', 'sheep', 'cow', 'elephant', 'bear', 'zebra', 'giraffe', 'bird']
  const furnitureLabels = ['couch', 'bed', 'dining table', 'tv']
  const deviceLabels = ['laptop', 'tv', 'keyboard', 'mouse', 'cell phone']

  // --- Pass 1: Per-class confidence filtering ---
  const filtered = objects.filter(obj => {
    const label = obj.label.toLowerCase()

    // Animals: require 75% confidence (lowered from 88%)
    if (animalLabels.includes(label)) {
      return obj.confidence >= 0.75
    }

    // Furniture / large objects: require 70% confidence (lowered from 85%)
    if (furnitureLabels.includes(label)) {
      return obj.confidence >= 0.70
    }

    // Everything else: require 65% confidence (unchanged)
    return obj.confidence >= 0.65
  })

  // --- Pass 2: Deduplicate per label, allowing up to 2 spatially-separated instances ---
  const kept: typeof objects = []
  const byLabel = new Map<string, typeof objects>()

  // Group by label, sorted by confidence descending
  for (const obj of filtered) {
    const label = obj.label.toLowerCase()
    if (!byLabel.has(label)) byLabel.set(label, [])
    byLabel.get(label)!.push(obj)
  }

  for (const [, group] of byLabel) {
    // Sort by confidence descending
    group.sort((a: any, b: any) => b.confidence - a.confidence)

    // Always keep the highest-confidence instance
    const accepted = [group[0]]

    // Allow a second instance only if it is spatially separated (IOU < 0.3)
    for (let i = 1; i < group.length && accepted.length < 2; i++) {
      const isSeparated = accepted.every(
        (existing: any) => calculateIOU(existing.bbox, group[i].bbox) < 0.3
      )
      if (isSeparated) {
        accepted.push(group[i])
      }
    }

    kept.push(...accepted)
  }

  // --- Pass 3: Limit total devices to 3 ---
  const devices = kept.filter(o => deviceLabels.includes(o.label.toLowerCase()))
  if (devices.length > 3) {
    devices.sort((a: any, b: any) => b.confidence - a.confidence)
    const toRemove = new Set(devices.slice(3))
    return kept.filter(o => !toRemove.has(o))
  }

  return kept
}

/**
 * Detectar objetos usando COCO-SSD
 *
 * @param canvas - Canvas con el frame
 * @param threshold - Umbral de confianza
 * @returns Array de objetos detectados con label, confidence y bounding box
 */
async function detectObjects(
  canvas: HTMLCanvasElement,
  threshold: number
) {
  // Try YOLOv8 first (better accuracy ~28% mAP vs ~22% mAP)
  if (isYolov8Loaded()) {
    try {
      const rawDetections = await detectObjectsWithYolov8(canvas, threshold)
      const objects = rawDetections.filter(d => d.label.toLowerCase() !== 'person' && d.confidence >= threshold)
      return filterFalsePositives(objects)
    } catch (error) {
      logWarn('[Processors] YOLOv8 detection failed, falling back to COCO-SSD', error)
    }
  }

  // FALLBACK: TensorFlow.js COCO-SSD
  if (isCocoSsdLoaded() && cocoSsdModel) {
    try {
      const detections = await detectObjectsWithCocoSsd(canvas, threshold)

      // Exclude "person" (detected separately) and apply false-positive filter
      const nonPersonDetections = detections.filter(obj => {
        if (obj.label.toLowerCase() === 'person') return false
        return obj.confidence >= threshold
      })

      return filterFalsePositives(nonPersonDetections)
    } catch (error) {
      logError('Error en COCO-SSD', error)
    }
  }

  // No model available - return empty to avoid fake data
  return []
}

const HEALTH_STABILIZATION_WINDOW = 1800 // 1.8 segundos

/**
 * Estimar estado de salud basado en emociones y actividad
 * @param detections - Detecciones actuales
 * @returns Estado de salud estimado (estabilizado)
 */
function estimateHealthStatus(
  detections: DetectionState['detections'],
  state: CameraProcessingState
): HealthStatus | null {
  const now = Date.now()
  
  // Limpiar historial antiguo
  state.healthStatusHistory = state.healthStatusHistory.filter(
    h => now - h.timestamp < HEALTH_STABILIZATION_WINDOW * 2
  )
  
  // Lógica simple de estimación
  let estimatedStatus: HealthStatus = 'normal'
  if (detections.activity === 'inactive') {
    estimatedStatus = 'tired'
  } else if (detections.emotions.includes('focused')) {
    estimatedStatus = 'focused'
  } else if (detections.emotions.includes('happy')) {
    estimatedStatus = 'normal'
  }
  
  // Agregar al historial
  state.healthStatusHistory.push({ status: estimatedStatus, timestamp: now })
  
  // Contar estados en la ventana de estabilización
  const recentStatuses = state.healthStatusHistory.filter(
    h => now - h.timestamp < HEALTH_STABILIZATION_WINDOW
  )
  
  // Contar ocurrencias de cada estado
  if (detections.persons === 0) {
    return null
  }
  
  const statusCounts = new Map<HealthStatus, number>()
  recentStatuses.forEach(h => {
    statusCounts.set(h.status, (statusCounts.get(h.status) || 0) + 1)
  })
  
  // Retornar el estado más frecuente solo si aparece al menos 2 veces
  if (statusCounts.size > 0) {
    const mostFrequent = Array.from(statusCounts.entries())
      .sort((a, b) => b[1] - a[1])[0]
    
    if (mostFrequent[1] >= 2) {
      return mostFrequent[0] as HealthStatus
    }
  }
  
  // Si no hay suficiente estabilidad, retornar el último estado calculado como fallback
  return recentStatuses.length > 0 ? recentStatuses[recentStatuses.length - 1].status : null
}

