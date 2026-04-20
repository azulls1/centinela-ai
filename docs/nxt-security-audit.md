# Auditoria de Seguridad - Vision Human Insight

## Resumen Ejecutivo
- **Fecha:** 2026-04-05
- **Auditor:** NXT CyberSec v3.8.0
- **Alcance:** Revision completa del proyecto vision-human-insight (API backend, frontend web, infraestructura Docker, configuracion Supabase)
- **Criticidad General:** ALTA

Se identificaron **4 hallazgos criticos**, **5 altos**, y **6 medios**. Los mas urgentes involucran credenciales de produccion expuestas en archivos versionados, un token administrativo debil hardcodeado, y la ausencia de autenticacion en la mayoria de los endpoints de la API.

---

## Hallazgos

### Criticos

| ID | Vulnerabilidad | Ubicacion | Descripcion | Remediacion |
|----|---------------|-----------|-------------|-------------|
| C-01 | Credenciales de produccion expuestas en repositorio | `infra/.env.production` (untracked pero presente) | El archivo contiene la **SUPABASE_SERVICE_ROLE_KEY**, la **OPENAI_API_KEY** (`sk-proj-3-JGCGxF...`), y el **ADMIN_API_TOKEN** en texto plano. Este archivo NO esta listado en `.gitignore` (solo `.env`, `.env.local` y `.env.*.local` estan excluidos). Cualquier `git add .` lo incluiria en el historial. | 1. Agregar `*.env.production` y `infra/.env.production*` a `.gitignore` inmediatamente. 2. Rotar TODAS las credenciales expuestas (Supabase service role key, OpenAI API key, admin token). 3. Usar un gestor de secretos (Vault, AWS Secrets Manager, o variables de entorno del hosting). |
| C-02 | Supabase Service Role Key expuesta en frontend env | `apps/web/.env.production:4` | El archivo `apps/web/.env.production` contiene `VITE_ADMIN_API_TOKEN=mi-token-super-secreto-admin-2024-xyz123`. Aunque el anon key es aceptable para frontend, el admin token es un secreto que no deberia estar en variables `VITE_*` ya que Vite las embebe en el bundle del cliente, haciendo el token visible para cualquier usuario que inspeccione el JavaScript. | 1. Eliminar `VITE_ADMIN_API_TOKEN` del frontend. 2. El admin token debe obtenerse SOLO a traves del flujo de login (ya implementado en `/sessions/admin/auth/login`). 3. Agregar `apps/web/.env.production` a `.gitignore`. |
| C-03 | Token administrativo debil y estatico | `apps/api/routers/sessions.py:30`, `infra/.env.production:5` | El `ADMIN_API_TOKEN` es un string estatico (`mi-token-super-secreto-admin-2024-xyz123`) que se compara directamente. No hay rotacion, no hay expiracion, y el mismo token se retorna al hacer login exitoso (linea 78). Esto significa que una vez obtenido, el token tiene validez indefinida. | 1. Implementar tokens JWT con expiracion (15-60 min). 2. Generar tokens firmados por sesion al hacer login, no retornar un secreto estatico del servidor. 3. Usar un token criptograficamente fuerte (minimo 256 bits de entropia). |
| C-04 | Backend usa Supabase service_role_key sin restriccion | `apps/api/supabase_client.py:14-23` | El backend usa exclusivamente `SUPABASE_SERVICE_ROLE_KEY` que bypassa completamente RLS (Row Level Security). Cualquier endpoint del backend tiene acceso total a todas las tablas sin restriccion. Si un endpoint tiene una vulnerabilidad, un atacante obtiene acceso a TODOS los datos. | 1. Usar el anon key + JWT del usuario para operaciones regulares. 2. Reservar service_role_key solo para operaciones administrativas especificas. 3. Aplicar validacion de permisos a nivel de aplicacion en cada endpoint. |

### Altos

