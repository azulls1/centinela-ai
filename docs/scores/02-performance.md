# 02 - Performance Evaluation

**Proyecto:** Vision Human Insight
**Fecha de evaluacion:** 2026-04-05
**Evaluador:** Automated code analysis (Claude)
**Metodo:** Analisis estatico de codigo fuente, configuraciones Docker y arquitectura

---

## 1. Tiempo de Respuesta

**Score: 5 / 10**

### Tabla de Evidencia

| Aspecto | Archivo | Hallazgo | Impacto |
|---------|---------|----------|---------|
| Code splitting (React.lazy) | `apps/web/src/App.tsx` L1-9 | Las 4 paginas (LivePage, DashboardPage, SettingsPage, AdminPage) usan `lazy()` con `Suspense` | Positivo: carga inicial reducida |
| Manual chunks (Vite) | `apps/web/vite.config.ts` L18-28 | Chunks separados para vendor-react, vendor-ui, vendor-ml, vendor-supabase | Positivo: paralelismo de carga, cache granular |
| Caching en API | `apps/api/routers/ai_summary.py` L22 | Solo `@lru_cache(maxsize=1)` para el cliente OpenAI | Limitado: no hay cache de respuestas de queries |
| Paginacion en API | `apps/api/routers/events.py` L50-51 | Parametros `limit` (max 1000) y `offset` con `.range()` | Positivo: evita cargas masivas de datos |
| Estadisticas sin cache | `apps/api/routers/events.py` L132-203, `analytics.py` L23-96 | Los endpoints `/stats/summary`, `/health-summary` y `/trends` recalculan todo en cada peticion | Negativo: sin cache de resultados computados |
| Throttling ML en frontend | `apps/web/src/lib/ml/processors.ts` L140 | `MIN_FRAME_INTERVAL_MS = 400` entre procesamientos ML | Positivo: evita saturar la CPU del navegador |
| ML interval adaptativo | `apps/web/src/components/CameraFeed.tsx` L202-207 | Si FPS < 24 incrementa intervalo ML (+350ms), si FPS > 48 reduce (-150ms) | Positivo: auto-ajuste segun capacidad del dispositivo |
| Uvicorn sin workers | `apps/api/main.py` L142-147 | `uvicorn.run()` sin parametro `workers`, single-process | Negativo: un solo proceso atiende todas las peticiones |

### Hallazgos

- El frontend implementa buenas practicas de code splitting y chunking que reducen el tiempo de carga inicial.
- La carga de modelos ML es diferida (lazy) y se realiza en paralelo con `Promise.allSettled`, lo cual minimiza el tiempo de espera.
- El backend carece de cualquier capa de cache para queries frecuentes (estadisticas, tendencias, health-summary). Cada peticion ejecuta una query completa a Supabase y procesa los resultados en memoria.
- Los endpoints de OpenAI (`/generate-summary`, `/validate-detections`) dependen de llamadas externas sin timeout configurado, lo que puede causar latencias impredecibles.
- No hay medicion P50/P95/P99 implementada ni middleware de telemetria.

### Recomendacion

1. Agregar cache con TTL (e.g., `cachetools.TTLCache` o Redis) para endpoints de estadisticas y analytics que se consultan frecuentemente.
2. Configurar timeouts explicitos en las llamadas a OpenAI (`timeout=30` en el constructor del cliente).
3. Agregar middleware de telemetria (e.g., `starlette-prometheus` o `opentelemetry`) para medir latencias reales P50/P95/P99.

---

## 2. Throughput

**Score: 3 / 10**

### Tabla de Evidencia

| Aspecto | Archivo | Hallazgo | Impacto |
|---------|---------|----------|---------|
| Workers uvicorn | `apps/api/main.py` L142-147 | Single process: `uvicorn.run("main:app", ...)` sin `workers` | Critico: un solo worker maneja todo el trafico |
| Dockerfile CMD | `apps/api/Dockerfile` L15 | `CMD ["uvicorn", "main:app", ...]` sin `--workers` | Critico: produccion con un solo worker |
| docker-compose command | `infra/docker-compose.yml` L16 | `uvicorn main:app --host 0.0.0.0 --port 8000 --reload` | Critico: `--reload` en produccion degrada rendimiento |
| Rate limiting | `apps/api/main.py` completo | No existe middleware de rate limiting | Riesgo: sin proteccion contra abuso |
| Connection pooling | `apps/api/supabase_client.py` L23 | Un unico cliente Supabase global (singleton) | Neutral: reutiliza conexion pero no hay pool explicito |
| Async handlers | Todos los routers | Todos los handlers son `async def` | Positivo: no bloquean el event loop en I/O |
| Concurrencia stream-gateway | `apps/stream-gateway/main.py` L69 | `STREAM_PROCESSES: Dict[str, StreamProcess] = {}` en memoria | Limitante: estado en memoria impide escalar |
| OpenAI calls sincronas | `apps/api/routers/ai_summary.py` L120 | `openai_client.chat.completions.create()` es call sincrona dentro de handler async | Negativo: bloquea el event loop durante la llamada |

