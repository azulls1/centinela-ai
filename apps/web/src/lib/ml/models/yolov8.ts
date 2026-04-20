/**
 * YOLOv8n via ONNX Runtime Web for object detection
 * Replaces COCO-SSD as primary detection model (~28% mAP vs ~22% mAP)
 * Falls back to COCO-SSD if ONNX model fails to load
 */

import * as ort from 'onnxruntime-web'

let session: ort.InferenceSession | null = null
let _isLoaded = false
let _loadPromise: Promise<boolean> | null = null

const INPUT_SIZE = 640

const COCO_CLASSES = [
  'person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus', 'train', 'truck',
  'boat', 'traffic light', 'fire hydrant', 'stop sign', 'parking meter', 'bench',
  'bird', 'cat', 'dog', 'horse', 'sheep', 'cow', 'elephant', 'bear', 'zebra',
  'giraffe', 'backpack', 'umbrella', 'handbag', 'tie', 'suitcase', 'frisbee',
  'skis', 'snowboard', 'sports ball', 'kite', 'baseball bat', 'baseball glove',
  'skateboard', 'surfboard', 'tennis racket', 'bottle', 'wine glass', 'cup',
  'fork', 'knife', 'spoon', 'bowl', 'banana', 'apple', 'sandwich', 'orange',
  'broccoli', 'carrot', 'hot dog', 'pizza', 'donut', 'cake', 'chair', 'couch',
  'potted plant', 'bed', 'dining table', 'toilet', 'tv', 'laptop', 'mouse',
  'remote', 'keyboard', 'cell phone', 'microwave', 'oven', 'toaster', 'sink',
  'refrigerator', 'book', 'clock', 'vase', 'scissors', 'teddy bear', 'hair drier',
  'toothbrush',
]

// ---------- Preprocessing ----------

interface PreprocessResult {
  tensor: Float32Array
  scale: number
  padX: number
  padY: number
}

function preprocessImage(canvas: HTMLCanvasElement, inputSize = INPUT_SIZE): PreprocessResult {
  const offscreen = document.createElement('canvas')
  offscreen.width = inputSize
  offscreen.height = inputSize
  const ctx = offscreen.getContext('2d')!

  // Letterbox: scale to fit, center, fill with gray (114)
  const scale = Math.min(inputSize / canvas.width, inputSize / canvas.height)
  const newW = Math.round(canvas.width * scale)
  const newH = Math.round(canvas.height * scale)
  const padX = Math.round((inputSize - newW) / 2)
  const padY = Math.round((inputSize - newH) / 2)

  ctx.fillStyle = 'rgb(114,114,114)'
  ctx.fillRect(0, 0, inputSize, inputSize)
  ctx.drawImage(canvas, padX, padY, newW, newH)

  const imageData = ctx.getImageData(0, 0, inputSize, inputSize)
  const { data } = imageData
  const pixels = inputSize * inputSize
  const tensor = new Float32Array(3 * pixels)

  // RGBA -> CHW RGB normalized [0, 1]
  for (let i = 0; i < pixels; i++) {
    tensor[i] = data[i * 4] / 255                   // R plane
    tensor[pixels + i] = data[i * 4 + 1] / 255      // G plane
    tensor[pixels * 2 + i] = data[i * 4 + 2] / 255  // B plane
  }

  return { tensor, scale, padX, padY }
}

// ---------- Postprocessing ----------

interface DetectionResult {
  label: string
  confidence: number
  bbox: { x: number; y: number; width: number; height: number }
}

function computeIoU(
  a: { x: number; y: number; width: number; height: number },
  b: { x: number; y: number; width: number; height: number },
): number {
  const x1 = Math.max(a.x, b.x)
  const y1 = Math.max(a.y, b.y)
  const x2 = Math.min(a.x + a.width, b.x + b.width)
  const y2 = Math.min(a.y + a.height, b.y + b.height)

  if (x2 <= x1 || y2 <= y1) return 0

  const intersection = (x2 - x1) * (y2 - y1)
  const union = a.width * a.height + b.width * b.height - intersection
  return union > 0 ? intersection / union : 0
}

function nms(candidates: DetectionResult[], iouThreshold: number): DetectionResult[] {
  // Sort by confidence descending
  candidates.sort((a, b) => b.confidence - a.confidence)

  // Group by class for per-class NMS
  const byClass = new Map<string, DetectionResult[]>()
  for (const c of candidates) {
    if (!byClass.has(c.label)) byClass.set(c.label, [])
    byClass.get(c.label)!.push(c)
  }

  const results: DetectionResult[] = []

  for (const [, group] of byClass) {
    const kept: DetectionResult[] = []
    for (const det of group) {
      let suppressed = false
      for (const k of kept) {
        if (computeIoU(det.bbox, k.bbox) >= iouThreshold) {
          suppressed = true
          break
        }
      }
      if (!suppressed) kept.push(det)
    }
    results.push(...kept)
  }

  return results
}

