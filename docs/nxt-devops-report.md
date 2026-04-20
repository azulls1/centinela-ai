# NXT DevOps Assessment Report - Vision Human Insight

> **Generado por:** NXT DevOps v3.8.0
> **Fecha:** 2026-04-05
> **Proyecto:** vision-human-insight (Vision Human Insight)
> **Severidad global:** CRITICA - Se requieren acciones inmediatas

---

## Resumen Ejecutivo

El proyecto vision-human-insight presenta una arquitectura de monorepo con tres servicios (API FastAPI, Stream Gateway, Web React/Vite) y usa Supabase como base de datos. Existe una configuracion Docker basica funcional y un stack de produccion con Traefik. Sin embargo, se identificaron **hallazgos criticos de seguridad**, ausencia total de pipelines CI/CD, y multiples deficiencias en la configuracion de contenedores que deben resolverse antes de considerar el proyecto listo para produccion.

---

## 1. Docker Configuration

### 1.1 API Dockerfile (`apps/api/Dockerfile`)

**Estado:** Funcional pero con deficiencias significativas.

| Problema | Severidad | Detalle |
|----------|-----------|---------|
| Sin multi-stage build | Media | Se instalan todas las dependencias en una sola capa, incrementando el tamano de la imagen |
| Ejecuta como root | Alta | No se define un usuario no-root; un exploit en la aplicacion obtendria permisos de root dentro del contenedor |
| Sin HEALTHCHECK | Alta | Docker no puede determinar si el proceso esta sano (el endpoint `/api/health` existe pero Docker no lo usa) |
| Sin .dockerignore | Media | Se copia todo el contexto incluyendo `__pycache__`, `.env`, logs, etc. |
| Sin pinning de imagen base | Baja | `python:3.11-slim` no fija un digest; builds futuros podrian romper |

### 1.2 Stream Gateway Dockerfile (`apps/stream-gateway/Dockerfile`)

**Estado:** Mejor que el API (tiene `PYTHONDONTWRITEBYTECODE` y `PYTHONUNBUFFERED`), pero comparte los mismos problemas fundamentales.

| Problema | Severidad | Detalle |
|----------|-----------|---------|
| Ejecuta como root | Alta | Mismo problema que API |
| Sin HEALTHCHECK | Alta | El endpoint `/health` existe en el codigo pero no se configura en Docker |
| Sin .dockerignore | Media | Podria copiar el directorio `streams/` y `__pycache__/` |

### 1.3 Frontend Dockerfile - INEXISTENTE

**Estado:** NO EXISTE. No hay `apps/web/Dockerfile`.

Esto significa que:
- No se puede desplegar el frontend como contenedor
- No hay build reproducible para produccion
- El stack de produccion (`infra/stack.yml`) no incluye servicio web
- El deploy del frontend se hace de forma manual o externa (no documentada)

**Recomendacion:** Crear un Dockerfile multi-stage con nginx para servir los assets estaticos:
```
Stage 1: node:20-alpine -> npm ci && npm run build
Stage 2: nginx:alpine -> copiar dist/ a /usr/share/nginx/html
```

### 1.4 Docker Compose (`infra/docker-compose.yml`)

**Estado:** Funcional para desarrollo local.

| Aspecto | Estado | Notas |
|---------|--------|-------|
| Servicios definidos | OK | api + stream-gateway |
| Red personalizada | OK | bridge network `vision-network` |
| Volumen nombrado | OK | `stream-data` para streams |
| Hot-reload | OK | Volumenes montados + `--reload` |
| Health checks | FALTA | Ningun servicio tiene healthcheck |
| Servicio web | FALTA | El frontend no esta en docker-compose |
| Dependencias entre servicios | FALTA | No hay `depends_on` ni `condition: service_healthy` |

### 1.5 Stack de Produccion (`infra/stack.yml`)

**Estado:** Bien estructurado para Docker Swarm con Traefik.