| ID | Vulnerabilidad | Ubicacion | Descripcion | Remediacion |
|----|---------------|-----------|-------------|-------------|
| A-01 | Sin autenticacion en endpoints publicos | `apps/api/routers/events.py`, `analytics.py`, `reports.py`, `external_cameras.py` | Los endpoints de eventos (`POST /api/events`, `GET /api/events`, `DELETE /api/events/{id}`), analytics, reportes y camaras externas no requieren ningun tipo de autenticacion. Cualquier persona puede crear, leer y eliminar eventos, y registrar camaras externas. | 1. Agregar middleware de autenticacion (JWT o API key) a todos los endpoints. 2. Implementar roles (usuario anonimo de demo vs. admin) con permisos diferenciados. 3. Como minimo, proteger `DELETE` y endpoints de camaras externas. |
| A-02 | Sin rate limiting en la API | `apps/api/main.py` (global) | No hay rate limiting en ningun endpoint. Esto expone la API a: abuso de recursos (ataques de denegacion de servicio), consumo excesivo de la API de OpenAI (costo financiero), y spam de eventos falsos. El endpoint `/api/ai/generate-summary` es especialmente peligroso ya que genera costos con OpenAI por cada invocacion. | 1. Instalar `slowapi` o equivalente para FastAPI. 2. Aplicar limites por IP: endpoints generales (60 req/min), endpoints de OpenAI (5 req/min), admin login (5 req/min con lockout). |
| A-03 | Credenciales de camaras RTSP en texto plano en BD | `apps/api/routers/external_cameras.py:66-70`, `infra/supabase/setup.sql:57-58` | Las credenciales de autenticacion de camaras externas (`auth_username`, `auth_password`) se almacenan en texto plano en la tabla `vishum_external_cameras`. Tambien se transmiten en texto plano al stream gateway. | 1. Cifrar las credenciales en reposo (AES-256 o similar). 2. Usar columnas de tipo `bytea` con cifrado a nivel de aplicacion. 3. Transmitir al gateway solo cuando sea necesario, no almacenar en BD si se puede evitar. |
| A-04 | Sin validacion de brute force en login admin | `apps/api/routers/sessions.py:42-78` | El endpoint `/sessions/admin/auth/login` no tiene proteccion contra ataques de fuerza bruta. No hay: limite de intentos fallidos, delay progresivo, bloqueo temporal de cuenta, ni logging de intentos fallidos. | 1. Implementar rate limiting especifico para login (5 intentos/minuto por IP). 2. Agregar delay progresivo despues de 3 intentos fallidos. 3. Registrar intentos fallidos con IP y timestamp para auditoria. |
| A-05 | CORS permite metodos y headers arbitrarios | `apps/api/main.py:43-49` | La configuracion CORS usa `allow_methods=["*"]` y `allow_headers=["*"]`, lo cual es mas permisivo de lo necesario. Ademas, automaticamente agrega la version HTTP alternativa de `FRONTEND_URL` (lineas 38-41), ampliando la superficie de ataque. | 1. Restringir `allow_methods` a los metodos realmente usados: `["GET", "POST", "DELETE", "OPTIONS"]`. 2. Restringir `allow_headers` a los necesarios: `["Content-Type", "x-admin-token", "Authorization"]`. 3. Eliminar la logica de agregar automaticamente el esquema alternativo (http/https). En produccion solo usar HTTPS. |

### Medios

