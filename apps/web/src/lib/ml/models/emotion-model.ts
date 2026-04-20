/**
 * ML-based Emotion Detection using FaceExpressionNet from @vladmandic/face-api
 *
 * Replaces the previous geometric heuristic with a real CNN classifier.
 * The model is a lightweight MobileNet-based network (~330KB, quantized)
 * trained on FER2013+ data that classifies 7 basic emotions:
 *   neutral, happy, sad, angry, fearful, disgusted, surprised
 *
 * The model weights are served from /models/face-expression/ and loaded
 * once on first use. Inference runs entirely in the browser via TF.js.
 */

import { nets, type FaceExpressions } from '@vladmandic/face-api/dist/face-api.esm-nobundle.js'
import { logDebug, logError, logWarn } from '../../../utils/logger'
import type { EmotionType } from '../../../types'

// ── State ──────────────────────────────────────────────────────────

let isModelLoaded = false
let _loadPromise: Promise<boolean> | null = null

// Reusable canvas for cropping face regions
let cropCanvas: HTMLCanvasElement | null = null
let cropCtx: CanvasRenderingContext2D | null = null

// The FaceExpressionNet expects 136x136 input (its internal resize handles
// other sizes, but providing a reasonably sized crop is more efficient).
const CROP_SIZE = 136

// ── Public API ─────────────────────────────────────────────────────

/**
 * Load the FaceExpressionNet model weights.
 * Safe to call multiple times; loads only once.
 */
export async function loadEmotionModel(): Promise<boolean> {
  if (isModelLoaded) return true
  if (_loadPromise) return _loadPromise

  _loadPromise = (async () => {
    try {
      logDebug('Loading FaceExpressionNet model...')

      // Model weights are served from the Vite public directory.
      // In both dev and production, the public dir is at the root path.
      const modelUrl = '/models/face-expression'

      await nets.faceExpressionNet.loadFromUri(modelUrl)

      isModelLoaded = true
      logDebug('FaceExpressionNet loaded successfully (~330 KB)')
      return true
    } catch (error) {
      logError('Failed to load FaceExpressionNet', error)
      _loadPromise = null // Allow retry on failure
      return false
    }
  })()

  return _loadPromise
}

/**
 * Check whether the emotion model is ready for inference.
 */
export function isEmotionModelLoaded(): boolean {
  return isModelLoaded && nets.faceExpressionNet.isLoaded
}

/**
 * The 7 expression labels produced by FaceExpressionNet, in the order they
 * map to the softmax output.
 */
export type FaceApiExpression =
  | 'neutral'
  | 'happy'
  | 'sad'
  | 'angry'
  | 'fearful'
  | 'disgusted'
  | 'surprised'

export interface EmotionPrediction {
  /** Best-matching EmotionType for the app */
  emotion: EmotionType
  /** Probability of the top expression (0-1) */
  confidence: number
  /** Full probability distribution from the model */
  raw: Record<FaceApiExpression, number>
}

/**
 * Classify the emotion for a single face crop.
 *
 * @param sourceCanvas  The full-frame canvas (same one used by MediaPipe).
 * @param faceBbox      Bounding box of the face as [x, y, width, height] in
 *                      pixel coordinates of `sourceCanvas`.
 * @param threshold     Minimum confidence to accept a prediction.
 * @returns An EmotionPrediction, or null if below threshold / model not ready.
 */
export async function classifyEmotion(
  sourceCanvas: HTMLCanvasElement,
  faceBbox: [number, number, number, number],
  threshold: number = 0.3,
): Promise<EmotionPrediction | null> {
  if (!isEmotionModelLoaded()) return null

  const [fx, fy, fw, fh] = faceBbox
  if (fw <= 0 || fh <= 0) return null

  // ── Crop the face region into a small canvas ──
  if (!cropCanvas) {
    cropCanvas = document.createElement('canvas')
    cropCanvas.width = CROP_SIZE
    cropCanvas.height = CROP_SIZE
    cropCtx = cropCanvas.getContext('2d')
  }
  if (!cropCtx) return null

  // Add a small margin around the face for better classification
  const margin = Math.max(fw, fh) * 0.15
  const sx = Math.max(0, fx - margin)
  const sy = Math.max(0, fy - margin)
  const sw = Math.min(sourceCanvas.width - sx, fw + margin * 2)
  const sh = Math.min(sourceCanvas.height - sy, fh + margin * 2)

  cropCtx.clearRect(0, 0, CROP_SIZE, CROP_SIZE)
  cropCtx.drawImage(sourceCanvas, sx, sy, sw, sh, 0, 0, CROP_SIZE, CROP_SIZE)

  // ── Run inference ──
  try {
    const result: FaceExpressions | FaceExpressions[] =
      await nets.faceExpressionNet.predictExpressions(cropCanvas)

    // predictExpressions may return an array if given multiple inputs;
    // we always pass a single canvas so take the first result.
    const expressions: FaceExpressions = Array.isArray(result) ? result[0] : result
    if (!expressions) return null

    const sorted = expressions.asSortedArray()
    if (sorted.length === 0) return null

    const top = sorted[0]
    if (top.probability < threshold) return null

    // Build raw probability map
    const raw: Record<FaceApiExpression, number> = {
      neutral: expressions.neutral,
      happy: expressions.happy,
      sad: expressions.sad,
      angry: expressions.angry,
      fearful: expressions.fearful,
      disgusted: expressions.disgusted,
      surprised: expressions.surprised,
    }

    return {
      emotion: mapToEmotionType(top.expression, sorted),
      confidence: top.probability,
      raw,
    }
  } catch (error) {
    logWarn('Emotion classification failed for face crop', error)
    return null
  }
}

// ── Internal helpers ───────────────────────────────────────────────

/**
 * Map a face-api expression label to the app's EmotionType.
 *
 * The app defines an extra type `focused` which has no direct model output.
 * We approximate it: when the top expression is `neutral` with moderate
 * confidence AND there is very low probability for all other expressions,
 * we label it `focused` (indicating attentive engagement without strong affect).
 */
function mapToEmotionType(
  topExpression: string,
  sorted: { expression: string; probability: number }[],
): EmotionType {
  // Direct 1:1 mappings
  const directMap: Record<string, EmotionType> = {
    happy: 'happy',
    sad: 'sad',
    angry: 'angry',
    surprised: 'surprised',
    fearful: 'fearful',
    disgusted: 'disgusted',
    neutral: 'neutral',
  }

  const mapped = directMap[topExpression]
  if (!mapped) return 'neutral'

  // Heuristic for 'focused': neutral with high confidence and very little
  // competition from emotional expressions.
  if (mapped === 'neutral' && sorted.length >= 2) {
    const topProb = sorted[0].probability
    const secondProb = sorted[1].probability
    // If neutral dominates strongly (>0.65) and the runner-up is very low,
    // the person is likely calmly attentive rather than expressionless.
    if (topProb > 0.65 && secondProb < 0.12) {
      return 'focused'
    }
  }

  return mapped
}
