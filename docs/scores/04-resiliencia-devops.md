# 04 - Resiliencia y DevOps

**Proyecto:** Vision Human Insight
**Fecha de evaluacion:** 2026-04-05
**Evaluador:** Claude Opus 4.6 (1M context)

---

## Resumen Ejecutivo

| Area | Puntuacion | Categoria |
|------|-----------|-----------|
| 1. Disponibilidad | 5/10 | Resiliencia |
| 2. MTTR | 3/10 | Resiliencia |
| 3. MTBF | 4/10 | Resiliencia |
| 4. Circuit Breakers | 1/10 | Resiliencia |
| 5. Backups & Recovery | 2/10 | Resiliencia |
| 6. Pipeline CI/CD | 3/10 | DevOps |
| 7. Lead Time | 2/10 | DevOps |
| 8. Rollback Capability | 1/10 | DevOps |
| 9. Observabilidad | 2/10 | DevOps |
| **Promedio Resiliencia** | **3.0/10** | |
| **Promedio DevOps** | **2.0/10** | |
| **Promedio General** | **2.6/10** | |

---

## RESILIENCIA

---

### 1. Disponibilidad - 5/10

#### Evidencia

| Elemento | Archivo | Estado |
|----------|---------|--------|
| Health endpoint API | `apps/api/main.py` linea 90 | Implementado (`/api/health`), verifica conexion a Supabase |
| Health endpoint Stream Gateway | `apps/stream-gateway/main.py` linea 199 | Implementado (`/health`), retorna conteo de streams activos |
| Docker healthcheck API | `infra/docker-compose.yml` lineas 19-23 | Configurado: interval 30s, timeout 5s, retries 3 |
| Docker healthcheck Stream Gateway | `infra/docker-compose.yml` lineas 42-45 | Configurado: interval 30s, timeout 5s, retries 3 |
| Dockerfile healthcheck API | `apps/api/Dockerfile` linea 14 | Presente con mismos parametros |
| Restart policy | `infra/docker-compose.yml` lineas 18, 39 | `restart: unless-stopped` en ambos servicios |
| Load balancer / redundancia | N/A | No existe |

#### Hallazgos

- Los healthchecks estan correctamente implementados tanto en los endpoints como en la configuracion Docker.
- El health endpoint de la API hace una verificacion real de la base de datos (query a `vishum_events`), lo cual es una buena practica.
- El health del stream-gateway es superficial: solo retorna status OK con conteo de streams, sin verificar estado real de ffmpeg.
- No hay ningun mecanismo de alta disponibilidad: un solo contenedor por servicio, sin load balancer, sin replicas.
- No hay frontend como servicio Docker en el compose (solo API y stream-gateway).

#### Recomendacion

- Agregar replicas en docker-compose o migrar a un orquestador (Docker Swarm / Kubernetes) para alta disponibilidad.
- Mejorar el healthcheck del stream-gateway para verificar que ffmpeg esta operativo.
- Agregar el frontend como servicio Docker con su propio healthcheck.
- Configurar un load balancer (Nginx/Traefik) delante de las replicas.

---

### 2. MTTR (Mean Time To Recovery) - 3/10

#### Evidencia

| Elemento | Archivo | Estado |
|----------|---------|--------|
| Restart policy Docker | `infra/docker-compose.yml` | `restart: unless-stopped` en ambos servicios |
| Runbooks / procedimientos | N/A | No existen |
| Troubleshooting documentado | `DEPLOYMENT.md` lineas 327-345 | Seccion basica con 3 escenarios |
| Logging estructurado | `apps/api/main.py`, routers | `logging.getLogger(__name__)` basico, sin formato estructurado |
| Monitoreo/alertas | N/A | No existe sistema de alertas |

#### Hallazgos