| ID | Vulnerabilidad | Ubicacion | Descripcion | Remediacion |
|----|---------------|-----------|-------------|-------------|
| M-01 | Sin Content Security Policy ni security headers | `apps/api/main.py` (global), frontend | La API no configura security headers (X-Content-Type-Options, X-Frame-Options, Strict-Transport-Security, CSP). El frontend tampoco los configura. | 1. Agregar middleware de security headers a FastAPI. 2. Configurar CSP en el frontend via `index.html` meta tags o servidor proxy. 3. Agregar HSTS header cuando se use HTTPS. |
| M-02 | Excepcion interna expuesta a clientes | Multiples routers | Los bloques `except Exception as e: raise HTTPException(status_code=500, detail=str(e))` exponen mensajes de error internos al cliente, incluyendo potencialmente stack traces, nombres de tablas, y detalles de conexion. Ver `events.py:42`, `analytics.py:91`, `ai_summary.py:143-147`. | 1. Registrar el error completo en logs del servidor. 2. Retornar mensajes genericos al cliente: `"Error interno del servidor"`. 3. Usar un exception handler global en FastAPI. |
| M-03 | Docker corre como root | `apps/api/Dockerfile` | El Dockerfile no especifica un usuario no-root. El contenedor se ejecuta como root por defecto, aumentando el impacto de cualquier vulnerabilidad de ejecucion de codigo. | 1. Agregar `RUN adduser --disabled-password --gecos '' appuser` y `USER appuser` al Dockerfile. |
| M-04 | Reload habilitado en docker-compose de produccion | `infra/docker-compose.yml:19`, `apps/api/main.py:122` | El flag `--reload` esta presente tanto en docker-compose como en el script de ejecucion. En produccion, el hot-reload observa el filesystem buscando cambios, consume recursos innecesariamente y puede ser un vector de ataque si se logra escribir archivos en el contenedor. | 1. Crear un `docker-compose.prod.yml` sin `--reload` ni volumes de codigo. 2. Eliminar `reload=True` del bloque `__main__` o protegerlo con `if os.getenv("ENV") == "development"`. |
| M-05 | Endpoint de TTS escribe en /tmp sin sanitizacion | `apps/api/routers/ai_summary.py:175-179` | El endpoint `/api/ai/generate-voice-description` escribe archivos en `/tmp` usando un nombre basado en timestamp. No hay: limpieza de archivos viejos, validacion de espacio, ni proteccion contra path traversal en el parametro `voice`. | 1. Validar que el parametro `voice` este en una lista whitelist (ya es un Query con default, pero no validado contra enum). 2. Implementar limpieza periodica de `/tmp`. 3. Usar un directorio dedicado con cuota de disco. |
| M-06 | Admin token fallback en frontend store | `apps/web/src/store/appStore.ts:30,490` | La linea `const ADMIN_API_TOKEN = import.meta.env.VITE_ADMIN_API_TOKEN ?? ''` y la linea `token: response.token \|\| ADMIN_API_TOKEN \|\| null` significan que si el login devuelve un token vacio, se usa el token hardcodeado del bundle como fallback. Esto mantiene el token embebido en el JavaScript del cliente incluso si el flujo de login falla. | 1. Eliminar la constante `ADMIN_API_TOKEN` del frontend. 2. Depender exclusivamente del token retornado por el endpoint de login. 3. Si no hay token del servidor, no autenticar. |

---

## Analisis Detallado por Area

### 1. Gestion de Secretos y Variables de Entorno

**Estado: CRITICO**

- `.gitignore` solo excluye `.env`, `.env.local`, y `.env.*.local`. No cubre:
  - `infra/.env.production` (contiene TODAS las credenciales de produccion)
  - `infra/.env.production.backup`
  - `apps/web/.env.production`
- Los archivos de produccion aparecen como **untracked** en git, lo que significa que aun no estan en el historial, pero un solo `git add .` descuidado los comprometeria.
- Credenciales encontradas en archivos no protegidos:
  - Supabase service role key (acceso total a la BD)
  - OpenAI API key (acceso a billing de OpenAI)
  - Admin API token (acceso al panel administrativo)
  - Supabase anon key + URL de produccion

### 2. Configuracion CORS

**Estado: ALTO**

- Origins correctamente restringidos a localhost y FRONTEND_URL (bien).
- `allow_methods=["*"]` y `allow_headers=["*"]` son demasiado permisivos.
- La logica que agrega automaticamente el esquema alternativo (http<->https) es innecesaria y amplifica riesgo.

### 3. Autenticacion y Autorizacion

**Estado: CRITICO**

- **Endpoints sin autenticacion:** `events`, `analytics`, `reports`, `external_cameras`, `ai_summary` son todos publicos. Cualquier persona puede:
  - Insertar eventos falsos
  - Leer todos los eventos de todos los usuarios
  - Eliminar eventos de cualquier usuario
  - Registrar camaras externas
  - Generar costos invocando la API de OpenAI
