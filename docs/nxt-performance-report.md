# NXT Performance Report - Vision Human Insight

> **Fecha:** 2026-04-05
> **Agente:** NXT Performance v3.8.0
> **Proyecto:** vision-human-insight (apps/web)
> **Score General:** 38/100 (CRITICO)

---

## Resumen Ejecutivo

El frontend de Vision Human Insight presenta problemas de rendimiento severos que impactan directamente la experiencia de usuario. El bundle JS de **3,326 kB** excede el presupuesto recomendado de 200 kB (gzipped) en mas de 16x. La causa principal es la inclusion monolitica de TensorFlow.js, COCO-SSD, MediaPipe y ONNX Runtime sin code splitting de rutas ni separacion adecuada de chunks. Adicionalmente, la arquitectura de procesamiento ML corre en el hilo principal, bloqueando la interactividad durante la inferencia de modelos.

---

## 1. Bundle Size (CRITICO - 3,326 kB JS)

### Diagnostico

El build produce un unico chunk JS de ~3,326 kB sin gzip. Las dependencias pesadas son:

| Paquete | Tamano estimado (sin gzip) | Impacto |
|---------|---------------------------|---------|
| `@tensorflow/tfjs` + backends | ~1,800 kB | CRITICO - se carga al inicio |
| `@tensorflow-models/coco-ssd` | ~200 kB | ALTO - modelo + wrappers |
| `@mediapipe/tasks-vision` | ~400 kB | ALTO - WASM + JS bindings |
| `onnxruntime-web` | ~300 kB | ALTO - incluido aunque se excluye de optimizeDeps |
| `framer-motion` | ~140 kB | MEDIO - animaciones en toda la app |
| `recharts` | ~200 kB | MEDIO - solo usado en DashboardPage |
| `hls.js` | ~60 kB | BAJO - necesario para streams externos |
| `@supabase/supabase-js` | ~50 kB | BAJO |
| `lucide-react` | ~30 kB (tree-shaken) | BAJO |

### Hallazgos

1. **Sin code splitting de rutas**: `App.tsx` importa `LivePage`, `DashboardPage`, `SettingsPage` y `AdminPage` de forma estatica. Todas las paginas y sus dependencias (incluyendo `recharts` en Dashboard) se cargan al inicio.

2. **TensorFlow.js es monolitico**: `coco-ssd.ts` hace `import * as tf from '@tensorflow/tfjs'` y `import '@tensorflow/tfjs-backend-webgl'` de forma estatica. Esto fuerza la inclusion de todo TensorFlow en el bundle inicial, incluso antes de que el usuario active una camara.

3. **MediaPipe se importa estaticamente**: Tanto `mediapipe-face.ts` como `mediapipe-pose.ts` importan `@mediapipe/tasks-vision` al nivel superior del modulo. Aunque los modelos .tflite se cargan desde CDN, el runtime JS entra en el bundle.

4. **ONNX Runtime incluido innecesariamente**: `onnxruntime-web` esta en `dependencies` de package.json y aunque se excluye de `optimizeDeps` en vite.config.ts, sigue siendo empaquetado si algun modulo lo importa (actualmente no parece usarse directamente, pero esta en el bundle).

5. **Vite sin configuracion de chunks**: `vite.config.ts` no tiene `build.rollupOptions.output.manualChunks`, lo que significa que Vite decide la estrategia de splitting automaticamente, generando un bundle monolitico.

### Recomendaciones

```typescript
// vite.config.ts - Agregar code splitting
export default defineConfig({
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          'vendor-react': ['react', 'react-dom', 'react-router-dom'],
          'vendor-ui': ['framer-motion', 'lucide-react'],
          'vendor-charts': ['recharts'],
          'vendor-supabase': ['@supabase/supabase-js'],
          'ml-tensorflow': ['@tensorflow/tfjs', '@tensorflow-models/coco-ssd'],
          'ml-mediapipe': ['@mediapipe/tasks-vision'],
          'hls': ['hls.js'],
        },
      },
    },
    target: 'esnext',
    minify: 'terser',
    terserOptions: {
      compress: { drop_console: true, drop_debugger: true },
    },
  },
})
```

