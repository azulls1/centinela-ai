/**
 * Face Detection using @vladmandic/face-api (TinyFaceDetector)
 *
 * Replaces MediaPipe Face Detection which caused WebGL context thrashing
 * (creating/destroying WebGL contexts on every frame regardless of settings).
 *
 * face-api uses TensorFlow.js under the hood, sharing the same WebGL context
 * with COCO-SSD — zero context thrashing, no freezing, no camera restarts.
 *
 * Model weights are served from /models/face-expression/ alongside the
 * FaceExpressionNet weights (same directory, different model files).
 */

import * as faceapi from '@vladmandic/face-api/dist/face-api.esm-nobundle.js'
import { logDebug, logError, logWarn } from '../../../utils/logger'

// ── State ──────────────────────────────────────────────────────────

let isModelLoaded = false
let _loadPromise: Promise<boolean> | null = null

// Cached offscreen canvas for converting ImageData to a canvas element
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

// ── Public API ─────────────────────────────────────────────────────

/**
 * Load the TinyFaceDetector model weights.
 * Safe to call multiple times; loads only once.
 * Returns true on success (kept for compatibility with old loader signature).
 */
export async function loadMediaPipeFaceDetector(): Promise<boolean> {
  if (isModelLoaded) return true
  if (_loadPromise) return _loadPromise

  _loadPromise = (async () => {
    try {
      logDebug('Loading face-api TinyFaceDetector model...')

      const modelUrl = '/models/face-expression'

      // Only load if not already loaded (emotion-model.ts may have loaded
      // other nets from the same directory but not the detector).
      if (!faceapi.nets.tinyFaceDetector.isLoaded) {
        await faceapi.nets.tinyFaceDetector.loadFromUri(modelUrl)
      }

      isModelLoaded = true
      logDebug('TinyFaceDetector loaded successfully')
      return true
    } catch (error) {
      logError('Failed to load TinyFaceDetector', error)
      _loadPromise = null // Allow retry on failure
      return false
    }
  })()

  return _loadPromise
}

/**
 * Check whether the face detection model is ready for inference.
 */
export function isMediaPipeFaceLoaded(): boolean {
  return isModelLoaded && faceapi.nets.tinyFaceDetector.isLoaded
}

/**
 * Detect faces in a video frame.
 * @param input - HTMLCanvasElement (preferred) or ImageData of the frame
 * @param threshold - Minimum detection confidence (0-1)
 * @returns Array of face detections with bbox, confidence, and optional landmarks
 */
export async function detectFacesWithMediaPipe(
  input: HTMLCanvasElement | ImageData,
  threshold: number = 0.5
): Promise<Array<{
  bbox: [number, number, number, number] // [x, y, width, height]
  confidence: number
  landmarks?: Array<{ x: number; y: number }>
}>> {
  try {
    if (!isMediaPipeFaceLoaded()) {
      const loaded = await loadMediaPipeFaceDetector()
      if (!loaded) return []
    }

    // Resolve input to a canvas element (face-api accepts canvas or img)
    let canvasInput: HTMLCanvasElement

    if (input instanceof HTMLCanvasElement) {
      canvasInput = input
    } else {
      // ImageData fallback: draw onto a cached offscreen canvas
      canvasInput = getOffscreenCanvas(input.width, input.height)
      const ctx = canvasInput.getContext('2d')
      if (!ctx) return []
      ctx.putImageData(input, 0, 0)
    }

    // Detect all faces using TinyFaceDetector
    const detections = await faceapi.detectAllFaces(
      canvasInput,
      new faceapi.TinyFaceDetectorOptions({
        inputSize: 224, // Faster for real-time (160, 224, 320, 416, 512, 608)
        scoreThreshold: Math.max(threshold - 0.15, 0.3), // Slightly more permissive for webcam use
      })
    )

    // Convert to the expected format: {bbox, confidence, landmarks?}
    return detections.map((detection) => {
      const box = detection.box
      return {
        bbox: [
          box.x,
          box.y,
          box.width,
          box.height,
        ] as [number, number, number, number],
        confidence: detection.score,
        // TinyFaceDetector does not produce landmarks; callers handle undefined gracefully
        landmarks: undefined,
      }
    })
  } catch (error) {
    logWarn('Error in face-api face detection', error)
    return []
  }
}