- **Admin panel:** Tiene autenticacion via bcrypt + token estatico. El flujo de login es correcto (bcrypt verify), pero el token retornado es un secreto estatico del servidor, no un JWT con expiracion.
- **Session init/heartbeat:** Endpoints publicos sin autenticacion. Cualquiera puede crear sesiones y enviar heartbeats.

### 4. Validacion de Input en API

**Estado: MEDIO**

- Pydantic models proveen validacion de tipos basica (bien).
- Query parameters tienen validacion de rangos (`ge=1, le=1000`, etc.) (bien).
- **Faltante:** No hay validacion de longitud maxima en campos de texto (`event_type`, `name`, `email`, `source_url`). Un atacante podria enviar strings de megabytes.
- **Faltante:** No hay sanitizacion del campo `payload` (JSONB). Se acepta cualquier JSON arbitrario.
- **Faltante:** No hay validacion de formato de email en `SessionInitRequest`.
- El endpoint `validate-detections` acepta `image_base64` sin limite de tamano, potencial vector de DoS.

### 5. Seguridad del Frontend

**Estado: MEDIO-BAJO**

- **XSS:** React escapa output por defecto. No se encontro uso de `dangerouslySetInnerHTML`. (BIEN)
- **Admin token en bundle:** `VITE_ADMIN_API_TOKEN` se embebe en el JavaScript compilado, visible para cualquier usuario.
- **Session storage:** La sesion se almacena en `localStorage` sin cifrado. Contiene nombre, email, IP, user agent.
- **No hay CSP:** Sin Content Security Policy configurada.

### 6. Configuracion Docker

**Estado: MEDIO**

- Contenedor corre como root (sin `USER` directive).
- `--reload` flag presente en compose (desarrollo).
- Source code montado como volume en compose (`../apps/api:/app`).
- No hay health checks definidos en compose.
- No hay limites de recursos (memory/cpu) en compose.
- El `.env` del root se comparte con el contenedor via `env_file`.

### 7. Configuracion Supabase

**Estado: MEDIO-ALTO**

- RLS esta habilitado en todas las tablas (BIEN).
- Politicas de RLS permiten operaciones para `user_id = 'anonymous'` y cuando `auth.uid() IS NULL` (lineas 133-138 de setup.sql). Esto es intencionalmente permisivo para la demo pero peligroso en produccion.
- El backend bypassa RLS completamente al usar service_role_key.
- Credenciales de camaras externas en texto plano en la BD.
- No hay tabla de auditoria para acciones administrativas (los eventos de sesion son una aproximacion parcial).

---

## OWASP Top 10 Checklist

| # | Vulnerabilidad | Estado | Notas |
|---|---------------|--------|-------|
| A01 | Broken Access Control | FALLA | Endpoints publicos sin autenticacion. Admin token estatico. |
| A02 | Cryptographic Failures | FALLA | Credenciales en texto plano. Passwords de camaras sin cifrar. |
| A03 | Injection | PASA (parcial) | Supabase client usa queries parametrizadas. Sin SQL directo. |
| A04 | Insecure Design | FALLA | Sin rate limiting. Sin threat modeling documentado. |
| A05 | Security Misconfiguration | FALLA | CORS permisivo. Sin security headers. Docker como root. |
| A06 | Vulnerable Components | REVISAR | Dependencias no auditadas. Ejecutar `npm audit` y `pip-audit`. |
| A07 | Auth Failures | FALLA | Sin brute force protection. Token sin expiracion. |
| A08 | Data Integrity Failures | FALLA | Sin validacion de integridad en payloads. |
| A09 | Logging Failures | FALLA | Sin logging estructurado. Errores van a stdout. Sin audit trail. |
| A10 | SSRF | RIESGO | `external_cameras.py` reenvia URLs a stream gateway sin validar. |

---

## Recomendaciones Generales (Priorizadas)