```typescript
// App.tsx - Lazy loading de rutas
import { lazy, Suspense } from 'react'

const LivePage = lazy(() => import('./pages/LivePage'))
const DashboardPage = lazy(() => import('./pages/DashboardPage'))
const SettingsPage = lazy(() => import('./pages/SettingsPage'))
const AdminPage = lazy(() => import('./pages/AdminPage'))

// En Routes:
<Suspense fallback={<PageSkeleton />}>
  <Routes>
    <Route path="/" element={<LivePage />} />
    <Route path="/dashboard" element={<DashboardPage />} />
    {/* ... */}
  </Routes>
</Suspense>
```

**Impacto estimado**: Reduccion del bundle inicial de 3,326 kB a ~400-500 kB (carga inicial), con lazy loading de ML (~2,400 kB) y recharts (~200 kB) bajo demanda. Mejora LCP en ~2-3 segundos.

---

## 2. ML Model Loading y Processing

### Diagnostico

| Aspecto | Estado | Evaluacion |
|---------|--------|------------|
| Lazy loading de modelos | Parcial (dynamic import en CameraFeed) | MEDIO |
| Web Workers | No implementado | CRITICO |
| Canvas de procesamiento | 320x240 (reducido) | OK |
| Throttling entre frames | 800ms minimo + adaptive | OK |
| yield a main thread | Si (via setTimeout) | INSUFICIENTE |

### Hallazgos

1. **Sin Web Workers**: Todo el procesamiento ML (COCO-SSD, MediaPipe Face, MediaPipe Pose) corre en el hilo principal. `processFrame()` en `processors.ts` ejecuta secuencialmente: detectPersons -> detectFaces -> detectEmotions -> detectMovement -> detectObjects, con `yieldToMainThread()` entre cada paso. Sin embargo, cada `await` de inferencia (ej. `loadedModel.detect(canvas)`) bloquea el main thread por 50-200ms por modelo, causando jank visible.

2. **Modelo cargado eagerly en LivePage**: `LivePage.tsx` linea 260 llama `loadModels()` despues de iniciar sesion, lo cual es correcto para UX. Sin embargo, `loadModels()` carga los 3 modelos en paralelo (`Promise.allSettled`), lo que puede bloquear el main thread por 3-8 segundos durante la inicializacion de TensorFlow.js + WebGL context.

3. **Canvas snapshot creado en cada frame ML**: En `CameraFeed.tsx` linea 607, se crea un `document.createElement('canvas')` en cada ciclo de procesamiento ML. Esto genera garbage collection frecuente. El canvas deberia reutilizarse.

4. **MediaPipe delegado a CPU**: Tanto `mediapipe-face.ts` como `mediapipe-pose.ts` usan `delegate: 'CPU'` en lugar de `'GPU'`. Esto fue hecho por estabilidad, pero impacta el rendimiento significativamente. Se deberia intentar GPU con fallback a CPU.

5. **Adaptive ML interval bien implementado**: El sistema en `CameraFeed.tsx` ajusta el intervalo de procesamiento ML (900ms-4500ms) basandose en FPS. Si FPS < 24, aumenta el intervalo; si FPS > 48, lo reduce. Este patron es correcto.

### Recomendaciones

**Prioridad MAXIMA: Mover inferencia ML a Web Worker**

```typescript
// ml-worker.ts
self.onmessage = async (event) => {
  const { imageData, config, cameraId } = event.data
  const detections = await processFrameInWorker(imageData, config, cameraId)
  self.postMessage({ cameraId, detections })
}
```

```typescript
// En CameraFeed.tsx - usar OffscreenCanvas + Worker
const worker = new Worker(new URL('../lib/ml/ml-worker.ts', import.meta.url), { type: 'module' })
// Enviar ImageData al worker en lugar de procesar en main thread
```

**Prioridad ALTA: Reutilizar canvas de snapshot**

```typescript
// Mover fuera del loop de procesamiento
const snapshotCanvasRef = useRef<HTMLCanvasElement>(document.createElement('canvas'))
snapshotCanvasRef.current.width = 320
snapshotCanvasRef.current.height = 240
```

**Impacto estimado**: Mover ML a Web Workers elimina bloqueos de 100-400ms en el main thread por ciclo, mejorando INP de ~500ms (pobre) a <100ms (bueno).

