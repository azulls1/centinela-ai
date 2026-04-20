# NXT Project Scorecard - Vision Human Insight

> **Evaluado por:** NXT Scorer (Sentinel)
> **Fecha:** 2026-04-05
> **Proyecto:** vision-human-insight (Vision Human Insight - IAGENTEK)
> **Version evaluada:** 1.0.0

---

## Resumen Ejecutivo

| Metrica         | Valor |
|-----------------|-------|
| Score Global    | **4.8 / 10** |
| Areas criticas  | Testing, Security, DevOps |
| Areas fuertes   | Architecture, Documentation |
| Riesgo general  | **ALTO** - El proyecto carece de tests, CI/CD y tiene debilidades de seguridad |

---

## Scorecard Detallado

| # | Area | Score | Hallazgos | Recomendaciones |
|---|------|-------|-----------|-----------------|
| 1 | **Code Quality** | **6 / 10** | TypeScript estricto habilitado (`strict: true`, `noUnusedLocals`, `noUnusedParameters`). ESLint configurado con plugins de React. Pydantic para validacion en backend. Patrones consistentes (Zustand store bien estructurado, FastAPI routers). Sin embargo: uso de `any` en varios puntos del frontend (`payload: any` en `supabase.ts`, `cocoSsdModel: any`, `faceDetector: any`, `poseDetector: any` en `processors.ts`). Variables `logError` declaradas como no-ops en lugar de usar el logger centralizado. | Eliminar todos los `any` y reemplazar con tipos concretos. Unificar logging usando `utils/logger` en todos los archivos (LivePage y DashboardPage definen `logError` local como no-op). Ejecutar `npm run lint` en CI para prevenir regresiones. |
| 2 | **Testing** | **1 / 10** | **No existe ni un solo archivo de test** en todo el proyecto. Ni unit tests, ni integration tests, ni E2E tests. No hay framework de testing configurado (no jest, vitest, pytest, ni playwright en dependencias). Cobertura: 0%. | Agregar Vitest para frontend y pytest para backend como minimo. Comenzar con tests para: `appStore.ts` (logica de estado), `supabase.ts` (API calls), `models.py` (validacion Pydantic), `events.py` (endpoints CRUD). Establecer un umbral minimo de cobertura (>60%) antes de cualquier deploy. |
| 3 | **Security** | **3 / 10** | `.gitignore` excluye `.env` correctamente. Backend valida existencia de variables de entorno al arrancar. Admin login usa bcrypt para password hashing. Pydantic valida inputs del API. **Problemas criticos:** (1) CORS permite `allow_methods=["*"]` y `allow_headers=["*"]` - demasiado permisivo. (2) `ADMIN_API_TOKEN` se expone como token estatico sin expiracion ni JWT. (3) `supabase_client.py` usa SERVICE_ROLE_KEY globalmente (bypasea RLS). (4) Endpoints de DELETE no tienen autenticacion. (5) `ai_summary.py` acepta base64 sin limitar tamano (riesgo DoS). (6) `infra/.env.production` y `infra/.env.production.backup` estan en el repo (archivos untracked pero presentes). (7) Credenciales de camaras externas (`auth_username`, `auth_password`) se almacenan sin cifrar. | Implementar JWT con expiracion para autenticacion admin. Restringir CORS a origenes especificos. Agregar middleware de autenticacion a endpoints sensibles (DELETE, admin). Limitar tamano de payload en `/validate-detections`. Usar Supabase anon key en frontend + RLS en lugar de service role. Cifrar credenciales de camaras. Agregar `.env.production*` al `.gitignore`. |
| 4 | **Performance** | **6 / 10** | ONNX Runtime Web excluido de optimizeDeps para carga dinamica. Modelos ML con lazy-loading (COCO-SSD se carga bajo demanda). Throttling de inserciones a BD (5s minimo). Sistema de presets de rendimiento adaptativos (performance/balanced/quality) que ajusta automaticamente FPS y modelos activos segun capacidad. `useMemo` y `useCallback` aplicados en componentes pesados. Eventos limitados a 100 en store. **Problemas:** No hay React.lazy/Suspense para code-splitting de paginas. No hay build analysis configurado. onnxruntime-web y tensorflow son librerias pesadas que se cargan en el bundle principal. | Implementar React.lazy + Suspense para las rutas (DashboardPage, SettingsPage, AdminPage). Configurar `rollup-plugin-visualizer` para analizar bundle size. Considerar dynamic import para tensorflow y onnxruntime-web. Agregar service worker para cache de modelos ML. |
| 5 | **Documentation** | **7 / 10** | README.md completo en espanol con instrucciones de instalacion, estructura del proyecto, uso y roadmap. Multiples docs especializados en `docs/` (ML training, optimizacion, integracion YOLO, modelos integrados). Guias SQL detalladas en `infra/supabase/`. Comentarios JSDoc en componentes principales. Pydantic models con `description` en cada campo. FastAPI endpoints con docstrings. **Carencias:** No hay API docs exportadas (aunque FastAPI genera Swagger automaticamente). No hay CONTRIBUTING.md ni guia de estilo. `packages/shared/` tiene README pero el paquete parece vacio o subutilizado. | Agregar link a `/docs` de FastAPI en el README. Crear CONTRIBUTING.md con guia de estilo. Documentar flujo de datos completo (frontend -> backend -> supabase). Agregar diagramas de arquitectura. |
| 6 | **DevOps** | **2 / 10** | Dockerfile funcional para el backend (Python 3.11-slim, sin usuario root especificado). docker-compose.yml define api + stream-gateway con restart policies, volumes y networking. **Problemas graves:** (1) No existe pipeline CI/CD (no hay `.github/workflows/`, ni GitLab CI, ni ningun archivo de CI). (2) No hay quality gates. (3) No hay Dockerfile para el frontend. (4) Docker no define healthchecks. (5) No hay configuracion de staging/production diferenciada en Docker. (6) El contenedor corre como root por defecto. (7) No hay rollback strategy. (8) No hay observabilidad (no Prometheus, no Grafana, no structured logging). | Crear pipeline CI/CD minimo: lint + type-check + tests en cada PR. Agregar Dockerfile para frontend (multi-stage build con nginx). Agregar `HEALTHCHECK` en Dockerfiles. Crear usuario no-root en contenedores. Configurar GitHub Actions o equivalente. Agregar structured logging (JSON) para integracion con plataformas de observabilidad. |
| 7 | **Architecture** | **7 / 10** | Monorepo bien organizado con workspaces (`apps/web`, `apps/api`, `apps/stream-gateway`, `packages/shared`). Clara separacion frontend/backend/infra. Backend sigue patron de routers con dependency injection (FastAPI Depends). Frontend usa Zustand para estado global con logica bien encapsulada. Tipos compartidos definidos en `types.ts`. Sistema de camaras multi-fuente (browser + external) con abstraccion limpia. Patron de presets de rendimiento bien disenado. **Debilidades:** `packages/shared` parece abandonado (no se importa). No hay capa de servicios en frontend (la logica de API esta directamente en `lib/supabase.ts`). El store (`appStore.ts`) es un archivo monolitico de 820+ lineas que deberia dividirse. | Dividir `appStore.ts` en slices (cameraSlice, sessionSlice, detectionSlice). Mover logica de API a una capa de servicios separada. Evaluar si `packages/shared` se usa o eliminarlo. Considerar React Context o providers para inyeccion de dependencias en el frontend. |
| 8 | **UX/UI** | **5 / 10** | Design system propio ("Forest Design System") con CSS custom properties y tema coherente. Framer Motion para animaciones (hover, tap, transitions). Lucide React para iconografia consistente. Recharts para graficas en dashboard. Navbar con indicadores activos. **Carencias:** Solo 17 atributos de accesibilidad (`aria-*`, `role`, `alt`) en todo el frontend - muy bajo para una app de esta complejidad. No hay skip-to-content, no hay focus management, no hay soporte de teclado aparente. No hay media queries especificas (depende solo de Tailwind). No hay dark mode. No hay loading skeletons (solo estados booleanos). Banner de privacidad presente (buena practica). | Agregar `aria-label`, `role`, y `aria-live` regions para detecciones en tiempo real. Implementar skip-to-content link. Agregar focus trapping en modales (SessionStartModal). Implementar loading skeletons. Agregar soporte responsive explicito para mobile. Considerar dark mode dado que el design system ya usa CSS variables. |
| 9 | **Error Handling** | **5 / 10** | 99 bloques try/catch en el frontend. Backend levanta HTTPException con codigos apropiados (400, 404, 500, 503). Frontend muestra mensajes de error en dashboard. Supabase client valida variables de entorno al arrancar. Throttling previene errores por sobrecarga de BD. Fallbacks cuando no hay datos (stats vacias, arrays vacios). **Problemas:** Muchos catch blocks solo hacen `logWarn` o retornan null silenciosamente. No hay error boundaries de React. No hay retry logic para llamadas API fallidas. La pagina de health check expone detalles de error internos (`str(e)`). No hay sistema de notificaciones de error al usuario consistente. | Agregar React Error Boundaries al menos en App level y por pagina. Implementar retry con backoff exponencial para llamadas API criticas. No exponer `str(e)` en respuestas de produccion (loguear internamente, retornar mensaje generico). Agregar toast/notification system para errores del usuario. |
| 10 | **Maintainability** | **5 / 10** | Dependencias modernas y actualizadas (React 18, Vite 5, FastAPI, Pydantic v2). Package-lock.json presente para builds reproducibles. Tipado fuerte con TypeScript + Pydantic. Estructura de carpetas clara e intuitiva. **Problemas:** `appStore.ts` tiene 820+ lineas (dificil de mantener). Duplicacion de tipos entre frontend `types.ts` y backend `models.py` sin sincronizacion automatica. `packages/shared` deberia resolver esto pero no se usa. Dependencias pesadas no necesariamente usadas (opencv-python-headless en requirements aunque el CV se hace en el navegador). No hay renovate/dependabot configurado. Scripts de `package.json` usan `cd` en lugar de workspace commands. Archivos sin trackear acumulandose (deployment_bundle.zip, varios scripts sueltos). | Dividir `appStore.ts` en multiples slices. Implementar generacion automatica de tipos desde OpenAPI schema de FastAPI. Configurar Dependabot/Renovate para actualizaciones automaticas. Limpiar archivos sin trackear y agregarlos a gitignore o al repo. Usar `npm workspace` commands en scripts del root package.json. Auditar requirements.txt y eliminar dependencias no usadas en produccion. |

