# SKILL: Containers y Docker

> **Version:** 3.8.0
> **Trigger:** Gestion de contenedores Docker y Kubernetes
> **Agente:** nxt-devops, nxt-infra
> **Track:** shared

## Proposito
Crear y gestionar contenedores Docker optimizados, seguros y listos
para produccion.

## Cuando se Activa
- Crear Dockerfiles
- Optimizar imagenes
- Docker Compose setup
- Multi-stage builds
- Container security

## Instrucciones

### 1. Dockerfile Best Practices

#### Orden de Capas (Cache Optimization)
```dockerfile
# Las capas que cambian menos van primero
FROM node:20-alpine

# 1. Metadata (casi nunca cambia)
LABEL maintainer="team@company.com"

# 2. System dependencies (rara vez cambian)
RUN apk add --no-cache dumb-init

# 3. Working directory
WORKDIR /app

# 4. Package files (cambian cuando hay nuevas deps)
COPY package*.json ./

# 5. Install dependencies
RUN npm ci --only=production

# 6. Application code (cambia frecuentemente)
COPY . .

# 7. Build (si aplica)
RUN npm run build

# 8. Runtime config
EXPOSE 3000
CMD ["dumb-init", "node", "dist/main.js"]
```

### 2. Multi-Stage Builds

#### Node.js Application
```dockerfile
# ============ Build Stage ============
FROM node:20-alpine AS builder

WORKDIR /app

# Install ALL dependencies (including devDeps)
COPY package*.json ./
RUN npm ci

# Copy source and build
COPY . .
RUN npm run build

# Prune dev dependencies
RUN npm prune --production

# ============ Production Stage ============
FROM node:20-alpine AS runner

# Security: non-root user
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 appuser

WORKDIR /app

# Copy only what's needed
COPY --from=builder --chown=appuser:nodejs /app/dist ./dist
COPY --from=builder --chown=appuser:nodejs /app/node_modules ./node_modules
COPY --from=builder --chown=appuser:nodejs /app/package.json ./

# Use non-root user
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:3000/health || exit 1

EXPOSE 3000

CMD ["node", "dist/main.js"]
```

#### Python Application
```dockerfile
# ============ Build Stage ============
FROM python:3.12-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ============ Production Stage ============
FROM python:3.12-slim AS runner

# Create non-root user
RUN useradd --create-home --shell /bin/bash appuser

WORKDIR /app

# Copy virtual environment
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy application
COPY --chown=appuser:appuser . .

USER appuser

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app:create_app()"]
```

#### Go Application
```dockerfile
# ============ Build Stage ============
FROM golang:1.22-alpine AS builder

WORKDIR /app

# Download dependencies
COPY go.mod go.sum ./
RUN go mod download

# Build
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -ldflags="-s -w" -o /app/server ./cmd/server

# ============ Production Stage ============
FROM scratch

# Copy CA certificates for HTTPS
COPY --from=builder /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/

# Copy binary
COPY --from=builder /app/server /server

EXPOSE 8080

ENTRYPOINT ["/server"]
```

### 3. Docker Compose