---

## 3. Camera Feed Rendering Performance

### Diagnostico

| Aspecto | Estado | Evaluacion |
|---------|--------|------------|
| requestAnimationFrame loop | Si | OK |
| Canvas 2D con alpha:false | Si | OK |
| desynchronized hint | Si | OK |
| willReadFrequently:false (render) | Si | OK |
| Canvas resize detection | Si (compara video dimensions) | OK |
| FPS tracking | Si (cada 1000ms) | OK |
| Video hidden + canvas visible | Si | OK |

### Hallazgos

1. **Render loop eficiente**: `startRenderLoop()` en `CameraFeed.tsx` usa `requestAnimationFrame` correctamente con early return para video pausado/ended/no listo. El canvas se configura con `{ alpha: false, desynchronized: true, willReadFrequently: false }`, que son las mejores opciones para rendering de video.

2. **drawOverlays optimizado**: El metodo de dibujo de overlays guarda y restaura el estado del contexto, y usa un loop `for` en lugar de `.forEach()` para mejor rendimiento. Las cadenas de color se calculan inline, lo cual es aceptable.

3. **Posible mejora con OffscreenCanvas**: Si el navegador soporta `OffscreenCanvas`, el rendering del video + overlays podria moverse a un segundo thread, liberando el main thread completamente.

4. **FPS update causa re-render innecesario**: `updateCameraDetection(cameraId, { currentFPS: fps })` se llama cada segundo desde el render loop. Esto dispara un setState en el store de Zustand que causa re-renders en LivePage y todos los componentes que consumen `cameraDetections`. Ver seccion 4.

5. **Visibility API bien implementada**: El componente pausa el video y detiene el render loop cuando la pagina no es visible, y reanuda al volver. Esto ahorra CPU/GPU cuando el tab esta en segundo plano.

### Recomendaciones

- Considerar `OffscreenCanvas` para separar rendering del main thread
- Desacoplar el update de FPS del store (usar ref local + display component separado)
- Batch overlay drawing cuando hay muchos objetos (>10)

---

## 4. Zustand Store Efficiency

### Diagnostico

| Aspecto | Estado | Evaluacion |
|---------|--------|------------|
| Selectores granulares | Parcial | NECESITA MEJORA |
| Re-renders por detection update | Excesivos | ALTO |
| Memoizacion de computed values | Parcial | MEDIO |

### Hallazgos

1. **CRITICO - updateCameraDetection recomputa todo**: Cada vez que se llama `updateCameraDetection()` (cada ~1-4 segundos por camara activa), el store recomputa `aggregatedDetections` y `detectionState` llamando `computeAggregatedDetections()` y `computeLegacyDetectionState()`. Ademas, evalua el auto-performance management. Esto genera un nuevo objeto de estado que fuerza re-renders en todos los consumidores.

2. **LivePage consume demasiados slices**: En `LivePage.tsx`, se seleccionan 6+ slices individuales del store:
   ```typescript
   const detectionState = useAppStore((state) => state.detectionState)
   const aggregatedDetections = useAppStore((state) => state.aggregatedDetections)
   const cameraDetections = useAppStore((state) => state.cameraDetections)
   const activeCameraIds = useAppStore((state) => state.activeCameraIds)
   const cameraConfigs = useAppStore((state) => state.cameraConfigs)
   ```
   Cada uno de estos genera una suscripcion independiente, y dado que `updateCameraDetection` genera nuevas referencias para `cameraDetections`, `aggregatedDetections` y `detectionState` simultaneamente, LivePage se re-renderiza hasta 3 veces por update.

3. **sessionInfo selector crea objeto nuevo cada render**:
   ```typescript
   const { sessionInfo, setSessionInfo, ... } = useAppStore((state) => ({
     sessionInfo: state.sessionInfo,
     setSessionInfo: state.setSessionInfo,
     ...
   }))
   ```
   Este patron crea un nuevo objeto en cada llamada al selector, causando re-renders innecesarios. Se debe usar `useShallow` de zustand o selectores individuales.

