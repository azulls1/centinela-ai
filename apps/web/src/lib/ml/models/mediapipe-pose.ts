/**
 * Integración de MediaPipe Pose para detección de poses/personas
 * Detecta poses completas del cuerpo en tiempo real
 * Usa runningMode: VIDEO para mantener el WebGL context entre frames
 */

import { PoseLandmarker, FilesetResolver } from '@mediapipe/tasks-vision'
import { logDebug, logError, logWarn as _logWarn } from '../../../utils/logger'

let poseLandmarker: PoseLandmarker | null = null
let isModelLoading = false
let isModelLoaded = false
let lastTimestamp = -1

// Cached offscreen canvas for converting ImageData to a canvas element
// MediaPipe VIDEO mode requires HTMLCanvasElement/HTMLVideoElement, not ImageData
let _offscreenCanvas: HTMLCanvasElement | null = null
function getOffscreenCanvas(width: number, height: number): HTMLCanvasElement {
  if (!_offscreenCanvas) {
    _offscreenCanvas = document.createElement('canvas')
  }
  if (_offscreenCanvas.width !== width || _offscreenCanvas.height !== height) {
    _offscreenCanvas.width = width
    _offscreenCanvas.height = height
  }
  return _offscreenCanvas
}

const POSE_MODEL_URL =
  'https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_full/float16/latest/pose_landmarker_full.task'

/**
 * Cargar modelo MediaPipe Pose
 */
export async function loadMediaPipePose(): Promise<PoseLandmarker | null> {
  if (isModelLoaded && poseLandmarker) {
    return poseLandmarker
  }

  if (isModelLoading) {
    while (isModelLoading) {
      await new Promise(resolve => setTimeout(resolve, 100))
    }
    return poseLandmarker
  }

  try {
    isModelLoading = true
    logDebug('📦 Cargando MediaPipe Pose...')

    const vision = await FilesetResolver.forVisionTasks(
      'https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.9/wasm'
    )

    // CPU delegate avoids WebGL context thrashing when multiple MediaPipe models run
    poseLandmarker = await PoseLandmarker.createFromOptions(vision, {
      baseOptions: {
        modelAssetPath: POSE_MODEL_URL,
        delegate: 'CPU',
      },
      runningMode: 'VIDEO',
      numPoses: 3,
      minPoseDetectionConfidence: 0.5,
      minPosePresenceConfidence: 0.5,
      minTrackingConfidence: 0.5,
    })

    isModelLoaded = true
    isModelLoading = false
    logDebug('✅ MediaPipe Pose cargado exitosamente')
    return poseLandmarker
  } catch (error) {
    logError('❌ Error cargando MediaPipe Pose', error)
    isModelLoading = false
    return null
  }
}

/**
 * Detectar poses/personas en un frame
 * @param input - HTMLCanvasElement (preferred) or ImageData of the frame
 * @returns Número de personas detectadas y sus poses
 */
export async function detectPosesWithMediaPipe(
  input: HTMLCanvasElement | ImageData
): Promise<{
  poses: Array<{
    confidence: number
    landmarks: Array<{ x: number; y: number; z?: number }>
  }>
}> {
  try {
    const landmarker = await loadMediaPipePose()
    if (!landmarker) {
      return { poses: [] }
    }

    // VIDEO mode requires monotonically increasing timestamps
    const now = performance.now()
    const timestamp = now <= lastTimestamp ? lastTimestamp + 1 : now
    lastTimestamp = timestamp

    // Resolve input to a canvas element -- detectForVideo needs
    // HTMLVideoElement | HTMLCanvasElement | HTMLImageElement, NOT ImageData
    let canvasInput: HTMLCanvasElement
    if (input instanceof HTMLCanvasElement) {
      canvasInput = input
    } else {
      // ImageData fallback: draw onto a cached offscreen canvas
      canvasInput = getOffscreenCanvas(input.width, input.height)
      const ctx = canvasInput.getContext('2d')
      if (!ctx) return { poses: [] }
      ctx.putImageData(input, 0, 0)
    }

    // detectForVideo instead of detect (VIDEO mode)
    const result = landmarker.detectForVideo(canvasInput, timestamp)

    return {
      poses: result.landmarks.map((landmarks, _index) => ({
        confidence: 0.85,
        landmarks: landmarks.map(lm => ({
          x: lm.x,
          y: lm.y,
          z: lm.z || 0,
        })),
      })),
    }
  } catch (error) {
    logError('Error en detección MediaPipe Pose', error)
    return { poses: [] }
  }
}

/**
 * Verificar si el modelo está cargado
 */
export function isMediaPipePoseLoaded(): boolean {
  return isModelLoaded && poseLandmarker !== null
}
