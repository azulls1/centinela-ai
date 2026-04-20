# Evaluacion de Codigo - Vision Human Insight

**Fecha de evaluacion:** 2026-04-05
**Evaluador:** Analisis automatizado con evidencia directa del repositorio
**Rama evaluada:** main

---

## 1. Deuda Tecnica

### Score: 4/10

| Metrica | Valor | Evidencia |
|---------|-------|-----------|
| Complejidad ciclomatica (appStore.ts) | Alta - 823 lineas, ~30 metodos en un unico store | `apps/web/src/store/appStore.ts` - Store monolitico con estado de camaras, detecciones, sesiones, admin auth, rendimiento y eventos en un solo archivo |
| Complejidad ciclomatica (processors.ts) | Alta - 600+ lineas, pipeline secuencial con 5+ niveles de anidamiento | `apps/web/src/lib/ml/processors.ts` - Funcion `processFrame` con try/catch anidados a 4-5 niveles, indentacion inconsistente (mezcla tabs/spaces lineas 212-328) |
| Complejidad ciclomatica (CameraFeed.tsx) | Alta - 748 lineas, 7 useEffect hooks en un solo componente | `apps/web/src/components/CameraFeed.tsx` - Maneja streams locales, HLS externos, render loop, ML processing, visibility change y video readiness |
| Duplicacion de codigo | Detectada | `createEmptySnapshot()` esta duplicada identicamente en `appStore.ts` (linea 97) y `CameraFeed.tsx` (linea 23) |
| Codigo legacy coexistente | Presente | `computeLegacyDetectionState` en appStore.ts - comentario explicito "(usado por componentes existentes)" indica deuda tecnica consciente |
| Modelos globales mutables | `any` types | `processors.ts` lineas 22-24: `let cocoSsdModel: any`, `let faceDetector: any`, `let poseDetector: any` - estado mutable global sin tipado |
| Test coverage | 3 archivos de test, ~28 archivos fuente = ~10.7% de archivos cubiertos | `src/__tests__/App.test.tsx` (smoke test), `appStore.test.ts` (5 tests basicos), `Toggle.test.tsx` (4 tests) |

**Hallazgos:**
- El store `appStore.ts` (823 lineas) mezcla multiples dominios: gestion de camaras, detecciones ML, sesiones de usuario, autenticacion admin, camaras externas y performance presets. Deberia dividirse en al menos 3-4 slices independientes.
- `CameraFeed.tsx` (748 lineas) es un componente "god component" con 7 `useEffect` hooks, manejo de streams locales y HLS, render loop con canvas, y scheduling de ML processing. Cada una de estas responsabilidades deberia ser un custom hook separado.
- `processors.ts` (600+ lineas) tiene indentacion inconsistente en la funcion `processFrame` (lineas 212-328), mezclando niveles de indentacion de 2 y 4 espacios.
- Funcion `createEmptySnapshot` duplicada en 2 archivos sin factorizacion compartida.
- Uso extensivo de `any` en processors.ts para modelos ML, eliminando beneficios de TypeScript.
- `@typescript-eslint/no-explicit-any` esta deshabilitado (`off`) en `.eslintrc.cjs` linea 29.

**Recomendacion:**
1. Dividir `appStore.ts` en slices: `cameraStore`, `detectionStore`, `sessionStore`, `adminStore` usando la tecnica de slices de Zustand.
2. Extraer custom hooks de `CameraFeed.tsx`: `useLocalStream`, `useHlsStream`, `useRenderLoop`, `useMLProcessing`.
3. Crear un modulo compartido `src/lib/detection-utils.ts` para funciones duplicadas como `createEmptySnapshot`.
4. Reemplazar tipos `any` en processors.ts con interfaces concretas para los modelos ML.
5. Habilitar `@typescript-eslint/no-explicit-any: warn` en eslint.

---

## 2. Arquitectura

### Score: 6/10

| Metrica | Valor | Evidencia |
|---------|-------|-----------|
| Separacion de capas | 3 apps independientes | `apps/web` (React/Vite), `apps/api` (FastAPI/Python), `apps/stream-gateway` (Python) - buena separacion a nivel de directorio |
| API routers organizados | 6 routers | `apps/api/routers/`: events, analytics, reports, ai_summary, external_cameras, sessions - cada uno con responsabilidad unica |
| Frontend routing | Lazy loading implementado | `App.tsx` usa `React.lazy()` para las 4 paginas principales |
| Shared package | Vacio/sin uso | `packages/shared/` existe pero solo contiene `README.md` y `package.json` - no se usa para compartir tipos entre web y api |
| Acoplamiento store-componentes | Alto | 12 archivos importan directamente desde `../store/appStore` - todos los componentes dependen de un unico store monolitico |
| Infraestructura | Docker + Supabase | `infra/docker-compose.yml`, `apps/api/Dockerfile`, `apps/stream-gateway/Dockerfile` - infraestructura dockerizada |
| Tipos compartidos | Solo frontend | `src/types.ts` centraliza tipos pero solo para el frontend; no hay contrato compartido con el API |