4. **useMemo triviales**: En `LivePage.tsx`:
   ```typescript
   const personsCount = useMemo(() => aggregatedDetections.totalPersons, [aggregatedDetections.totalPersons])
   ```
   Esto no aporta nada ya que `aggregatedDetections.totalPersons` es un numero primitivo; la comparacion es igual de costosa que la memorizacion.

### Recomendaciones

```typescript
// 1. Usar useShallow para selectores de objetos
import { useShallow } from 'zustand/react/shallow'

const { sessionInfo, setSessionInfo } = useAppStore(
  useShallow((state) => ({
    sessionInfo: state.sessionInfo,
    setSessionInfo: state.setSessionInfo,
  }))
)

// 2. Separar FPS del detection update (evitar recomputar aggregated)
// Crear un store separado para FPS o usar refs

// 3. Eliminar useMemo triviales para primitivos
const personsCount = aggregatedDetections.totalPersons

// 4. Batch detection updates con unstable_batchedUpdates o microtask
```

**Impacto estimado**: Reduccion de re-renders de ~15-20/segundo a ~3-5/segundo con 3 camaras activas.

---

## 5. Vite Configuration Optimization

### Diagnostico

El archivo `vite.config.ts` actual es minimalista:

```typescript
export default defineConfig({
  plugins: [react()],
  resolve: { alias: { '@': path.resolve(__dirname, './src') } },
  server: { port: 5173, host: true },
  optimizeDeps: { exclude: ['onnxruntime-web'] },
})
```

### Hallazgos Criticos

1. **Sin configuracion de build**: No hay `build.rollupOptions`, `build.target`, `build.minify`, ni `build.chunkSizeWarningLimit`.

2. **Sin code splitting manual**: Sin `manualChunks`, Vite/Rollup genera un solo chunk vendor + un solo chunk de app, resultando en el bundle de 3,326 kB.

3. **Sin compresion**: No se usa `vite-plugin-compression` para generar assets gzipped/brotli.

4. **Sin analisis de bundle**: No hay `rollup-plugin-visualizer` configurado.

5. **onnxruntime-web excluido de optimizeDeps pero no del bundle**: La exclusion de `optimizeDeps` solo afecta el pre-bundling de desarrollo, no el build de produccion. Si algun modulo lo importa, seguira en el bundle final.

### Recomendacion Completa

```typescript
import { defineConfig, type PluginOption } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: { '@': path.resolve(__dirname, './src') },
  },
  server: { port: 5173, host: true },
  optimizeDeps: {
    exclude: ['onnxruntime-web'],
  },
  build: {
    target: 'esnext',
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true,
        drop_debugger: true,
      },
    },
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (id.includes('node_modules')) {
            if (id.includes('react') || id.includes('react-dom') || id.includes('react-router')) {
              return 'vendor-react'
            }
            if (id.includes('@tensorflow') || id.includes('coco-ssd')) {
              return 'ml-tensorflow'
            }
            if (id.includes('@mediapipe')) {
              return 'ml-mediapipe'
            }
            if (id.includes('recharts') || id.includes('d3-')) {
              return 'vendor-charts'
            }
            if (id.includes('framer-motion')) {
              return 'vendor-motion'
            }
            if (id.includes('hls.js')) {
              return 'vendor-hls'
            }
            if (id.includes('@supabase')) {
              return 'vendor-supabase'
            }
            if (id.includes('onnxruntime')) {
              return 'ml-onnx'
            }
          }
        },
      },
    },
    chunkSizeWarningLimit: 500,
  },
})
```

---

## 6. Auto-Performance Management System

### Diagnostico

| Aspecto | Estado | Evaluacion |
|---------|--------|------------|
| Presets definidos | 3 (performance/balanced/quality) | OK |
| Auto-adjustment | Si, basado en FPS promedio | OK |
| Cooldown entre ajustes | 6s (downgrade) / 12s (upgrade) | OK |
| Modelo toggle per-camera | Si | OK |

### Hallazgos

1. **Bien disenado**: El sistema de auto-performance en `appStore.ts` (lineas 736-792) monitorea `averageFPS` y ajusta automaticamente:
   - FPS < 18 por >6s: baja al preset inferior (ej. balanced -> performance)
   - FPS > 36 por >12s: sube al preset superior (ej. balanced -> quality)