---

## Score por Categoria

```
Code Quality      [======----]  6/10
Testing           [=---------]  1/10
Security          [===-------]  3/10
Performance       [======----]  6/10
Documentation     [=======---]  7/10
DevOps            [==--------]  2/10
Architecture      [=======---]  7/10
UX/UI             [=====-----]  5/10
Error Handling    [=====-----]  5/10
Maintainability   [=====-----]  5/10
────────────────────────────────────
PROMEDIO GLOBAL   [=====-----]  4.7/10
```

---

## Top 5 Acciones Prioritarias

| Prioridad | Accion | Impacto | Esfuerzo |
|-----------|--------|---------|----------|
| 1 | **Agregar testing framework + primeros tests** | Critico | Medio |
| 2 | **Crear pipeline CI/CD basico** (lint + typecheck + test) | Critico | Bajo |
| 3 | **Corregir vulnerabilidades de seguridad** (CORS, auth, service role key) | Critico | Medio |
| 4 | **Agregar React Error Boundaries + retry logic** | Alto | Bajo |
| 5 | **Implementar code-splitting** (React.lazy para rutas) | Medio | Bajo |

---

## Riesgos Identificados

| Riesgo | Severidad | Probabilidad | Descripcion |
|--------|-----------|-------------|-------------|
| Zero test coverage | CRITICA | CERTEZA | Cualquier cambio puede romper funcionalidad sin deteccion |
| Service role key en backend sin RLS | ALTA | ALTA | Un atacante que acceda al backend tiene control total de la BD |
| Sin CI/CD | ALTA | CERTEZA | No hay quality gates; codigo roto puede llegar a produccion |
| Admin token estatico sin expiracion | MEDIA | MEDIA | Token comprometido da acceso permanente al panel admin |
| Bundle size excesivo | MEDIA | ALTA | TensorFlow.js + ONNX Runtime + MediaPipe en bundle principal |

---

*Generado por NXT Scorer v3.8.0 - Evaluacion basada en evidencia del codigo fuente*