**Hallazgos:**
- La separacion en 3 aplicaciones (web, api, stream-gateway) es una buena decision arquitectonica. Cada app tiene su propio stack tecnologico apropiado.
- El API sigue el patron de FastAPI routers correctamente, con 6 routers separados por dominio (events, analytics, reports, ai_summary, external_cameras, sessions).
- El paquete `packages/shared` esta vacio y no cumple su proposito. No hay contrato de tipos compartido entre frontend y backend.
- El frontend tiene un unico store Zustand monolitico que crea acoplamiento fuerte: 12 de ~20 archivos fuente importan del mismo store.
- No existe un API client/SDK layer en el frontend - los componentes probablemente hacen llamadas directas al API.
- La capa ML (`src/lib/ml/`) esta bien organizada con modelos separados (coco-ssd, mediapipe-face, mediapipe-pose) y un procesador central.

**Recomendacion:**
1. Implementar tipos compartidos en `packages/shared` para contratos API (event types, request/response schemas).
2. Crear un API client layer en `src/lib/api/` que encapsule todas las llamadas HTTP al backend.
3. Dividir el store monolitico en modulos independientes para reducir acoplamiento.
4. Considerar un patron de event bus o middleware para comunicacion entre modulos del store.

---

## 3. Mantenibilidad

### Score: 5/10

| Metrica | Valor | Evidencia |
|---------|-------|-----------|
| Documentacion (archivos .md) | 20+ archivos .md en el proyecto | README.md, INSTALLATION.md, DEPLOYMENT.md, PROJECT_STRUCTURE.md, CONFIGURACION_OPENAI.md, CONFIGURACION_SUPABASE.md, plus 7+ docs en `/docs/` y 5+ en `infra/supabase/` |
| Comentarios inline | Mixtos - espanol e ingles | `types.ts`: cada tipo tiene comentario en espanol. `processors.ts`: JSDoc en espanol, comentarios inline en ingles. `CameraFeed.tsx`: sin JSDoc |
| JSDoc/Docstrings | Parcial | `processors.ts` tiene JSDoc en funciones exportadas. `appStore.ts` no tiene JSDoc en ninguno de sus ~30 metodos. API Python tiene docstrings en endpoints |
| Naming conventions | Generalmente buenas | camelCase para variables/funciones, PascalCase para componentes/tipos. Excepciones: mezcla espanol/ingles en labels ("Camara sin nombre" vs "browser") |
| ESLint configurado | Si, con reglas relajadas | `.eslintrc.cjs`: extends recommended configs pero `no-explicit-any: off`, `no-misused-promises: off` |
| TypeScript strict mode | Activado | `tsconfig.json`: `"strict": true`, `"noUnusedLocals": true`, `"noUnusedParameters": true` |
| Prettier/Formatting | No configurado | No se encontro `.prettierrc`, `.prettierignore` ni dependencia de prettier en package.json |
| Organizacion de archivos | Razonable | Estructura clara: `components/`, `pages/`, `lib/`, `store/`, `utils/`, `__tests__/` |
| Script de lint | Configurado | `package.json`: script `lint` con `--max-warnings 0` |
| Python linting | No configurado | No se encontro `ruff`, `flake8`, `black`, ni `pyproject.toml` con config de linting en `apps/api/` |

**Hallazgos:**
- La documentacion es abundante (20+ archivos .md) pero fragmentada y sin estructura clara. Hay documentos como `SOLUCION_MCP_GITLAB.md` que parecen notas de troubleshooting mas que documentacion de proyecto.
- TypeScript strict mode esta correctamente activado, lo cual es positivo, pero se anula parcialmente al desactivar `no-explicit-any` en ESLint.
- No hay Prettier configurado, lo que puede llevar a inconsistencias de formato (ya evidenciado en la indentacion mixta de processors.ts).
- Mezcla de idiomas (espanol/ingles) en comentarios, nombres de variables y mensajes de log reduce la coherencia.
- El backend Python no tiene herramientas de linting configuradas (ni ruff, ni flake8, ni black).
- El archivo `pytest.ini` existe pero el directorio `tests/` referenciado no existe y no hay archivos de test Python.