- La unica recuperacion automatica es el `restart: unless-stopped` de Docker, que reinicia contenedores caidos.
- No hay runbooks de incidentes, no hay procedimientos de escalacion, no hay scripts de diagnostico automatico.
- El troubleshooting en `DEPLOYMENT.md` es muy basico (3 escenarios con comandos manuales).
- No hay sistema de alertas que notifique cuando un servicio cae.
- Sin monitoreo activo, la deteccion de fallos depende enteramente de que alguien note el problema manualmente.

#### Recomendacion

- Crear runbooks detallados para los escenarios de fallo mas comunes (base de datos caida, servicio sin respuesta, disco lleno).
- Implementar alertas (al menos via webhook/email) cuando los healthchecks fallen.
- Agregar scripts de diagnostico automatico que se ejecuten al detectar un fallo.
- Documentar tiempos esperados de recuperacion para cada tipo de incidente.

---

### 3. MTBF (Mean Time Between Failures) - 4/10

#### Evidencia

| Elemento | Archivo | Estado |
|----------|---------|--------|
| Error handling API | `apps/api/routers/events.py`, `analytics.py`, etc. | try/except con `logger.exception()` y HTTPException 500 |
| Error handling frontend | `apps/web/src/lib/supabase.ts` | try/catch retorna null/array vacio en vez de propagar errores |
| ML model graceful degradation | `apps/web/src/lib/ml/processors.ts` lineas 97-131 | `Promise.allSettled` con fallbacks si un modelo falla |
| ML fallback pattern | `apps/web/src/lib/ml/processors.ts` lineas 395-457 | Fallback a COCO-SSD si MediaPipe falla; simulacion si todo falla |
| Input validation | `apps/stream-gateway/main.py` lineas 25-30 | Pydantic validators para campos positivos |
| Security headers | `apps/api/main.py` lineas 59-68 | Middleware con X-Content-Type-Options, X-Frame-Options, etc. |
| Throttling | `apps/web/src/lib/supabase.ts` lineas 50-51 | 5s minimo entre inserciones de eventos |

#### Hallazgos

- El manejo de errores en la API es consistente: todos los routers usan try/except con logging y retornan HTTP 500/503.
- El frontend tiene buen patron de degradacion: retorna valores vacios/null en lugar de crashear.
- El procesador ML tiene excelente degradacion gradual: usa `Promise.allSettled` para cargar modelos, y si un modelo falla, usa fallback a otro modelo o simulacion.
- El throttling de eventos (5s minimo) previene sobrecarga de la base de datos.
- Sin embargo, no hay proteccion contra memory leaks, no hay limites de rate en la API, no hay validacion exhaustiva de inputs en todos los endpoints.

#### Recomendacion

- Agregar rate limiting en la API (e.g., slowapi o fastapi-limiter).
- Implementar validacion de payload mas estricta con Pydantic en todos los endpoints.
- Agregar mecanismos de proteccion contra memory leaks en el procesamiento ML del frontend.
- Considerar timeouts explicitos en las llamadas a Supabase desde el backend.

---

### 4. Circuit Breakers - 1/10

#### Evidencia

| Elemento | Archivo | Estado |
|----------|---------|--------|
| Circuit breaker pattern | Busqueda global | No implementado en codigo aplicativo |
| Retry logic | Busqueda global | No implementado |
| Exponential backoff | Busqueda global | No implementado |
| Timeout handling API calls | `apps/web/src/lib/supabase.ts` | `fetch()` sin timeout configurado |
| Timeout handling sessions | `apps/web/src/lib/sessions.ts` | `fetch()` sin timeout configurado |
| Stream process timeout | `apps/stream-gateway/main.py` linea 64 | Solo timeout de 5s en `process.wait()` al detener ffmpeg |

#### Hallazgos