| Aspecto | Estado | Notas |
|---------|--------|-------|
| Resource limits | OK | CPU y memoria definidos |
| Restart policy | OK | `on-failure` |
| Traefik labels | OK | TLS con Let's Encrypt |
| Red externa | OK | `iagenteknet` |
| Health checks | FALTA | Ninguno definido en el stack |
| Logging | FALTA | Sin configuracion de logging (max-size, driver) |
| Frontend | FALTA | No hay servicio web en el stack |

---

## 2. CI/CD Pipeline - INEXISTENTE

**Estado:** CRITICO. No se encontro ningun archivo de CI/CD en el proyecto.

- No existe `.github/workflows/` (GitHub Actions)
- No existe `.gitlab-ci.yml` (GitLab CI)
- No existe `Jenkinsfile`
- No existe ningun sistema de integracion continua

### Impacto

- No hay validacion automatica de codigo (lint, type-check, tests)
- No hay build automatizado de imagenes Docker
- No hay deploy automatizado
- No hay escaneo de seguridad
- Los deploys son manuales y propensos a errores

### Recomendacion

Crear al minimo dos workflows de GitHub Actions:

1. **CI Pipeline** (en push/PR a main): lint, type-check, build web, build Docker images
2. **CD Pipeline** (en tags `v*`): build, push imagenes a registry, deploy a produccion

---

## 3. Environment Management

### 3.1 HALLAZGO CRITICO DE SEGURIDAD

**Archivos con secretos comprometidos en el repositorio:**

| Archivo | Secretos expuestos | Severidad |
|---------|-------------------|-----------|
| `infra/.env.production` | SUPABASE_SERVICE_ROLE_KEY, OPENAI_API_KEY, ADMIN_API_TOKEN | **CRITICA** |
| `apps/web/.env.production` | VITE_SUPABASE_ANON_KEY, VITE_ADMIN_API_TOKEN | **ALTA** |
| `infra/.env.production.backup` | Posible copia de secretos | **ALTA** |

**Detalles especificos:**

1. **`infra/.env.production`** contiene:
   - `SUPABASE_SERVICE_ROLE_KEY` completo (clave con permisos de administrador sobre toda la base de datos)
   - `OPENAI_API_KEY` completo con prefijo `sk-proj-` (puede generar cargos en la cuenta de OpenAI)
   - `ADMIN_API_TOKEN` en texto plano con valor trivial (`mi-token-super-secreto-admin-2024-xyz123`)

2. **`apps/web/.env.production`** contiene:
   - `VITE_ADMIN_API_TOKEN` con el mismo token trivial
   - URLs de produccion expuestas

### Acciones inmediatas requeridas:

1. **ROTAR TODOS LOS SECRETOS INMEDIATAMENTE:**
   - Generar nuevo `SUPABASE_SERVICE_ROLE_KEY` en el panel de Supabase
   - Revocar y regenerar la `OPENAI_API_KEY` en platform.openai.com
   - Cambiar el `ADMIN_API_TOKEN` por un valor criptograficamente seguro
2. **Eliminar los archivos `.env.production` del historial de Git** usando `git filter-branch` o BFG Repo Cleaner
3. **Agregar al `.gitignore`:**
   ```
   .env.production
   .env.production.backup
   infra/.env.production
   infra/.env.production.backup
   ```
4. **Usar GitHub Secrets** o un gestor de secretos para variables de produccion

### 3.2 Estado del .gitignore

El `.gitignore` actual tiene reglas basicas pero **no cubre todos los casos**:

| Regla presente | Estado |
|---------------|--------|
| `.env` | SI |
| `.env.local` | SI |
| `.env.*.local` | SI |
| `.env.production` | **NO - FALTA** |
| `.env.production.backup` | **NO - FALTA** |
| `infra/.env.production` | **NO - FALTA** |
| `*.pem`, `*.key` | **NO - FALTA** |
| `docker-compose.override.yml` | **NO - FALTA** |

### 3.3 Variables de entorno - Inventario

