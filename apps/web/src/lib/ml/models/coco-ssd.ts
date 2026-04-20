/**
 * Integración de TensorFlow.js COCO-SSD para detección de objetos
 * Modelo pre-entrenado que detecta 80 clases de objetos COCO
 */

import * as tf from '@tensorflow/tfjs'
import '@tensorflow/tfjs-backend-webgl'
import '@tensorflow/tfjs-backend-cpu'
import * as cocoSsd from '@tensorflow-models/coco-ssd'
import { logDebug, logWarn, logError } from '../../../utils/logger'

let model: cocoSsd.ObjectDetection | null = null
let isModelLoaded = false
let _loadPromise: Promise<cocoSsd.ObjectDetection | null> | null = null

/**
 * Cargar modelo COCO-SSD
 * @returns Modelo cargado o null si hay error
 */
async function ensureTensorflowBackend() {
  await tf.ready()

  try {
    if (tf.getBackend() !== 'webgl') {
      await tf.setBackend('webgl')
    }
  } catch (error) {
    logWarn('⚠️ WebGL no disponible, usando backend CPU para TensorFlow.js', error)
    await tf.setBackend('cpu')
  }

  // Ajustar configuración para minimizar recreación de contextos WebGL
  try {
    tf.env().set('WEBGL_DELETE_TEXTURE_THRESHOLD', 0)
    tf.env().set('WEBGL_FLUSH_THRESHOLD', 0)
  } catch (error) {
    logDebug('No se pudo ajustar configuración WEBGL', error)
  }
}

export async function loadCocoSsdModel(): Promise<cocoSsd.ObjectDetection | null> {
  if (isModelLoaded && model) return model
  if (_loadPromise) return _loadPromise

  _loadPromise = (async () => {
    try {
      logDebug('📦 Cargando modelo COCO-SSD...')

      await ensureTensorflowBackend()

      // Cargar modelo COCO-SSD (lazy-loading)
      model = await cocoSsd.load({
        base: 'mobilenet_v2', // Usar MobileNet v2 (más rápido)
      })

      isModelLoaded = true
      logDebug('✅ Modelo COCO-SSD cargado exitosamente')
      return model
    } catch (error) {
      logError('❌ Error cargando modelo COCO-SSD', error)
      _loadPromise = null // Allow retry on failure
      return null
    }
  })()

  return _loadPromise
}

/**
 * Detectar objetos en una imagen usando COCO-SSD
 * @param canvas - Canvas con la imagen
 * @param threshold - Umbral de confianza (0-1)
 * @returns Array de objetos detectados
 */
export async function detectObjectsWithCocoSsd(
  canvas: HTMLCanvasElement,
  threshold: number = 0.5
): Promise<Array<{
  label: string
  confidence: number
  bbox: { x: number; y: number; width: number; height: number }
}>> {
  try {
    // Cargar modelo si no está cargado
    const loadedModel = await loadCocoSsdModel()
    if (!loadedModel) {
      logWarn('Modelo COCO-SSD no disponible')
      return []
    }

    // Ejecutar detección
    const predictions = await loadedModel.detect(canvas, undefined, threshold)

    // Convertir a formato esperado
    return predictions.map(pred => ({
      label: pred.class,
      confidence: pred.score,
      bbox: {
        x: pred.bbox[0],
        y: pred.bbox[1],
        width: pred.bbox[2],
        height: pred.bbox[3],
      },
    }))
  } catch (error) {
    logError('Error en detección COCO-SSD', error)
    return []
  }
}

/**
 * Verificar si el modelo está cargado
 */
export function isCocoSsdLoaded(): boolean {
  return isModelLoaded && model !== null
}