- No existe ninguna implementacion de circuit breaker en el codigo aplicativo real.
- Las llamadas `fetch()` del frontend a la API no tienen timeout configurado; si la API no responde, el frontend quedara colgado indefinidamente.
- No hay logica de reintentos en ninguna parte del codigo. Si una llamada a la API falla, simplemente retorna null/error.
- No hay backoff exponencial para llamadas a servicios externos (Supabase, OpenAI).
- El unico timeout encontrado es el de 5 segundos al detener un proceso ffmpeg en el stream-gateway.
- Nota: el archivo `.nxt/scores.json` afirma que hay circuit breakers "implementados y testeados", pero esto es metadata de una herramienta de evaluacion automatica, no codigo real del proyecto.

#### Recomendacion

- Implementar `AbortController` con timeout en todas las llamadas `fetch()` del frontend.
- Agregar una libreria de circuit breaker para las llamadas al backend (e.g., `opossum` en Node.js o patron manual).
- Implementar retry con backoff exponencial para llamadas a Supabase y OpenAI en el backend.
- Considerar un patron de bulkhead para aislar fallos entre servicios.

---

### 5. Backups & Recovery - 2/10

#### Evidencia

| Elemento | Archivo | Estado |
|----------|---------|--------|
| Database schema script | `infra/supabase/setup.sql` | Script de creacion completo (378 lineas) con tablas, indices, RLS, funciones |
| Migration scripts | N/A | No existen scripts de migracion incrementales |
| Migration rollback | N/A | No existe |
| Backup script | N/A | No existe ningun script de backup |
| Backup documentation | `DEPLOYMENT.md` linea 311 | Solo mencion "Backup de base de datos configurado (opcional)" en checklist |
| Supabase SQL scripts | `infra/supabase/` | Multiples scripts: `setup.sql`, `storage_setup.sql`, `verificar.sql`, `create_buckets.sql`, etc. |
| Data recovery procedure | N/A | No documentado |
| Volume persistence | `infra/docker-compose.yml` linea 52 | Volume `stream-data` para datos de streaming |

#### Hallazgos

- El schema de base de datos esta bien documentado en `setup.sql` con tablas, indices, RLS, funciones y comentarios.
- No hay sistema de migraciones incrementales (como Alembic, Flyway, o similar). Solo existe un script monolitico de creacion.
- No hay scripts de backup ni procedimientos de restauracion.
- No hay Point-in-Time Recovery configurado (Supabase lo ofrece en planes de pago).
- El backup esta mencionado como "opcional" en el checklist de deployment, lo cual indica que no se considera critico.
- No hay versionado del schema de base de datos.
- El volume Docker `stream-data` es efimero por defecto si el host se pierde.

#### Recomendacion

- Implementar un sistema de migraciones incrementales (Alembic para Python o scripts SQL numerados).
- Crear un script de backup automatizado con pg_dump o usar las funciones de backup de Supabase.
- Documentar un procedimiento de restauracion paso a paso.
- Habilitar Point-in-Time Recovery en Supabase.
- Agregar versionado semantico al schema de base de datos.

---

## DEVOPS

---

### 6. Pipeline CI/CD - 3/10

#### Evidencia

| Elemento | Archivo | Estado |
|----------|---------|--------|
| CI workflow | `.github/workflows/ci.yml` | Presente, 37 lineas |
| Frontend job | `ci.yml` lineas 10-23 | `npm ci` + `npm run build` |
| Backend job | `ci.yml` lineas 25-37 | `pip install` + `python -c "import main"` (solo verifica que el modulo carga) |
| Linting | N/A | No configurado en CI |
| Tests unitarios | N/A | No ejecutados en CI |
| Tests de integracion | N/A | No existen |
| Security scanning | N/A | No configurado (no hay SAST, DAST, ni dependency scanning) |
| Deploy automatico | N/A | No existe |
| Quality gates | N/A | No hay umbrales de calidad definidos |

#### Hallazgos

