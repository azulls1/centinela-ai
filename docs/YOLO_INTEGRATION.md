# 🎯 Guía de Integración de YOLO Real

Esta guía explica cómo integrar detección de objetos YOLO real en el navegador usando `onnxruntime-web`.

## 📋 Prerequisitos

1. **Modelo YOLO ONNX**: Necesitas un modelo YOLOv8n o YOLO11n convertido a formato ONNX
2. **onnxruntime-web**: Ya está en las dependencias del proyecto
3. **CDN o servidor**: Para servir el modelo ONNX (recomendado: ~6-10 MB)

## 🚀 Pasos de Implementación

### 1. Obtener Modelo YOLO ONNX

Puedes usar modelos pre-convertidos o convertir uno tú mismo:

**Opción A: Descargar modelo pre-convertido**
```bash
# YOLOv8n (nano - más rápido, menos preciso)
wget https://github.com/ultralytics/assets/releases/download/v8.2.0/yolov8n.onnx

# YOLO11n (última versión)
# Descargar desde: https://github.com/ultralytics/ultralytics
```

**Opción B: Convertir modelo YOLO a ONNX**
```python
from ultralytics import YOLO

# Cargar modelo YOLO
model = YOLO('yolov8n.pt')  # o yolov11n.pt

# Exportar a ONNX
model.export(format='onnx', imgsz=640)
```

### 2. Almacenar el Modelo

Coloca el modelo en `apps/web/public/models/yolov8n.onnx` o súbelo a un CDN.

### 3. Implementar Carga del Modelo

Actualiza `apps/web/src/lib/ml/processors.ts`:

```typescript
import * as ort from 'onnxruntime-web'

let yoloModel: ort.InferenceSession | null = null
const MODEL_URL = '/models/yolov8n.onnx' // o URL del CDN

async function loadYOLOModel() {
  if (yoloModel) return yoloModel
  
  try {
    // Configurar ort para usar WebAssembly (más rápido)
    ort.env.wasm.numThreads = 1
    ort.env.wasm.simd = true
    
    // Cargar modelo
    yoloModel = await ort.InferenceSession.create(MODEL_URL, {
      executionProviders: ['wasm'], // o 'webgpu' si está disponible
    })
    
    console.log('Modelo YOLO cargado exitosamente')
    return yoloModel
  } catch (error) {
    console.error('Error cargando modelo YOLO:', error)
    throw error
  }
}
```

### 4. Preprocesar Frame

```typescript
function preprocessFrame(
  canvas: HTMLCanvasElement, 
  targetSize: number = 640
): Float32Array {
  // Crear canvas temporal para redimensionar
  const tempCanvas = document.createElement('canvas')
  tempCanvas.width = targetSize
  tempCanvas.height = targetSize
  const tempCtx = tempCanvas.getContext('2d')!
  
  // Dibujar frame redimensionado manteniendo aspect ratio
  const scale = Math.min(targetSize / canvas.width, targetSize / canvas.height)
  const x = (targetSize - canvas.width * scale) / 2
  const y = (targetSize - canvas.height * scale) / 2
  
  tempCtx.drawImage(
    canvas, 
    x, y, 
    canvas.width * scale, 
    canvas.height * scale
  )
  
  // Obtener imagen data
  const imageData = tempCtx.getImageData(0, 0, targetSize, targetSize)
  const data = imageData.data
  
  // Convertir RGB a tensor normalizado [0, 1]
  const tensor = new Float32Array(3 * targetSize * targetSize)
  
  for (let i = 0; i < data.length; i += 4) {
    const pixelIndex = i / 4
    // YOLO espera RGB normalizado y formato CHW (Channel, Height, Width)
    tensor[pixelIndex] = data[i] / 255.0     // R
    tensor[pixelIndex + targetSize * targetSize] = data[i + 1] / 255.0     // G
    tensor[pixelIndex + 2 * targetSize * targetSize] = data[i + 2] / 255.0 // B
  }
  
  return tensor
}
```

### 5. Ejecutar Inferencia

```typescript
async function runYOLOInference(
  model: ort.InferenceSession,
  preprocessedTensor: Float32Array,
  inputSize: number = 640
): Promise<Float32Array> {
  // Crear tensor de entrada
  const tensor = new ort.Tensor('float32', preprocessedTensor, [1, 3, inputSize, inputSize])
  
  // Ejecutar inferencia
  const feeds = { [model.inputNames[0]]: tensor }
  const results = await model.run(feeds)
  
  // Obtener salida (normalmente 'output0' o el primer output)
  const output = results[model.outputNames[0]]
  
  return output.data as Float32Array
}
```

### 6. Post-procesar Resultados (NMS + Decodificación)