2. **Cooldown asimetrico correcto**: El downgrade es mas agresivo (6s) que el upgrade (12s), lo cual es el patron correcto para evitar oscilaciones.

3. **Presets afectan resolucion, FPS y modelos activos**: El preset `performance` desactiva emotionDetection y objectDetection, y baja a 360x240@20fps. Esto es agresivo pero efectivo.

4. **Potencial problema**: El auto-adjustment corre dentro de `updateCameraDetection`, que ya es la funcion mas llamada del store. Podria moverse a un efecto separado con debounce para reducir la carga computacional del store update.

### Recomendacion

Extraer la logica de auto-performance a un hook o efecto independiente con `setInterval` de 5 segundos, en lugar de evaluarla en cada detection update.

---

## 7. Memory Leaks

### Diagnostico

| Componente | Cleanup | Evaluacion |
|------------|---------|------------|
| CameraFeed - render loop | cancelAnimationFrame en cleanup | OK |
| CameraFeed - ML timers | clearTimeout + cancelIdleCallback | OK |
| CameraFeed - MediaStream | tracks.stop() en cleanup | OK |
| CameraFeed - HLS | hls.destroy() en cleanup | OK |
| CameraFeed - event listeners | removeEventListener en cleanup | OK |
| CameraFeed - visibility handler | removeEventListener | OK |
| LivePage - heartbeat interval | clearInterval en cleanup | OK |
| LivePage - save event timeouts | clearTimeout en cleanup | OK |
| LivePage - model loading | cancelled flag | OK |
| processors.ts - cameraStates Map | resetCameraState llamado en cleanup | OK |
| processors.ts - processingCanvas | Creado per-camera, no eliminado explicitamente | MEDIO |

### Hallazgos

1. **Cleanup patterns son robustos**: `CameraFeed.tsx` tiene un cleanup comprehensivo en el useEffect principal (linea 259-266) que llama `stopRenderLoop()`, `cleanupMLTimers()`, `stopLocalStream()` y `cleanupExternalStream()`. Cada sub-efecto tambien tiene su propio cleanup.

2. **cancelled flags correctos**: Los efectos async usan flags `cancelled` para evitar setState despues de unmount.

3. **Potencial leak en processingCanvas**: `createCameraState()` crea un `document.createElement('canvas')` para cada camara. Cuando se llama `resetCameraState(cameraId)`, se elimina del Map pero el canvas sigue en memoria hasta que el GC lo recoja. No es un leak verdadero pero podria acumularse.

4. **Snapshot canvas NO reutilizado (leak leve)**: En `CameraFeed.tsx` linea 607:
   ```typescript
   const snapshotCanvas = document.createElement('canvas')
   ```
   Esto crea un nuevo canvas en **cada ciclo ML** (cada 1-4 segundos por camara). Con 3 camaras, son ~3-9 canvas/segundo que deben ser GC'd. Aunque el GC eventualmente los limpia, esto genera presion de memoria innecesaria.

5. **TensorFlow tensors**: No se observa `tf.dispose()` o `tf.tidy()` en el codigo de inferencia de COCO-SSD. Si `model.detect()` crea tensors internamente, estos podrian acumularse. Sin embargo, el wrapper de `@tensorflow-models/coco-ssd` deberia manejar esto internamente.

6. **Event listener en track.onended**: En `CameraFeed.tsx` linea 334-335, `track.onended` se asigna directamente. Si la stream se recrea sin cleanup, el handler anterior podria persistir. Sin embargo, como `stopLocalStream()` llama `track.stop()`, el track se invalida y el handler no deberia ejecutarse.

### Recomendacion

Reutilizar el snapshot canvas (ver seccion 2) y considerar wrappear llamadas a COCO-SSD en `tf.tidy()` para asegurar cleanup de tensors intermedios.

---

## Plan de Accion Priorizado

