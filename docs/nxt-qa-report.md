# QA Report: Vision Human Insight

> **Generado por:** NXT QA v3.8.0
> **Fecha:** 2026-04-05
> **Proyecto:** vision-human-insight v1.0.0
> **Alcance:** Full-stack assessment (FastAPI backend + React/TypeScript frontend)

---

## Resumen Ejecutivo

| Metrica                  | Estado       | Detalle                                    |
|--------------------------|--------------|--------------------------------------------|
| Cobertura de tests       | **0%**       | No existen tests unitarios, de integracion ni E2E |
| TODOs pendientes         | **9**        | 7 en codigo fuente de aplicacion           |
| Uso de `any` en TypeScript | **Alto**   | 15+ ocurrencias en archivos de produccion  |
| Frameworks de testing    | **Ninguno**  | No hay Jest, Vitest, Pytest ni Playwright configurados |
| Calidad de error handling| **Media**    | Backend consistente, frontend irregular    |

**Veredicto general:** El proyecto tiene una arquitectura solida y tipos TypeScript bien definidos, pero carece completamente de infraestructura de testing. La cobertura es 0%. Antes de cualquier deploy a produccion, es critico establecer al menos tests unitarios para los routers de la API y los componentes principales del frontend.

---

## 1. Cobertura de Tests

### 1.1 Estado Actual: Sin Tests

No se encontraron archivos de test en el proyecto:

- **Frontend (`apps/web/`):** Cero archivos `*.test.ts`, `*.test.tsx`, `*.spec.ts` o `*.spec.tsx`.
- **Backend (`apps/api/`):** Solo existen `test_openai.py` y `test_openai_quick.py`, que son scripts manuales de verificacion de la API key de OpenAI, no tests automatizados con assertions.
- **No hay configuracion de test runners:** `package.json` no incluye Vitest, Jest ni Playwright. `requirements.txt` no incluye pytest.

### 1.2 Frameworks de Testing Ausentes

| Capa      | Framework esperado | Configurado | Instalado |
|-----------|--------------------|-------------|-----------|
| Frontend unit    | Vitest o Jest | No | No |
| Frontend E2E     | Playwright o Cypress | No | No |
| Backend unit     | pytest | No | No |
| Backend integration | pytest + httpx/TestClient | No | No |
| API contract     | Schemathesis o similar | No | No |

### 1.3 Tests Criticos Que Deberian Existir

#### Backend (Python/FastAPI)
1. **`tests/api/test_events.py`** - CRUD de eventos: crear, listar, filtrar, eliminar
2. **`tests/api/test_analytics.py`** - Health summary y trends con datos mock
3. **`tests/api/test_reports.py`** - Generacion de reportes JSON
4. **`tests/api/test_sessions.py`** - Init, heartbeat, admin actions (ban, disconnect, limit)
5. **`tests/api/test_external_cameras.py`** - CRUD de camaras externas con gateway mock
6. **`tests/api/test_ai_summary.py`** - Generacion de resumenes con OpenAI client mock
7. **`tests/api/test_auth.py`** - Login admin, token validation, bcrypt password check

#### Frontend (TypeScript/React)
8. **`apps/web/src/__tests__/store/appStore.test.ts`** - Zustand store: activateCamera, deactivateCamera, performance preset changes, session management
9. **`apps/web/src/__tests__/lib/supabase.test.ts`** - API client: insertEvent throttling, getEvents, getEventStats
10. **`apps/web/src/__tests__/lib/ml/processors.test.ts`** - Emotion stabilization, activity detection, false positive filtering
11. **`apps/web/src/__tests__/components/DashboardPage.test.tsx`** - Renders loading, empty state, data state
12. **`apps/web/src/__tests__/components/SessionStartModal.test.tsx`** - Form validation, submit flow

---

## 2. TODOs y FIXMEs Pendientes

Se identificaron **9 TODOs** en codigo fuente de la aplicacion (excluyendo herramientas/orquestador):