### Hallazgos

- El factor limitante mas critico es el uso de un unico worker de uvicorn tanto en desarrollo como en produccion. FastAPI con un solo worker puede manejar ~100-500 req/s para endpoints simples, pero las llamadas bloqueantes a OpenAI reducen drasticamente el throughput efectivo.
- Las llamadas a OpenAI usan el SDK sincrono (`openai.OpenAI`) dentro de handlers `async def`, lo cual bloquea el event loop y reduce la capacidad de concurrencia a practicamente una peticion de IA a la vez.
- No existe rate limiting, lo que expone la API a abuso y agotamiento de recursos.
- El stack.yml de produccion define `replicas: 1` para ambos servicios.

### Recomendacion

1. Configurar multiples workers en produccion: `uvicorn main:app --workers 4` (o usar gunicorn con uvicorn workers).
2. Reemplazar `openai.OpenAI` por `openai.AsyncOpenAI` para no bloquear el event loop.
3. Agregar rate limiting con `slowapi` o un middleware personalizado.
4. Eliminar `--reload` de la configuracion de docker-compose para produccion.

---

## 3. Escalabilidad

**Score: 4 / 10**

### Tabla de Evidencia

| Aspecto | Archivo | Hallazgo | Impacto |
|---------|---------|----------|---------|
| API stateless | `apps/api/main.py`, `supabase_client.py` | La API no almacena estado en memoria; toda la persistencia es en Supabase | Positivo: puede escalar horizontalmente |
| Stream-gateway stateful | `apps/stream-gateway/main.py` L69 | `STREAM_PROCESSES: Dict` almacena procesos ffmpeg en memoria del contenedor | Critico: no puede escalar horizontalmente |
| Docker replicas | `infra/stack.yml` L21, L51 | `replicas: 1` para ambos servicios | Negativo: sin escalamiento horizontal configurado |
| Resource limits | `infra/stack.yml` L24-29 | API: limits 1 CPU / 1G RAM, reservations 0.25 CPU / 256M | Positivo: limites definidos evitan consumo descontrolado |
| Traefik labels | `infra/stack.yml` L32-37 | Configuracion de Traefik con load balancer | Positivo: infraestructura de reverse proxy lista para escalar |
| Supabase como DB | `apps/api/supabase_client.py` | Supabase (PostgreSQL gestionado) como unico almacen | Positivo: la base de datos escala independientemente |
| Volume para streams | `infra/docker-compose.yml` L36, `stack.yml` L69 | `stream-data` volume local | Limitante: volumen local no se comparte entre replicas |
| Frontend SPA | `apps/web/` | Aplicacion React estatica, sin SSR | Positivo: desplegable en CDN, escala infinitamente |
| Sin message queue | Todo el proyecto | No existe cola de mensajes para procesamiento asincrono | Negativo: no hay desacoplamiento para cargas pesadas (OpenAI, reportes) |

### Hallazgos

- La API principal es esencialmente stateless (usa Supabase externamente), lo cual es bueno para escalamiento horizontal. Sin embargo, las replicas estan fijadas en 1.
- El stream-gateway es inherentemente stateful: almacena procesos ffmpeg y archivos de segmentos HLS en memoria/disco local. Escalar este servicio requiere una arquitectura diferente (e.g., sticky sessions o estado compartido).
- No existe un sistema de colas (RabbitMQ, Redis Queue, Celery) para desacoplar operaciones costosas como las llamadas a OpenAI o la generacion de reportes.
- La infraestructura de Traefik esta preparada para load balancing, pero no se aprovecha con `replicas: 1`.

### Recomendacion

1. Incrementar `replicas` de la API a 2-4 en `stack.yml` para escalar horizontalmente.
2. Desacoplar el stream-gateway usando almacenamiento compartido (S3/MinIO) para los segmentos HLS en lugar de volumen local.
3. Implementar una cola de tareas (Celery + Redis) para las operaciones costosas de OpenAI y generacion de reportes.
4. Considerar auto-scaling basado en metricas de CPU/memoria.

---

## 4. Uso de Recursos

**Score: 6 / 10**

### Tabla de Evidencia