| # | Accion | Impacto | Esfuerzo | Prioridad |
|---|--------|---------|----------|-----------|
| 1 | **Lazy loading de rutas en App.tsx** | Bundle inicial -60% | 1h | CRITICA |
| 2 | **manualChunks en vite.config.ts** | Chunks separados para ML libs | 1h | CRITICA |
| 3 | **Dynamic import de TF.js y MediaPipe** en model loaders | ML libs cargadas bajo demanda | 2h | CRITICA |
| 4 | **Mover inferencia ML a Web Worker** | Main thread desbloqueado, INP <200ms | 8h | ALTA |
| 5 | **Eliminar onnxruntime-web** si no se usa | -300 kB del bundle | 15m | ALTA |
| 6 | **useShallow en selectores de Zustand** | -50% re-renders | 1h | ALTA |
| 7 | **Reutilizar snapshot canvas** | Menos GC pressure | 30m | MEDIA |
| 8 | **Separar FPS update del detection store** | Menos recomputaciones | 2h | MEDIA |
| 9 | **Extraer auto-performance a hook separado** | Store update mas ligero | 1h | MEDIA |
| 10 | **MediaPipe delegate GPU con fallback** | ~2x mas rapido en dispositivos con GPU | 2h | MEDIA |
| 11 | **vite-plugin-compression (brotli)** | -70% tamano transferido | 30m | BAJA |
| 12 | **OffscreenCanvas para render loop** | Main thread libre de rendering | 4h | BAJA |

---

## Metricas Objetivo Post-Optimizacion

| Metrica | Actual (estimado) | Objetivo | Target NXT |
|---------|-------------------|----------|------------|
| Bundle inicial (gzipped) | ~900 kB | <200 kB | <=200 kB |
| Bundle total (gzipped) | ~1,100 kB | <800 kB | <1,000 kB |
| LCP | ~4.5s | <2.5s | <=2.5s |
| INP | ~500ms | <200ms | <=200ms |
| CLS | ~0.05 | <0.1 | <=0.1 |
| TTFB | ~200ms (Vite dev) | <800ms | <=800ms |
| ML model load time | ~5-8s | <3s (en Worker) | <5s |
| Render loop FPS | 30-60 | 30-60 | >=30 |
| Memory (3 cameras, 5min) | ~350MB | <250MB | <300MB |

---

## Dependencias por Tamano (Audit)

| Dependencia | Tamano Bundle (est.) | Necesaria | Alternativa |
|-------------|---------------------|-----------|-------------|
| @tensorflow/tfjs | ~1,400 kB | Si (COCO-SSD) | tfjs-tflite (mas pequeno) |
| @tensorflow/tfjs-backend-webgl | ~400 kB | Si | Ya incluido en tfjs |
| @mediapipe/tasks-vision | ~400 kB | Si | No hay alternativa mas ligera |
| @tensorflow-models/coco-ssd | ~200 kB | Si | YOLO via ONNX (mas eficiente) |
| onnxruntime-web | ~300 kB | **NO** (sin uso) | ELIMINAR |
| recharts | ~200 kB | Solo en Dashboard | Lazy load |
| framer-motion | ~140 kB | Parcial | motion (lite) o CSS animations |
| hls.js | ~60 kB | Si (external cameras) | Lazy load cuando se necesite |
| react + react-dom | ~130 kB | Si | - |
| react-router-dom | ~30 kB | Si | - |
| @supabase/supabase-js | ~50 kB | Si | - |
| zustand | ~3 kB | Si | - |
| lucide-react | ~30 kB (tree-shaken) | Si | - |

**Total estimado sin optimizar**: ~3,350 kB (coincide con los 3,326 kB reportados)
**Total estimado carga inicial (post-optimizacion)**: ~350-500 kB (React + UI + Supabase + router)

---

## Proximos Pasos

- [ ] Implementar acciones 1-3 (lazy routes + manualChunks + dynamic imports) - Sprint actual
- [ ] Implementar accion 5 (eliminar onnxruntime-web) - Inmediato
- [ ] Implementar accion 6 (useShallow) - Sprint actual
- [ ] Planificar accion 4 (Web Workers) para siguiente sprint
- [ ] Configurar performance budget en CI (`chunkSizeWarningLimit: 500`)
- [ ] Agregar `rollup-plugin-visualizer` al build para monitoreo continuo
- [ ] Medir Core Web Vitals reales con Lighthouse despues de optimizaciones

---

*NXT Performance v3.8.0 - Cada milisegundo cuenta*