1. **INMEDIATO:** Rotar todas las credenciales expuestas (Supabase keys, OpenAI key, admin token).
2. **INMEDIATO:** Agregar `**/.env.production*` y `**/.env.production.backup` a `.gitignore`.
3. **INMEDIATO:** Eliminar `VITE_ADMIN_API_TOKEN` del frontend; depender solo del flujo de login.
4. **CORTO PLAZO:** Implementar autenticacion en todos los endpoints (JWT o API key por sesion).
5. **CORTO PLAZO:** Implementar rate limiting con `slowapi` (especialmente en endpoints de OpenAI y login).
6. **CORTO PLAZO:** Reemplazar el admin token estatico por tokens JWT firmados con expiracion.
7. **MEDIO PLAZO:** Agregar security headers (CSP, HSTS, X-Frame-Options, X-Content-Type-Options).
8. **MEDIO PLAZO:** Cifrar credenciales de camaras en la base de datos.
9. **MEDIO PLAZO:** Crear Dockerfile de produccion con usuario no-root y sin reload.
10. **MEDIO PLAZO:** Implementar logging estructurado y audit trail para acciones administrativas.

---

## Pre-Deploy Security Checklist

### Autenticacion
- [ ] Implementar JWT con expiracion para admin (reemplazar token estatico)
- [ ] Rate limiting en login (5 intentos/min con lockout)
- [ ] Logging de intentos de login fallidos

### Autorizacion
- [ ] Proteger endpoints de eventos con autenticacion de sesion
- [ ] Proteger endpoints de camaras externas
- [ ] Proteger endpoints de OpenAI con autenticacion + rate limit
- [ ] Validar permisos de delete/admin en backend

### Datos
- [ ] Validar longitud maxima de strings en modelos Pydantic
- [ ] Validar formato de email en SessionInitRequest
- [ ] Cifrar credenciales de camaras en BD
- [ ] Limitar tamano de payload JSON (max 1MB)
- [ ] Limitar tamano de image_base64 en validate-detections

### Configuracion
- [ ] HTTPS obligatorio en produccion
- [ ] Security headers configurados (CSP, HSTS, X-Frame-Options)
- [ ] CORS restrictivo (metodos y headers especificos)
- [ ] Secrets en gestor de secretos (no en archivos)
- [ ] `.env.production*` en `.gitignore`

### Docker/Infra
- [ ] Dockerfile con usuario no-root
- [ ] docker-compose.prod.yml sin --reload ni volumes de codigo
- [ ] Health checks en compose
- [ ] Limites de recursos (memory, cpu)

### Dependencias
- [ ] Ejecutar `npm audit` en apps/web
- [ ] Ejecutar `pip-audit` en apps/api
- [ ] Actualizar dependencias con vulnerabilidades conocidas
- [ ] Configurar Dependabot o Renovate

### Logging y Monitoreo
- [ ] Logging estructurado (JSON) con niveles
- [ ] Audit trail para acciones administrativas
- [ ] Alertas por intentos de acceso no autorizado
- [ ] Monitoreo de errores (Sentry o similar)

---

## Proximos Pasos

- [ ] Rotar credenciales expuestas (Supabase, OpenAI, admin token) -- **URGENTE**
- [ ] Actualizar `.gitignore` para cubrir archivos de produccion -- **URGENTE**
- [ ] Eliminar `VITE_ADMIN_API_TOKEN` del frontend -- **URGENTE**
- [ ] Implementar autenticacion en endpoints publicos -- **ALTA PRIORIDAD**
- [ ] Agregar rate limiting con slowapi -- **ALTA PRIORIDAD**
- [ ] Reemplazar token estatico admin por JWT -- **ALTA PRIORIDAD**
- [ ] Crear docker-compose.prod.yml seguro -- **MEDIA PRIORIDAD**
- [ ] Agregar security headers -- **MEDIA PRIORIDAD**
- [ ] Audit de dependencias -- **MEDIA PRIORIDAD**
- [ ] Implementar logging estructurado -- **MEDIA PRIORIDAD**

---

*Generado por NXT CyberSec v3.8.0 -- La seguridad no es un producto, es un proceso.*