function postprocess(
  output: Float32Array,
  origWidth: number,
  origHeight: number,
  _inputSize: number,
  scale: number,
  padX: number,
  padY: number,
  confThreshold: number,
  nmsIouThreshold = 0.45,
): DetectionResult[] {
  const numClasses = 80
  const numDetections = 8400

  // YOLOv8 output: [1, 84, 8400]
  // Row layout: 0-3 = cx,cy,w,h  |  4-83 = class scores
  const candidates: DetectionResult[] = []

  for (let j = 0; j < numDetections; j++) {
    // Find best class
    let maxScore = -1
    let maxIdx = -1
    for (let i = 0; i < numClasses; i++) {
      const score = output[(4 + i) * numDetections + j]
      if (score > maxScore) {
        maxScore = score
        maxIdx = i
      }
    }

    if (maxScore < confThreshold) continue

    // Get bbox in letterboxed coordinates (center format)
    const cx = output[0 * numDetections + j]
    const cy = output[1 * numDetections + j]
    const w = output[2 * numDetections + j]
    const h = output[3 * numDetections + j]

    // Convert center -> corner
    let x = cx - w / 2
    let y = cy - h / 2

    // Reverse letterbox transform
    x = (x - padX) / scale
    y = (y - padY) / scale
    const bw = w / scale
    const bh = h / scale

    // Clamp to original image bounds
    const clampedX = Math.max(0, Math.min(x, origWidth))
    const clampedY = Math.max(0, Math.min(y, origHeight))
    const clampedW = Math.max(0, Math.min(bw, origWidth - clampedX))
    const clampedH = Math.max(0, Math.min(bh, origHeight - clampedY))

    candidates.push({
      label: COCO_CLASSES[maxIdx],
      confidence: maxScore,
      bbox: { x: clampedX, y: clampedY, width: clampedW, height: clampedH },
    })
  }

  return nms(candidates, nmsIouThreshold)
}

// ---------- Public API ----------

/**
 * Load YOLOv8n ONNX model
 * Tries WebGL first, falls back to WASM
 */
export async function loadYolov8Model(): Promise<boolean> {
  if (_isLoaded) return true
  if (_loadPromise) return _loadPromise

  _loadPromise = (async () => {
    try {
      // Enable WASM multi-threading + SIMD for ~3-4x speedup
      // Requires Cross-Origin-Opener-Policy: same-origin (set in vite.config.ts)
      ort.env.wasm.numThreads = Math.min(navigator.hardwareConcurrency || 4, 4)
      ort.env.wasm.proxy = false

      const modelUrl = '/models/yolov8n.onnx'
      const providers: ort.InferenceSession.ExecutionProviderConfig[] = ['wasm']

      // Try WebGPU if available (5-19x faster than WASM on supported GPUs)
      if (typeof navigator !== 'undefined' && 'gpu' in navigator) {
        try {
          const adapter = await (navigator as any).gpu?.requestAdapter()
          if (adapter) {
            providers.unshift('webgpu')
            console.log('[YOLOv8] WebGPU adapter found, will try WebGPU first')
          }
        } catch { /* WebGPU not available */ }
      }

      for (const provider of providers) {
        try {
          session = await ort.InferenceSession.create(modelUrl, {
            executionProviders: [provider],
          })
          console.log(`[YOLOv8] Model loaded with provider: ${provider}`)
          console.log(`[YOLOv8] Input names: ${session.inputNames}, Output names: ${session.outputNames}`)
          _isLoaded = true
          return true
        } catch (err) {
          console.warn(`[YOLOv8] Provider "${provider}" failed, trying next...`, err)
        }
      }

      console.warn('[YOLOv8] All providers failed, model not loaded')
      _loadPromise = null // Allow retry on failure
      return false
    } catch (error) {
      console.error('[YOLOv8] Error loading model:', error)
      _loadPromise = null // Allow retry on failure
      return false
    }
  })()

  return _loadPromise
}

/**
 * Run object detection using YOLOv8n
 */
export async function detectObjectsWithYolov8(
  canvas: HTMLCanvasElement,
  threshold = 0.5,
): Promise<DetectionResult[]> {
  if (!session) return []

  const { tensor, scale, padX, padY } = preprocessImage(canvas)

  const inputTensor = new ort.Tensor('float32', tensor, [1, 3, INPUT_SIZE, INPUT_SIZE])
  const inputName = session.inputNames[0]

  const results = await session.run({ [inputName]: inputTensor })
  const outputData = results[session.outputNames[0]].data as Float32Array

  return postprocess(
    outputData,
    canvas.width,
    canvas.height,
    INPUT_SIZE,
    scale,
    padX,
    padY,
    threshold,
  )
}

/**
 * Check if YOLOv8n model is loaded and ready
 */
export function isYolov8Loaded(): boolean {
  return _isLoaded && session !== null
}