| # | Archivo | Linea | TODO | Severidad |
|---|---------|-------|------|-----------|
| 1 | `apps/web/src/lib/ml/processors.ts` | 506 | Implementar deteccion real de emociones | **Alta** |
| 2 | `apps/web/src/lib/ml/processors.ts` | 566 | Implementar deteccion real de movimiento | **Alta** |
| 3 | `apps/api/routers/reports.py` | 46 | Implementar generacion de PDF con reportlab | Media |
| 4 | `apps/api/services/model_trainer.py` | 85 | Implementar conversion completa (YOLO bbox) | Media |
| 5 | `apps/api/services/model_trainer.py` | 106 | Implementar formato COCO | Media |
| 6 | `apps/api/services/model_trainer.py` | 113 | Implementar formato personalizado | Media |
| 7 | `apps/api/services/model_trainer.py` | 156 | Ejecutar entrenamiento real con ultralytics | Media |

### Detalle de TODOs Criticos

**TODO #1 y #2 (processors.ts):** Las funciones `detectEmotions()` y `detectMovement()` contienen simulaciones con valores aleatorios en lugar de deteccion real. Esto significa que:
- Las emociones mostradas al usuario son aleatorias entre `['neutral', 'focused', 'happy']`
- El movimiento siempre retorna `'active'`
- El sistema tiene mecanismos de estabilizacion (ventanas temporales), lo cual es bueno, pero los datos de entrada son ficticios

**Impacto:** Cualquier usuario que confie en las metricas de emociones o movimiento recibira informacion no confiable. Esto debe documentarse claramente o implementarse con modelos reales.

---

## 3. TypeScript Type Safety

### 3.1 Configuracion (Buena)

El archivo `tsconfig.json` tiene `"strict": true` habilitado, junto con:
- `noUnusedLocals: true`
- `noUnusedParameters: true`
- `noFallthroughCasesInSwitch: true`

Esto es correcto y alineado con mejores practicas.

### 3.2 Tipos Bien Definidos (Bueno)

El archivo `apps/web/src/types.ts` (236 lineas) define tipos exhaustivos:
- Union types para `EventType`, `EmotionType`, `ActivityType`, `HealthStatus`
- Interfaces completas para `EventPayload`, `Event`, `CameraConfig`, `DetectionState`
- Tipos para sesiones demo (`DemoSessionRecord`, `AdminSessionsResponse`)
- Tipos para camaras externas (`ExternalCamera`, `ExternalCameraPayload`)

### 3.3 Uso Excesivo de `any` (Problema)

Se encontraron **15+ ocurrencias de `any`** en codigo de produccion:

| Archivo | Ocurrencias | Detalle |
|---------|-------------|---------|
| `processors.ts` | 8 | `any[]` para faces, bbox, objects, filterFalsePositives |
| `CameraManager.tsx` | 5 | `catch (err: any)` en multiples handlers |
| `CameraFeed.tsx` | 1 | `catch (err: any)` |
| `ExternalCameraForm.tsx` | 1 | `catch (err: any)` |
| `supabase.ts` | 2 | `payload: any`, `catch (error: any)` |

**Recomendacion:**
- Reemplazar `any[]` en processors.ts con interfaces tipadas para detecciones faciales y bounding boxes
- Reemplazar `catch (err: any)` con `catch (err: unknown)` y usar type narrowing
- Tipar el `payload` en `insertEvent()` con `EventPayload` en lugar de `any`

---

## 4. Error Handling

### 4.1 Backend API (Bueno)

Los routers de FastAPI siguen un patron consistente:
- Todos los endpoints estan envueltos en `try/except`
- Se usa `HTTPException` con codigos de estado apropiados (400, 401, 403, 404, 500, 502, 503)
- El re-raise de `HTTPException` es correcto en `events.py` (lineas 98-99, 118-119)
- El router de sesiones maneja multiples edge cases: banned IPs, missing sessions, bcrypt validation