```typescript
interface Detection {
  x: number
  y: number
  width: number
  height: number
  confidence: number
  classId: number
  className: string
}

function postProcessYOLO(
  output: Float32Array,
  canvasWidth: number,
  canvasHeight: number,
  inputSize: number = 640,
  confThreshold: number = 0.5,
  iouThreshold: number = 0.45
): Detection[] {
  const detections: Detection[] = []
  const scaleX = canvasWidth / inputSize
  const scaleY = canvasHeight / inputSize
  
  // YOLO output: [batch, num_detections, 85]
  // 85 = 4 (bbox) + 1 (objectness) + 80 (classes)
  const numDetections = output.length / 85
  
  for (let i = 0; i < numDetections; i++) {
    const offset = i * 85
    
    // Bounding box (center_x, center_y, width, height) - normalizado [0,1]
    const centerX = output[offset] * scaleX
    const centerY = output[offset + 1] * scaleY
    const width = output[offset + 2] * scaleX
    const height = output[offset + 3] * scaleY
    
    // Objectness score
    const objectness = output[offset + 4]
    
    // Class probabilities
    let maxClassProb = 0
    let maxClassId = 0
    for (let j = 0; j < 80; j++) {
      const classProb = output[offset + 5 + j]
      if (classProb > maxClassProb) {
        maxClassProb = classProb
        maxClassId = j
      }
    }
    
    // Confidence = objectness * class_probability
    const confidence = objectness * maxClassProb
    
    if (confidence >= confThreshold) {
      detections.push({
        x: centerX - width / 2,
        y: centerY - height / 2,
        width,
        height,
        confidence,
        classId: maxClassId,
        className: COCO_CLASSES[maxClassId] || 'unknown'
      })
    }
  }
  
  // Aplicar Non-Maximum Suppression (NMS)
  return applyNMS(detections, iouThreshold)
}

function applyNMS(detections: Detection[], iouThreshold: number): Detection[] {
  // Ordenar por confianza
  detections.sort((a, b) => b.confidence - a.confidence)
  
  const kept: Detection[] = []
  
  while (detections.length > 0) {
    // Tomar la detección con mayor confianza
    const best = detections.shift()!
    kept.push(best)
    
    // Eliminar detecciones con alto IOU
    detections = detections.filter(det => {
      const iou = calculateIOU(best, det)
      return iou < iouThreshold || det.classId !== best.classId
    })
  }
  
  return kept
}

function calculateIOU(box1: Detection, box2: Detection): number {
  const x1 = Math.max(box1.x, box2.x)
  const y1 = Math.max(box1.y, box2.y)
  const x2 = Math.min(box1.x + box1.width, box2.x + box2.width)
  const y2 = Math.min(box1.y + box1.height, box2.y + box2.height)
  
  if (x2 < x1 || y2 < y1) return 0
  
  const intersection = (x2 - x1) * (y2 - y1)
  const area1 = box1.width * box1.height
  const area2 = box2.width * box2.height
  const union = area1 + area2 - intersection
  
  return union > 0 ? intersection / union : 0
}
```

### 7. Integrar en detectObjects()

Reemplaza la función `detectObjects()` actual:

```typescript
async function detectObjects(
  canvas: HTMLCanvasElement, 
  threshold: number,
  currentDetections?: Partial<DetectionState['detections']>
) {
  try {
    // Cargar modelo si no está cargado
    const model = await loadYOLOModel()
    
    // Preprocesar frame
    const preprocessed = preprocessFrame(canvas, 640)
    
    // Ejecutar inferencia
    const output = await runYOLOInference(model, preprocessed, 640)
    
    // Post-procesar resultados
    const detections = postProcessYOLO(
      output,
      canvas.width,
      canvas.height,
      640,
      threshold,
      0.45 // IOU threshold para NMS
    )
    
    // Convertir al formato esperado
    return detections.map(det => ({
      label: det.className,
      confidence: det.confidence,
      bbox: {
        x: det.x,
        y: det.y,
        width: det.width,
        height: det.height
      }
    }))
  } catch (error) {
    console.error('Error en detección YOLO:', error)
    // Fallback a simulación si hay error
    return []
  }
}
```

### 8. Actualizar loadModels()

```typescript
export async function loadModels() {
  if (modelsLoaded) return
  
  try {
    console.log('Cargando modelos de ML...')
    
    // Cargar YOLO en segundo plano
    await loadYOLOModel()
    
    // Cargar otros modelos (MediaPipe, etc.)
    // ...
    
    modelsLoaded = true
    console.log('Modelos cargados exitosamente')
  } catch (error) {
    console.error('Error cargando modelos:', error)
    modelsLoaded = true // Permitir que la app continúe
  }
}
```

## 📊 Optimizaciones

### Rendimiento

1. **Usar WebGPU** (si está disponible):
   ```typescript
   executionProviders: ['webgpu', 'wasm']
   ```

2. **Reducir resolución de entrada**:
   - 640x640: Balance velocidad/precisión (recomendado)
   - 416x416: Más rápido, menos preciso
   - 320x320: Muy rápido, baja precisión

3. **Throttling de inferencias**:
   - Ejecutar YOLO cada 2-3 frames en lugar de cada frame
   - Usar el tracking para mantener detecciones entre frames

### Precisión

1. **Ajustar umbrales**:
   - `confThreshold`: 0.5 (default), aumentar para menos falsos positivos
   - `iouThreshold`: 0.45 (default), ajustar según necesidad

2. **Filtrado post-procesamiento**:
   - Ya implementado: `filterFalsePositives()`
   - Tracking con persistencia temporal

## 🔗 Recursos

- [ONNX Runtime Web Docs](https://onnxruntime.ai/docs/tutorials/web/)
- [Ultralytics YOLO](https://github.com/ultralytics/ultralytics)
- [YOLOv8 Documentation](https://docs.ultralytics.com/)
- [COCO Dataset Classes](https://cocodataset.org/#explore)

## ⚠️ Notas Importantes

1. **Tamaño del modelo**: YOLOv8n es ~6MB, YOLOv8s es ~22MB
2. **Rendimiento**: Espera ~30-60 FPS en hardware moderno con YOLOv8n
3. **Compatibilidad**: WebAssembly funciona en todos los navegadores modernos
4. **WebGPU**: Solo disponible en navegadores compatibles (Chrome 113+, Edge 113+)

## ✅ Estado Actual

- ✅ Sistema de tracking con persistencia implementado
- ✅ Filtrado de falsos positivos
- ✅ Estabilización temporal
- ⏳ Detección YOLO real (pendiente de implementar según esta guía)