- El pipeline CI solo tiene 2 jobs: frontend y backend.
- El job de frontend solo compila (`npm run build`); no ejecuta linting, tests ni analisis de calidad.
- El job de backend es extremadamente basico: solo verifica que el modulo Python se importa sin error (`python -c "import main"`). No hay tests reales.
- No hay etapa de despliegue (CD). El deployment es completamente manual.
- No hay escaneo de seguridad de dependencias.
- No hay notificaciones de fallo del pipeline.
- El pipeline se ejecuta en push a `main` y `develop`, y en PRs a `main`.

#### Recomendacion

- Agregar linting al pipeline: ESLint para frontend, flake8/ruff para backend.
- Agregar ejecucion de tests unitarios (crear tests primero).
- Agregar escaneo de dependencias con `npm audit` y `pip-audit` o `safety`.
- Agregar un stage de deploy automatico (al menos a staging).
- Configurar quality gates que bloqueen el merge si el build falla.
- Agregar SAST basico (e.g., Semgrep, Bandit para Python).

---

### 7. Lead Time - 2/10

#### Evidencia

| Elemento | Archivo | Estado |
|----------|---------|--------|
| Deploy documentation | `DEPLOYMENT.md` | Manual completo de 348 lineas, 3 opciones de despliegue |
| Automated deploy | N/A | No existe |
| Deploy script | N/A | No existe script automatizado |
| Git history | `gitStatus` | Solo 1 commit inicial (todo staged, sin historial de releases) |
| Release frequency | N/A | No hay evidencia de releases |
| Environment management | `.env.production`, `.env.production.example` | Archivos de configuracion por entorno |

#### Hallazgos

- No hay historial de deploys ni releases. El repositorio muestra solo un commit inicial con todo el codigo.
- El despliegue es 100% manual, documentado en `DEPLOYMENT.md` con multiples pasos manuales.
- No hay scripts de deploy automatizado.
- La documentacion de despliegue es detallada (Docker, manual, systemd, Nginx, SSL), lo que es positivo pero insuficiente sin automatizacion.
- No hay entornos de staging definidos.
- El lead time estimado para un cambio seria alto: requiere SSH al servidor, pull manual, rebuild, restart.

#### Recomendacion

- Crear un script de deploy (`deploy.sh`) que automatice los pasos documentados.
- Implementar CD en el pipeline de GitHub Actions (al menos deploy a staging).
- Definir entornos claros (development, staging, production) con configuraciones separadas.
- Establecer una cadencia de releases regular.

---

### 8. Rollback Capability - 1/10

#### Evidencia

| Elemento | Archivo | Estado |
|----------|---------|--------|
| Git tags / releases | gitStatus | No hay tags ni releases |
| Docker image tagging | `infra/docker-compose.yml` | Build from source, sin tags de imagen |
| Database migration rollback | N/A | No existe sistema de migraciones |
| Rollback documentation | N/A | No documentado |
| Version pinning | `apps/api/Dockerfile` linea 1 | `python:3.11-slim` - version de base pinned |
| Feature flags | N/A | No implementados |

#### Hallazgos

- No hay mecanismo de rollback definido en ningun nivel.
- Las imagenes Docker se construyen desde el codigo fuente sin tags versionados. No se puede volver a una version anterior de la imagen.
- No hay sistema de migraciones de base de datos, por lo tanto no hay rollback de schema.
- No hay tags de Git ni releases en GitHub.
- No hay feature flags que permitan deshabilitar funcionalidad sin rollback.
- Un rollback requeriria `git revert` manual, rebuild de contenedores, y verificacion manual.
- Si un cambio de schema rompe datos, no hay forma de revertir automaticamente.

#### Recomendacion

- Implementar versionado semantico con tags de Git en cada release.
- Publicar imagenes Docker con tags de version en un registry (Docker Hub, GHCR).
- Implementar migraciones de base de datos con soporte de rollback (UP/DOWN).
- Documentar un procedimiento de rollback paso a paso.
- Considerar feature flags para deploys graduales.

---