**Problemas detectados:**
- **BUG-001:** En `events.py` linea 42, el catch generico `except Exception as e` expone el mensaje de error interno al cliente via `detail=str(e)`. Esto puede filtrar informacion sensible (paths, queries SQL, etc.)
- **BUG-002:** En `analytics.py` linea 127, `datetime.fromisoformat()` puede lanzar `ValueError` si `created_at` tiene un formato inesperado, pero no hay try/catch especifico (a diferencia de `events.py` linea 172 que si lo tiene)
- **BUG-003:** En `sessions.py` linea 144, `_insert_session_event()` silencia todas las excepciones con un `except Exception: pass`. Esto oculta errores de insercion de eventos de sesion sin logging
- **BUG-004:** En `external_cameras.py`, los endpoints `start_external_camera` y `stop_external_camera` no manejan el caso donde `result.data` es `None` despues del update (lineas 117, 152)

### 4.2 Frontend (Irregular)

**Patron positivo:**
- El archivo `supabase.ts` tiene un wrapper `apiRequest<T>()` que maneja errores HTTP de forma centralizada
- El logError/logWarn esta canalizado a traves de `utils/logger.ts` en vez de console.log directo
- `DashboardPage.tsx` muestra mensajes de error amigables al usuario

**Problemas detectados:**
- **BUG-005:** Multiples `.catch(() => {})` en `CameraFeed.tsx` (lineas 287, 384, 416, 478, 497, 510, 598) silencian errores completamente. Si `video.play()` falla, el usuario no recibe feedback
- **BUG-006:** En `supabase.ts` linea 62-64, el throttle de `insertEvent()` retorna `null` silenciosamente sin diferenciar entre "throttled" y "error", haciendo dificil el debugging
- **BUG-007:** En `DashboardPage.tsx` linea 9, `logError` esta hardcodeado como no-op: `const logError = (_message: string, _error?: unknown) => {}`. Los errores del dashboard se pierden completamente

---

## 5. Code Quality Issues

### 5.1 Seguridad

| ID | Severidad | Descripcion |
|----|-----------|-------------|
| SEC-001 | **Alta** | `supabase_client.py` usa `SUPABASE_SERVICE_ROLE_KEY` (permisos completos). Si este backend es expuesto publicamente, cualquier request con el token correcto tiene acceso total a la base de datos |
| SEC-002 | **Alta** | `sessions.py` linea 30: `ADMIN_API_TOKEN` se lee de env y se compara en texto plano. No hay rotacion, ni expiracion, ni rate limiting en el endpoint de login |
| SEC-003 | **Media** | `ai_summary.py` linea 178: Los archivos de audio TTS se guardan en `/tmp/` sin cleanup. Esto puede causar acumulacion de archivos en produccion |
| SEC-004 | **Media** | `external_cameras.py` linea 54: `user_id` esta hardcodeado como `"anonymous"`. No hay autenticacion real para operaciones CRUD de camaras |
| SEC-005 | **Media** | `ai_summary.py` linea 219: La imagen base64 enviada a OpenAI para validacion de detecciones no tiene validacion de tamano. Un payload grande podria causar problemas de memoria |

### 5.2 Duplicacion de Codigo

- La funcion `get_supabase()` se repite identica en cada router (`events.py`, `analytics.py`, `reports.py`, `ai_summary.py`, `external_cameras.py`, `sessions.py`). Deberia centralizarse como dependency global.
- `computeAggregatedDetections()` y `computeLegacyDetectionState()` en `appStore.ts` se llaman juntas en 8 lugares. Considerar un helper que retorne ambas.

### 5.3 Modelos ML Simulados

Dos de los tres procesadores ML principales son simulaciones:

| Modelo | Archivo | Estado | Detalle |
|--------|---------|--------|---------|
| COCO-SSD (objetos) | `models/coco-ssd.ts` | **Real** | TensorFlow.js model cargado |
| MediaPipe Face | `models/mediapipe-face.ts` | **Real** | Face detection funcional |
| MediaPipe Pose | `models/mediapipe-pose.ts` | **Real** | Pose detection funcional |
| Emociones | `processors.ts:500` | **Simulado** | Random entre neutral/focused/happy |
| Movimiento | `processors.ts:561` | **Simulado** | Siempre retorna 'active' |