| Aspecto | Archivo | Hallazgo | Impacto |
|---------|---------|----------|---------|
| Bundle splitting | `apps/web/vite.config.ts` L19-25 | 4 chunks manuales: vendor-react, vendor-ui, vendor-ml (~17MB total ML), vendor-supabase | Positivo: carga ML solo cuando se necesita |
| Carga ML diferida | `apps/web/src/lib/ml/processors.ts` L89-132 | `loadModels()` ejecuta `Promise.allSettled` para cargar 3 modelos en paralelo; tolerancia a fallos individuales | Positivo: no bloquea la app si un modelo falla |
| Tamano modelos ML | `apps/web/src/lib/ml/processors.ts` L85-87 | COCO-SSD ~10MB, MediaPipe Face ~2MB, MediaPipe Pose ~5MB = ~17MB total | Significativo: carga pesada para conexiones lentas |
| Cleanup en useEffect | `apps/web/src/components/CameraFeed.tsx` L263-270 | Effect de limpieza ejecuta `stopRenderLoop`, `cleanupMLTimers`, `stopLocalStream`, `cleanupExternalStream` | Positivo: prevencion de memory leaks |
| cancelAnimationFrame | `apps/web/src/components/CameraFeed.tsx` L216-222 | `stopRenderLoop` cancela animation frame correctamente | Positivo: libera ciclos de renderizado |
| Limpieza de MediaStream | `apps/web/src/components/CameraFeed.tsx` L239-244 | `stopLocalStream` llama `.stop()` en todos los tracks | Positivo: libera dispositivo de camara |
| Limpieza de HLS | `apps/web/src/components/CameraFeed.tsx` L246-261 | `cleanupExternalStream` destruye instancia HLS y limpia video | Positivo: evita leaks de video/network |
| Canvas 2D optimizado | `apps/web/src/components/CameraFeed.tsx` L148-151 | `getContext('2d', { alpha: false, desynchronized: true, willReadFrequently: false })` | Positivo: optimizaciones de GPU habilitadas |
| ML snapshot resize | `apps/web/src/components/CameraFeed.tsx` L611-613 | Redimensiona a 320x240 antes de enviar a ML | Positivo: reduce carga de procesamiento ML |
| requestIdleCallback | `apps/web/src/components/CameraFeed.tsx` L569-580 | ML scheduling usa `requestIdleCallback` con fallback | Positivo: procesamiento ML no bloquea UI |
| Docker multi-stage | `apps/api/Dockerfile` L1-4 | Build en dos etapas: builder + slim runtime | Positivo: imagen de produccion mas ligera |
| Resource limits Docker | `infra/stack.yml` L24-29, L55-60 | Ambos servicios: max 1 CPU / 1G RAM | Positivo: limites definidos protegen el host |
| Limpieza camera state | `apps/web/src/lib/ml/processors.ts` L64-70 | `resetCameraState` y `resetAllCameraStates` limpian Maps | Positivo: prevencion de acumulacion de estado |
| chunkSizeWarningLimit | `apps/web/vite.config.ts` L28 | Umbral elevado a 800KB | Informativo: indica chunks grandes esperados (ML) |
| No-op loggers en produccion | `apps/web/src/lib/ml/processors.ts` L6-8 | `debugLog`, `logError`, `logWarn` son funciones vacias | Positivo: sin overhead de logging en produccion |

### Hallazgos

- El frontend demuestra un buen manejo de recursos: cleanup sistematico en todos los useEffect, uso de requestIdleCallback para ML, redimensionado de frames antes del procesamiento, y optimizaciones de canvas.
- La carga de modelos ML (~17MB) es significativa pero se maneja de forma diferida y tolerante a fallos.
- El backend usa Docker multi-stage build y tiene limites de recursos definidos en produccion.
- No se observan memory leaks evidentes en el codigo del frontend; todas las rutas de cleanup estan implementadas (animation frames, media streams, HLS, timers).
- El estado por camara (`cameraStates` Map) crece con cada camara activa pero se limpia correctamente al desmontar.
- No hay monitoreo de uso de memoria o CPU a nivel de aplicacion.

### Recomendacion

1. Implementar lazy loading de modelos ML individuales (cargar solo los modelos que el usuario habilita en la configuracion, no todos).
2. Considerar Web Workers para el procesamiento ML para evitar cualquier impacto en el hilo principal de UI.
3. Agregar metricas de memoria y CPU al endpoint `/api/health` para monitoreo en produccion.
4. Evaluar `OffscreenCanvas` para el renderizado de video en navegadores compatibles.

---

## Resumen General

| Area | Score | Estado |
|------|-------|--------|
| Tiempo de Respuesta | 5/10 | Frontend bien optimizado, backend sin cache |
| Throughput | 3/10 | Single worker, calls sincronas a OpenAI, sin rate limiting |
| Escalabilidad | 4/10 | API stateless pero replicas=1, stream-gateway stateful |
| Uso de Recursos | 6/10 | Buen cleanup frontend, Docker limits, modelos ML pesados |
| **Promedio** | **4.5/10** | **Necesita mejoras significativas en backend** |

### Prioridades de Mejora (por impacto)

1. **[Throughput]** Configurar multiples workers en uvicorn y usar `AsyncOpenAI` en lugar del SDK sincrono.
2. **[Throughput]** Agregar rate limiting para proteccion contra abuso.
3. **[Tiempo de Respuesta]** Implementar cache con TTL para endpoints de analytics/estadisticas.
4. **[Escalabilidad]** Incrementar replicas de la API y desacoplar stream-gateway del almacenamiento local.
5. **[Uso de Recursos]** Mover procesamiento ML a Web Workers y cargar solo los modelos habilitados.