**Recomendacion:**
1. Agregar Prettier con configuracion compartida para formateo consistente.
2. Configurar `ruff` o `black` + `flake8` para el backend Python.
3. Estandarizar el idioma de codigo (preferiblemente ingles para codigo, espanol para UI/documentacion).
4. Agregar JSDoc a los metodos del store que son la API publica del estado.
5. Re-habilitar `no-explicit-any` como warning para mejorar progresivamente el tipado.

---

## 4. Cobertura de Pruebas

### Score: 2/10

| Metrica | Valor | Evidencia |
|---------|-------|-----------|
| Framework de testing (frontend) | Vitest 4.1.2 configurado | `vitest.config.ts` con happy-dom, v8 coverage provider |
| Tests unitarios frontend | 3 archivos, ~10 tests totales | `App.test.tsx` (1 smoke test), `appStore.test.ts` (5 tests), `Toggle.test.tsx` (4 tests) |
| Archivos fuente frontend | ~28 archivos .ts/.tsx (excluyendo tests) | 11 componentes, 4 paginas, 6 lib/utils, 1 store, 1 types, etc. |
| Cobertura estimada por archivos | ~10.7% (3/28) | Solo 3 de 28 archivos fuente tienen tests asociados |
| Tests unitarios backend (Python) | 0 archivos | `pytest.ini` configurado pero directorio `tests/` no existe; `test_openai.py` y `test_openai_quick.py` son scripts de verificacion, no tests automatizados |
| Tests de integracion | 0 | No se encontraron tests que verifiquen interaccion entre API y frontend |
| Tests E2E | 0 | No se encontro Playwright, Cypress ni ninguna herramienta E2E |
| Coverage reporting | Configurado pero sin metricas | `vitest.config.ts` tiene coverage con v8 provider pero no hay reporte generado ni threshold minimo definido |
| Testing libraries instaladas | Si | `@testing-library/react`, `@testing-library/jest-dom`, `happy-dom`, `jsdom` - buena base |

**Hallazgos:**
- Solo existen 3 archivos de test en todo el proyecto, todos en el frontend:
  - `App.test.tsx`: Un unico smoke test que verifica renderizado sin crash.
  - `appStore.test.ts`: 5 tests basicos del store (config defaults, update, privacy, cameras, presets). No cubre detecciones, camaras externas, sesiones ni admin auth.
  - `Toggle.test.tsx`: 4 tests de un componente simple de UI.
- Los componentes criticos no tienen tests: `CameraFeed.tsx` (748 lineas), `CameraManager.tsx`, `DetectionPanel.tsx`, `PerformancePanel.tsx`.
- La logica ML compleja en `processors.ts` (600+ lineas) no tiene ningun test.
- El backend Python tiene `pytest.ini` configurado pero el directorio `tests/` no existe. Los archivos `test_openai.py` y `test_openai_quick.py` son scripts ad-hoc de verificacion de API key, no tests automatizados.
- No hay tests de integracion ni E2E. Para una aplicacion de vision por computadora en tiempo real, esto representa un riesgo significativo.
- Las testing libraries necesarias estan instaladas (`@testing-library/react`, `happy-dom`) pero sub-utilizadas.

**Recomendacion:**
1. **Prioridad alta**: Agregar tests para `appStore.ts` cubriendo flujos de camaras, detecciones y sesiones (al menos 80% de los metodos).
2. **Prioridad alta**: Crear tests unitarios para `processors.ts` con mocks de los modelos ML.
3. Crear el directorio `apps/api/tests/` con tests basicos de cada endpoint usando `httpx` + `pytest`.
4. Definir un threshold minimo de coverage (e.g., `fail_under: 40`) en `vitest.config.ts`.
5. Agregar al menos un test E2E con Playwright para el flujo critico: iniciar sesion -> activar camara -> ver detecciones.
6. Integrar coverage check en CI/CD para prevenir regresiones.

---

## Resumen Ejecutivo

| Area | Score | Estado |
|------|-------|--------|
| Deuda Tecnica | **4/10** | Critico - Componentes god-object, duplicacion, tipos any |
| Arquitectura | **6/10** | Aceptable - Buena separacion de apps, store monolitico |
| Mantenibilidad | **5/10** | Medio - TS strict activo, falta formatter y linting Python |
| Cobertura de Pruebas | **2/10** | Critico - Solo 3 archivos de test, 0 tests backend, 0 E2E |

**Score promedio ponderado: 4.25/10**

### Top 3 acciones inmediatas:
1. **Dividir componentes criticos**: Separar `appStore.ts`, `CameraFeed.tsx` y `processors.ts` en modulos mas pequenos con responsabilidad unica.
2. **Aumentar cobertura de tests**: Llevar de 3 a al menos 15 archivos de test cubriendo store, procesadores ML y endpoints API.
3. **Estandarizar herramientas de calidad**: Agregar Prettier, configurar ruff para Python, y definir thresholds de coverage.