### 5.4 Dead Code

- `apps/web/src/components/CameraView.tsx` esta listado como "AD" en git (added then deleted)
- Variables de modelo `cocoSsdModel`, `faceDetector`, `poseDetector` en `processors.ts` (lineas 22-24) se declaran pero las referencias se manejan dentro de los modulos importados

---

## 6. Bugs Encontrados

| ID | Severidad | Componente | Descripcion |
|----|-----------|------------|-------------|
| BUG-001 | Alta | Backend API | Error messages internos expuestos al cliente en todas las rutas via `detail=str(e)` |
| BUG-002 | Media | analytics.py | `datetime.fromisoformat()` sin manejo de formato invalido en `/trends` |
| BUG-003 | Baja | sessions.py | `_insert_session_event()` silencia excepciones sin logging |
| BUG-004 | Media | external_cameras.py | No se verifica `result.data` despues de update en start/stop |
| BUG-005 | Media | CameraFeed.tsx | `.catch(() => {})` silencia errores de reproduccion de video |
| BUG-006 | Baja | supabase.ts | Throttle de insertEvent no distingue entre "throttled" y "error" |
| BUG-007 | Media | DashboardPage.tsx | `logError` es una funcion no-op, errores se pierden |

---

## 7. Recomendaciones Priorizadas

### Prioridad 1 - Critica (Sprint actual)

1. **Configurar pytest + httpx** en el backend con al menos tests para `events.py` y `sessions.py`
2. **Configurar Vitest** en el frontend con tests para `appStore.ts` y `supabase.ts`
3. **Reemplazar `detail=str(e)`** en los handlers de excepcion del backend con mensajes genericos para el cliente, loggeando el error completo internamente

### Prioridad 2 - Alta (Proximo sprint)

4. **Implementar deteccion real de emociones** o documentar explicitamente al usuario que es simulada
5. **Eliminar uso de `any`** en `processors.ts` y `CameraManager.tsx`
6. **Agregar logging real** en `DashboardPage.tsx` (reemplazar no-op `logError`)
7. **Validar `result.data`** en `external_cameras.py` despues de operaciones de update

### Prioridad 3 - Media (Backlog)

8. **Centralizar `get_supabase()`** como dependency global en `main.py`
9. **Implementar generacion de PDF** en `reports.py` (TODO pendiente)
10. **Agregar rate limiting** al endpoint de login admin
11. **Agregar cleanup** para archivos TTS en `/tmp/`
12. **Configurar Playwright** para tests E2E del flujo completo: init session -> live detection -> dashboard

---

## 8. Metricas de Calidad

| Metrica | Valor Actual | Objetivo Minimo | Estado |
|---------|-------------|-----------------|--------|
| Test coverage (backend) | 0% | 80% | FAIL |
| Test coverage (frontend) | 0% | 60% | FAIL |
| TODOs en codigo | 9 | 0 criticos | WARN |
| Uso de `any` | 15+ | 0 | WARN |
| Error handling consistente | ~70% | 95% | WARN |
| Tipos TypeScript definidos | Bueno | Bueno | PASS |
| Strict mode TS | Habilitado | Habilitado | PASS |
| Console.log en produccion | 2 (via logger) | 0 directo | PASS |
| Secrets en codigo | 0 | 0 | PASS |

---

## 9. Criterios de Salida QA

- [ ] Test coverage backend >= 80%
- [ ] Test coverage frontend >= 60%
- [ ] 0 bugs criticos abiertos
- [ ] 0 TODOs criticos sin plan de resolucion
- [ ] Eliminacion de `any` en codigo de produccion
- [ ] Error handling consistente en todos los endpoints

**Estado actual: NO APTO para release a produccion.**
El proyecto necesita al minimo la infraestructura de testing (Prioridad 1) antes de considerarse listo.

---

*NXT QA v3.8.0 - Si No Esta Testeado, No Esta Terminado*