#### Development Environment
```yaml
# docker-compose.yml
version: '3.8'

services:
  app:
    build:
      context: .
      dockerfile: Dockerfile.dev
    ports:
      - "3000:3000"
    volumes:
      - .:/app
      - /app/node_modules  # Exclude node_modules
    environment:
      - NODE_ENV=development
      - DATABASE_URL=postgres://user:pass@db:5432/app
      - REDIS_URL=redis://redis:6379
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_started

  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
      POSTGRES_DB: app
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user -d app"]
      interval: 5s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

#### Production Compose
```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  app:
    image: ${REGISTRY}/app:${VERSION}
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 256M
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3
    environment:
      - NODE_ENV=production
    secrets:
      - db_password
      - api_key
    healthcheck:
      test: ["CMD", "wget", "-q", "--spider", "http://localhost:3000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

secrets:
  db_password:
    external: true
  api_key:
    external: true
```

### 4. Optimizacion de Imagenes

#### Reducir Tamano
```dockerfile
# Usar alpine
FROM node:20-alpine  # ~130MB vs ~900MB

# Instalar solo lo necesario
RUN apk add --no-cache <package>

# Limpiar cache
RUN npm cache clean --force

# Usar .dockerignore
# .dockerignore
node_modules
.git
*.md
tests/
coverage/
.env*
```

#### Comparativa de Tamanos
| Base Image | Size |
|------------|------|
| node:20 | ~900MB |
| node:20-slim | ~200MB |
| node:20-alpine | ~130MB |
| distroless | ~20MB |
| scratch (Go) | ~10MB |

### 5. Seguridad

#### Security Checklist
```dockerfile
# 1. No usar root
USER appuser

# 2. Imagen base minima
FROM node:20-alpine

# 3. No secrets en imagen
# Usar build args o runtime env

# 4. Pin versions
FROM node:20.10.0-alpine3.19

# 5. Scan vulnerabilities
# docker scout cves myimage

# 6. Read-only filesystem
# docker run --read-only myimage

# 7. No privileged
# docker run --security-opt=no-new-privileges myimage
```

#### Hadolint (Dockerfile Linter)
```bash
# Instalar
brew install hadolint

# Ejecutar
hadolint Dockerfile

# Reglas comunes
# DL3008: Pin versions in apt-get
# DL3018: Pin versions in apk add
# DL3025: Use JSON form of CMD
# DL4006: Set SHELL option -o pipefail
```

### 6. Comandos Utiles

```bash
# Build
docker build -t myapp:latest .
docker build --target builder -t myapp:builder .
docker build --no-cache -t myapp:latest .

# Run
docker run -d -p 3000:3000 --name myapp myapp:latest
docker run --rm -it myapp:latest sh  # Debug

# Inspect
docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}"
docker history myapp:latest
docker inspect myapp:latest

# Cleanup
docker system prune -a
docker image prune -a
docker volume prune

# Multi-platform
docker buildx build --platform linux/amd64,linux/arm64 -t myapp:latest .

# Security scan
docker scout cves myapp:latest
trivy image myapp:latest
```

### 7. Checklist

#### Dockerfile
- [ ] Multi-stage build
- [ ] Usuario no-root
- [ ] Imagen base alpine/slim
- [ ] Cache optimizado
- [ ] .dockerignore configurado
- [ ] HEALTHCHECK definido
- [ ] Versiones pinneadas

#### Seguridad
- [ ] No secrets en imagen
- [ ] Imagen escaneada
- [ ] Hadolint sin errores
- [ ] No capabilities extra

#### Compose
- [ ] Health checks
- [ ] Resource limits
- [ ] Restart policy
- [ ] Volume persistente
- [ ] Network isolation

## Configuraciones de Produccion

### .hadolint.yaml
```yaml
ignored:
  - DL3008  # Pin versions in apt get install
  - DL3013  # Pin versions in pip install
trustedRegistries:
  - docker.io
  - gcr.io
```

### Docker Scout / Trivy Scan
```bash
# Escanear vulnerabilidades
docker scout cves myapp:latest
# O con Trivy (open source)
trivy image myapp:latest --severity HIGH,CRITICAL

# En CI (GitHub Actions)
- name: Run Trivy vulnerability scanner
  uses: aquasecurity/trivy-action@master
  with:
    image-ref: 'myapp:latest'
    format: 'sarif'
    severity: 'CRITICAL,HIGH'
```

### docker-compose.prod.yml
```yaml
services:
  app:
    image: myapp:latest
    restart: unless-stopped
    deploy:
      resources:
        limits: {memory: 512M, cpus: '0.5'}
        reservations: {memory: 256M}
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    logging:
      driver: json-file
      options: {max-size: "10m", max-file: "3"}
```

## Comandos de Ejemplo

```
"Crea un Dockerfile optimizado para Node.js"
"Convierte este Dockerfile a multi-stage"
"Genera docker-compose para desarrollo"
"Como reduzco el tamano de esta imagen?"
"Configura health check para este contenedor"
```