### 9. Observabilidad - 2/10

#### Evidencia

| Elemento | Archivo | Estado |
|----------|---------|--------|
| Backend logging | `apps/api/main.py`, routers | `logging.getLogger(__name__)` con `logger.exception()` |
| Frontend logging | `apps/web/src/utils/logger.ts` | Logger personalizado, suprime logs en produccion |
| Structured logging | N/A | No implementado (logging basico de Python) |
| Prometheus metrics | N/A | No implementado |
| Grafana dashboards | N/A | No implementados |
| Distributed tracing | N/A | No implementado (OpenTelemetry, Jaeger, etc.) |
| Error tracking (Sentry) | N/A | No implementado |
| Log aggregation | N/A | No implementado |
| Health metrics endpoint | `apps/api/main.py` linea 90 | Solo status binario (healthy/unhealthy) |
| API info endpoint | `apps/api/main.py` linea 112 | Version y lista de features, no metricas |

#### Hallazgos

- El logging del backend usa el modulo estandar de Python sin formato estructurado (no JSON). Los logs son solo texto plano.
- El frontend tiene un logger personalizado que suprime todos los logs en produccion (`isDevEnvironment` check), lo que significa que en produccion no hay visibilidad de errores del lado del cliente.
- No hay metricas expuestas en formato Prometheus ni ningun otro formato.
- No hay sistema de tracing distribuido entre frontend, API y stream-gateway.
- No hay integracion con servicios de error tracking como Sentry.
- No hay agregacion de logs centralizada.
- El healthcheck solo retorna un booleano; no expone metricas como latencia, uso de memoria, conexiones activas, etc.

#### Recomendacion

- Configurar logging estructurado en formato JSON en el backend (python-json-logger).
- Integrar Sentry o similar para tracking de errores en frontend y backend.
- Exponer metricas Prometheus en `/metrics` (fastapi-prometheus-instrumentator).
- Agregar dashboards Grafana para visualizar metricas de la aplicacion.
- No suprimir logs de error en produccion en el frontend; al menos enviarlos a un servicio de error tracking.
- Considerar OpenTelemetry para tracing distribuido entre servicios.

---

## Matriz de Prioridades

| Prioridad | Area | Score | Impacto de Mejora |
|-----------|------|-------|-------------------|
| CRITICA | Circuit Breakers | 1/10 | Previene fallos en cascada entre servicios |
| CRITICA | Rollback Capability | 1/10 | Permite recuperacion rapida ante deploys defectuosos |
| ALTA | Observabilidad | 2/10 | Sin visibilidad no se pueden diagnosticar problemas |
| ALTA | Backups & Recovery | 2/10 | Riesgo de perdida de datos sin backup |
| ALTA | Lead Time | 2/10 | Deploy manual lento aumenta MTTR |
| MEDIA | Pipeline CI/CD | 3/10 | Pipeline minimo no previene regresiones |
| MEDIA | MTTR | 3/10 | Sin alertas ni runbooks, la recuperacion es lenta |
| MEDIA | MTBF | 4/10 | Buen patron de fallback en ML, pero falta proteccion en API |
| BAJA | Disponibilidad | 5/10 | Healthchecks presentes, falta redundancia |

---

## Plan de Accion Sugerido (Quick Wins)

1. **Agregar timeouts a todas las llamadas fetch()** del frontend con `AbortController` (Circuit Breakers, 1-2 horas).
2. **Configurar logging JSON** en el backend con `python-json-logger` (Observabilidad, 1 hora).
3. **Crear script de backup** con pg_dump o Supabase CLI (Backups, 2 horas).
4. **Agregar ESLint y flake8 al CI** pipeline (CI/CD, 1 hora).
5. **Crear tags de version** en Git y documentar procedimiento de rollback (Rollback, 1 hora).
6. **No suprimir errores en produccion** en el frontend logger (Observabilidad, 30 minutos).