| Variable | Servicio | Tipo | Gestion actual |
|----------|----------|------|----------------|
| SUPABASE_URL | API, Web | Config | .env files |
| SUPABASE_ANON_KEY | Web | Secret | .env.production (expuesto) |
| SUPABASE_SERVICE_ROLE_KEY | API | Secret | .env.production (expuesto) |
| OPENAI_API_KEY | API | Secret | .env.production (expuesto) |
| ADMIN_API_TOKEN | API, Web | Secret | .env.production (expuesto) |
| FRONTEND_URL | API | Config | .env / stack.yml |
| STREAM_GATEWAY_* | Stream GW | Config | .env / stack.yml |
| SESSION_* | API | Config | stack.yml con defaults |

---

## 4. Deployment Readiness

### 4.1 Scorecard

| Criterio | Estado | Peso | Puntuacion |
|----------|--------|------|------------|
| Dockerfiles funcionales | Parcial | 15% | 7/15 |
| Frontend containerizado | No | 10% | 0/10 |
| CI/CD pipeline | No | 20% | 0/20 |
| Health checks en Docker | No | 10% | 0/10 |
| Secrets management | Critico | 20% | 0/20 |
| Logging configurado | No | 5% | 0/5 |
| Build optimization | Parcial | 5% | 2/5 |
| Monitoring/alertas | No | 5% | 0/5 |
| Documentacion de deploy | Parcial | 5% | 3/5 |
| Rollback strategy | No | 5% | 0/5 |
| **TOTAL** | | **100%** | **12/100** |

### 4.2 Build Optimization

**Frontend (Vite):**
- `vite.config.ts` es minimo; no tiene configuracion de chunk splitting, compression, ni optimizacion de assets
- `onnxruntime-web` excluido de optimizeDeps (correcto para carga dinamica)
- No hay `vite.config.ts` de produccion separado
- Dependencias pesadas: TensorFlow.js, ONNX Runtime, MediaPipe -- el bundle sera grande sin code splitting

**Backend (Python):**
- `requirements.txt` incluye dependencias opcionales pesadas (opencv, numpy, Pillow, reportlab) que se instalan siempre
- No hay multi-stage build para separar dependencias de build vs runtime
- No hay `requirements-prod.txt` separado

### 4.3 Produccion - Stack Analysis

El archivo `infra/stack.yml` esta orientado a Docker Swarm con Traefik como reverse proxy:
- Dominio: `apicentinela.iagentek.com.mx`
- TLS via Let's Encrypt (correcto)
- Red externa `iagenteknet` (asume infraestructura Traefik existente)
- Resource limits definidos (1 CPU, 1GB RAM por servicio)
- Solo 1 replica por servicio (sin alta disponibilidad)

---

## 5. Health Checks - AUSENTES

### 5.1 Endpoints existentes en el codigo

| Servicio | Endpoint | Ruta | Estado en Docker |
|----------|----------|------|-----------------|
| API | Health check | `/api/health` | No configurado |
| Stream Gateway | Health check | `/health` | No configurado |
| Web | N/A | N/A | No existe contenedor |

### 5.2 Recomendacion

Agregar en cada Dockerfile:
```dockerfile
# API
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/health')" || exit 1

# Stream Gateway
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8081/health')" || exit 1
```

Agregar en `docker-compose.yml`:
```yaml
services:
  api:
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/health')"]
      interval: 30s
      timeout: 5s
      retries: 3
      start_period: 10s
```

Agregar en `stack.yml`:
```yaml
services:
  api:
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/health')"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 15s
```

---

## 6. Frontend Dockerfile - FALTANTE

No existe `apps/web/Dockerfile`. Se recomienda crear el siguiente archivo:

```dockerfile
# Stage 1: Build
FROM node:20-alpine AS builder
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm ci
COPY . .
RUN npm run build

# Stage 2: Serve
FROM nginx:alpine AS runner
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Non-root user
RUN chown -R nginx:nginx /usr/share/nginx/html
USER nginx

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:80/ || exit 1
```

Tambien se requiere un `apps/web/nginx.conf` para manejar SPA routing:

```nginx
server {
    listen 80;
    root /usr/share/nginx/html;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /assets/ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

---

## 7. Volume Management & Data Persistence

### 7.1 Volumenes definidos

| Volumen | Servicio | Tipo | Proposito | Backup |
|---------|----------|------|-----------|--------|
| `stream-data` | stream-gateway | Named volume | Segmentos HLS temporales | No necesario (efimero) |
| Source mounts (dev) | api, stream-gw | Bind mount | Hot-reload en desarrollo | N/A |

### 7.2 Analisis

- **Datos persistentes:** La aplicacion usa Supabase (externo) como base de datos, por lo que no hay volumenes de BD que gestionar localmente. Esto es correcto.
- **Stream data:** Los segmentos HLS son temporales por naturaleza (`delete_segments` flag en ffmpeg). El volumen `stream-data` en stack.yml usa `driver: local`, lo cual es correcto.
- **Riesgo:** Si se escala stream-gateway a mas de 1 replica, cada replica tendra su propio volumen local y los streams no seran compartidos. Se necesitaria un volumen compartido (NFS, EFS) o un object storage.

### 7.3 Datos faltantes

- No hay estrategia de backup documentada
- No hay limpieza automatica de streams huerfanos (si ffmpeg muere, los archivos quedan)
- El stream-gateway limpia archivos al detener un stream, pero no hay un job de limpieza periodica

---

## 8. Plan de Accion Priorizado

### Prioridad CRITICA (Hacer AHORA)

| # | Accion | Esfuerzo |
|---|--------|----------|
| 1 | **Rotar todos los secretos** expuestos en `.env.production` | 30 min |
| 2 | **Eliminar secretos del historial de Git** (BFG Repo Cleaner) | 1 hora |
| 3 | **Actualizar .gitignore** para cubrir `.env.production*` | 5 min |
| 4 | **Cambiar ADMIN_API_TOKEN** a un valor seguro (>= 32 chars aleatorios) | 10 min |

### Prioridad ALTA (Esta semana)

| # | Accion | Esfuerzo |
|---|--------|----------|
| 5 | Crear Dockerfile para frontend (multi-stage con nginx) | 2 horas |
| 6 | Agregar health checks a todos los Dockerfiles | 1 hora |
| 7 | Agregar health checks a docker-compose.yml y stack.yml | 30 min |
| 8 | Crear CI pipeline basico (GitHub Actions: lint + build) | 2 horas |
| 9 | Agregar usuario no-root a Dockerfiles de API y stream-gateway | 30 min |

### Prioridad MEDIA (Este sprint)

| # | Accion | Esfuerzo |
|---|--------|----------|
| 10 | Crear CD pipeline (build + push imagenes + deploy) | 4 horas |
| 11 | Crear `.dockerignore` para cada servicio | 30 min |
| 12 | Configurar logging en stack.yml (json-file con max-size) | 30 min |
| 13 | Optimizar Dockerfiles con multi-stage builds | 2 horas |
| 14 | Agregar Vite build optimization (chunk splitting, compression) | 2 horas |
| 15 | Agregar servicio web al stack.yml de produccion | 1 hora |

### Prioridad BAJA (Proximo sprint)

| # | Accion | Esfuerzo |
|---|--------|----------|
| 16 | Configurar monitoring (metricas de salud, alertas) | 4 horas |
| 17 | Crear runbook de deploy documentado | 2 horas |
| 18 | Implementar rollback automatizado | 3 horas |
| 19 | Agregar escaneo de seguridad al CI (Snyk/Trivy) | 2 horas |
| 20 | Implementar limpieza periodica de streams huerfanos | 1 hora |

---

## Arquitectura Actual vs Recomendada

```
ACTUAL:
  Developer -> manual build -> manual docker push -> manual deploy
  Sin CI/CD, sin health checks, secretos en repo

RECOMENDADA:
  Developer -> PR -> GitHub Actions CI (lint, test, build)
           -> merge -> GitHub Actions CD (build images, push, deploy)
           -> Docker Swarm con health checks
           -> Monitoring + alertas
           -> Secretos en GitHub Secrets / Vault
```

---

*NXT DevOps v3.8.0 - Del Codigo a Produccion*
