# 03 - Seguridad

Fecha de evaluacion: 2026-04-05

---

## Resumen Ejecutivo

| Area                       | Puntaje | Nivel       |
|----------------------------|---------|-------------|
| Control de Acceso          | 3/10    | Critico     |
| Gestion de Credenciales    | 2/10    | Critico     |
| Superficie de Ataque       | 4/10    | Deficiente  |
| Auditoria & Logs           | 3/10    | Critico     |
| Dependencias Vulnerables   | 6/10    | Aceptable   |
| **Promedio General**       | **3.6/10** | **Critico** |

---

## 1. Control de Acceso  --  3/10

### Evidencia

| Archivo | Hallazgo | Severidad |
|---------|----------|-----------|
| `apps/api/supabase_client.py:14,23` | Usa `SUPABASE_SERVICE_ROLE_KEY` exclusivamente; **todo** el backend opera con permisos completos que anulan RLS | CRITICA |
| `apps/api/routers/events.py` | Endpoints `POST /`, `GET /`, `GET /{id}`, `DELETE /{id}`, `GET /stats/summary` -- **ninguno** requiere autenticacion | CRITICA |
| `apps/api/routers/analytics.py` | Endpoints `GET /health-summary`, `GET /trends` -- **sin autenticacion** | CRITICA |
| `apps/api/routers/reports.py` | Endpoints `POST /generate`, `GET /available` -- **sin autenticacion** | ALTA |
| `apps/api/routers/ai_summary.py` | Endpoints `POST /generate-summary`, `POST /generate-voice-description`, `POST /validate-detections` -- **sin autenticacion**; consumo de API OpenAI abierto al publico | CRITICA |
| `apps/api/routers/external_cameras.py` | CRUD completo de camaras externas -- **sin autenticacion** | CRITICA |
| `apps/api/routers/sessions.py:80-89` | Endpoints admin (`/admin`, `/admin/{id}/disconnect`, `/admin/{id}/ban`, etc.) protegidos con `require_admin_token` via header `x-admin-token` | POSITIVO |
| `apps/api/routers/sessions.py:42-78` | Login admin con bcrypt contra `vishum_admin_users` -- buena practica | POSITIVO |
| `infra/supabase/setup.sql:117-196` | RLS habilitado en todas las tablas, pero `auth.uid() IS NULL` permite inserciones anonimas sin restriccion | ALTA |
| `apps/web/src/store/appStore.ts:30` | `VITE_ADMIN_API_TOKEN` importado en el frontend -- token de admin visible en bundle JS | CRITICA |

### Hallazgos

1. **~80% de los endpoints API no tienen autenticacion.** Cualquiera puede crear eventos, consultar analytics, generar reportes, invocar OpenAI (generando costos) y manipular camaras externas sin credencial alguna.
2. El backend usa `service_role_key` para todas las operaciones, lo que anula completamente las politicas RLS de Supabase. Las RLS definidas en `setup.sql` solo protegen llamadas directas desde el frontend con `anon_key`, no las del backend.
3. El token admin se embebe como `VITE_ADMIN_API_TOKEN` en el bundle de JavaScript del frontend. Cualquier usuario puede extraerlo del bundle compilado y acceder al panel administrativo.
4. No existe rate limiting en ningun endpoint, exponiendo la API OpenAI a abuso de costos.

### Recomendaciones

1. **URGENTE:** Implementar middleware de autenticacion global (JWT o Supabase Auth) para todos los routers.
2. Crear un cliente Supabase con `anon_key` para operaciones de lectura de usuarios y reservar `service_role_key` solo para operaciones administrativas privilegiadas.
3. **URGENTE:** Eliminar `VITE_ADMIN_API_TOKEN` del frontend; el flujo de login ya retorna el token via API.
4. Agregar rate limiting (ej. `slowapi`) a endpoints criticos como `/api/ai/*` y `/api/events/`.

---

## 2. Gestion de Credenciales  --  2/10

### Evidencia

| Archivo | Hallazgo | Severidad |
|---------|----------|-----------|
| `.gitignore:19-25` | Excluye `.env`, `.env.local`, `.env.production`, `infra/.env.production*`, `apps/web/.env.production` | POSITIVO |
| `apps/web/.env.production:4` | Contiene `VITE_ADMIN_API_TOKEN=mi-token-super-secreto-admin-2024-xyz123` -- token trivial y predecible | CRITICA |
| `apps/web/.env.production:3` | Contiene `VITE_SUPABASE_ANON_KEY` con JWT embebido | ALTA |
| `apps/web/.env.production:1-2` | Expone URL de API de produccion y URL de Supabase | MEDIA |
| `apps/api/supabase_client.py:14` | `SUPABASE_SERVICE_ROLE_KEY` cargada via `.env` (correcto), pero no hay validacion de complejidad | MEDIA |
| `apps/api/routers/sessions.py:30` | `ADMIN_API_TOKEN` con fallback a string vacio `""` -- si la variable no existe, la comparacion falla pero de forma silenciosa | ALTA |
| `apps/api/routers/external_cameras.py:67-69` | Credenciales RTSP (`auth_username`, `auth_password`) se almacenan en texto plano en Supabase | ALTA |
| Git status | `apps/web/.env.production` aparece como archivo no rastreado (`??`), pero esta presente en el directorio y podria ser incluido accidentalmente | ALTA |

### Hallazgos

1. **Token admin trivial**: `mi-token-super-secreto-admin-2024-xyz123` es facilmente adivinable y esta en un archivo `.env.production` en el directorio del proyecto.
2. **Sin rotacion de secretos**: No existe mecanismo alguno de rotacion, expiracion o revocacion de tokens.
3. **Credenciales RTSP en texto plano**: Las contrasenas de camaras externas se almacenan sin cifrar en la tabla `vishum_external_cameras`.
4. **JWT de Supabase en .env.production**: Aunque `anon_key` es "publico" por diseno de Supabase, combinado con el token admin trivial, un atacante tiene acceso completo.
5. El `.gitignore` excluye `.env.production` correctamente, pero el archivo existe en el directorio de trabajo y aparece como untracked -- riesgo de commit accidental.

### Recomendaciones

1. **URGENTE:** Reemplazar `mi-token-super-secreto-admin-2024-xyz123` por un token criptograficamente seguro (min 256 bits).
2. Cifrar credenciales RTSP en base de datos (AES-256 o equivalente).
3. Implementar expiracion y rotacion de tokens admin (JWT con TTL corto).
4. Agregar un pre-commit hook que impida commit de archivos `.env*`.
5. Mover secretos de produccion a un gestor de secretos (Vault, AWS Secrets Manager, etc.).

---

## 3. Superficie de Ataque  --  4/10

### Evidencia

| Archivo | Hallazgo | Severidad |
|---------|----------|-----------|
| `infra/docker-compose.yml:6,30` | 2 puertos expuestos: `8000` (API), `8081` (stream-gateway) | MEDIA |
| `apps/api/main.py:34-38` | CORS permite `localhost:5173`, `localhost:3000` y `FRONTEND_URL` configurable | POSITIVO |
| `apps/api/main.py:41-44` | CORS agrega automaticamente variante http/https del `FRONTEND_URL` | MEDIA |
| `apps/api/main.py:49-51` | `allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"]` -- todos los metodos HTTP habilitados | MEDIA |
| `apps/api/main.py:52` | `allow_headers` no incluye `x-admin-token`, lo que podria causar errores CORS en produccion o forzar preflight sin validacion correcta | ALTA |
| `apps/api/main.py:59-68` | `SecurityHeadersMiddleware` agrega `X-Content-Type-Options`, `X-Frame-Options`, `X-XSS-Protection`, `Referrer-Policy` | POSITIVO |
| Routers (todos) | Total de ~20 endpoints publicos sin autenticacion | CRITICA |
| `apps/api/routers/external_cameras.py:24-33` | Llamadas a stream-gateway sin autenticacion servidor-a-servidor | ALTA |
| `apps/api/routers/ai_summary.py:179-182` | Archivos de audio escritos en `/tmp` sin limpieza -- potencial ataque de disco lleno | MEDIA |

### Conteo de Endpoints

| Router | Endpoints | Protegidos | Sin Proteger |
|--------|-----------|------------|--------------|
| events | 5 | 0 | 5 |
| analytics | 2 | 0 | 2 |
| reports | 2 | 0 | 2 |
| ai_summary | 3 | 0 | 3 |
| external_cameras | 5 | 0 | 5 |
| sessions | 8 | 5 (admin) | 3 (init, heartbeat, login) |
| root/health/info | 3 | 0 | 3 (aceptable) |
| **Total** | **28** | **5 (18%)** | **23 (82%)** |

### Hallazgos

1. **82% de los endpoints estan abiertos** al publico, incluyendo operaciones de escritura y eliminacion.
2. La configuracion CORS es razonablemente restrictiva (no usa `*`), pero falta `x-admin-token` en `allow_headers`, lo que podria causar problemas en navegadores.
3. Existe `SecurityHeadersMiddleware` con cabeceras de seguridad basicas -- buen inicio.
4. No hay Content Security Policy (CSP) header.
5. La comunicacion API-a-gateway no tiene autenticacion; un atacante con acceso a la red interna podria manipular streams.
6. No hay WAF, proteccion DDoS ni rate limiting.

### Recomendaciones

1. Implementar autenticacion en todos los endpoints de datos (ver seccion 1).
2. Agregar `x-admin-token` a `allow_headers` en la configuracion CORS.
3. Agregar Content-Security-Policy header.
4. Implementar autenticacion entre servicios internos (API <-> stream-gateway) con token compartido.
5. Agregar rate limiting global y por endpoint.
6. Limpiar archivos temporales en `/tmp` con un mecanismo programado.

---

## 4. Auditoria & Logs  --  3/10

### Evidencia

| Archivo | Hallazgo | Severidad |
|---------|----------|-----------|
| `apps/api/main.py:12,15` | `logging.getLogger(__name__)` configurado a nivel de modulo | POSITIVO |
| `apps/api/routers/events.py:8,13` | Logger configurado, usa `logger.exception()` en bloques catch | POSITIVO |
| `apps/api/routers/analytics.py:8,13` | Logger con `logger.exception()` en errores | POSITIVO |
| `apps/api/routers/reports.py:8,13` | Logger con `logger.exception()` en errores | POSITIVO |
| `apps/api/routers/ai_summary.py:10,13` | Logger con `logger.exception()` en errores | POSITIVO |
| `apps/api/routers/sessions.py` | **Sin import de logging** -- usa `print()` para errores (lineas 620-621) y `traceback.print_exc()` | ALTA |
| `apps/api/routers/external_cameras.py` | **Sin logging** -- errores se propagan como HTTPException sin registro | ALTA |
| Todos los routers | No hay logging de acceso exitoso (solo errores) | ALTA |
| `apps/api/main.py` | **No hay middleware de logging de requests/responses** (IP, path, status code, duracion) | CRITICA |
| `apps/api/routers/sessions.py:130-145` | `_insert_session_event()` registra acciones en `vishum_session_events` -- audit trail para sesiones | POSITIVO |
| `apps/api/routers/sessions.py:409,436,446` | Acciones admin (disconnect, ban, limit) generan eventos de auditoria via `_insert_session_event()` | POSITIVO |

### Hallazgos

1. **Logging solo de errores**: Se registran excepciones en 4 de 6 routers, pero no se registran accesos exitosos, lo que impide detectar patrones de abuso.
2. **Sin access log middleware**: No hay registro centralizado de quien accede a que endpoint, con que IP, ni cuanto tarda la respuesta.
3. **Audit trail parcial**: Solo las acciones administrativas sobre sesiones generan un trail en `vishum_session_events`. Operaciones como eliminar eventos, generar reportes o invocar OpenAI no dejan rastro.
4. **Sessions router usa `print()` y `traceback.print_exc()`** en lugar del sistema de logging estandar.
5. No hay integracion con sistema de monitoreo externo (Sentry, Datadog, etc.).
6. No hay alertas automaticas por errores repetidos o patrones sospechosos.

### Recomendaciones

1. **URGENTE:** Agregar middleware de access logging que registre IP, metodo, path, status code, duracion y user-agent para cada request.
2. Reemplazar `print()`/`traceback.print_exc()` en `sessions.py` por `logger.exception()`.
3. Agregar logging a `external_cameras.py`.
4. Implementar audit trail para operaciones destructivas (DELETE de eventos, DELETE de camaras).
5. Configurar logging centralizado con formato JSON estructurado para facilitar analisis.
6. Integrar con un servicio de monitoreo (Sentry, Datadog o CloudWatch).

---

## 5. Dependencias Vulnerables  --  6/10

### Evidencia

| Archivo | Paquete | Version | Observacion |
|---------|---------|---------|-------------|
| `apps/api/requirements.txt` | `fastapi` | >=0.111.0 | Version reciente, sin CVEs conocidos criticos |
| `apps/api/requirements.txt` | `uvicorn[standard]` | >=0.30.1 | Version reciente |
| `apps/api/requirements.txt` | `supabase` | >=2.24.0 | Version reciente |
| `apps/api/requirements.txt` | `openai` | >=1.35.0 | Version reciente |
| `apps/api/requirements.txt` | `pydantic` | >=2.11.7 | Version reciente |
| `apps/api/requirements.txt` | `bcrypt` | >=4.1.2 | Version reciente |
| `apps/api/requirements.txt` | `Pillow` | >=10.3.0 | Pillow tiene historial frecuente de CVEs; necesita monitoreo constante |
| `apps/api/requirements.txt` | `opencv-python-headless` | >=4.9.0.80 | Generalmente estable |
| `apps/web/package.json` | `react` | ^18.3.1 | Version reciente |
| `apps/web/package.json` | `@tensorflow/tfjs` | ^4.15.0 | Paquete grande con dependencias transitivas; riesgo medio |
| `apps/web/package.json` | `vite` | ^5.2.0 | Version estable |
| `apps/web/package.json` | `eslint` | ^8.57.0 | ESLint 8.x esta en end-of-life; migrar a 9.x |
| `apps/api/requirements.txt` | Todas | `>=` (sin tope superior) | Sin pin de version maxima; actualizaciones automaticas podrian romper compatibilidad | MEDIA |
| `apps/web/package.json` | Todas | `^` (caret range) | Permite minor/patch updates; razonable pero sin lockfile verificado |

### Hallazgos

1. **Versiones generalmente recientes**: Las dependencias principales estan en versiones modernas sin CVEs criticos conocidos al momento de la evaluacion.
2. **Sin scan automatizado de CVEs**: No hay `npm audit`, `pip-audit`, Snyk, Dependabot ni similar configurado en CI/CD.
3. **Pillow es un riesgo recurrente**: Historicamente tiene CVEs frecuentes; la version >=10.3.0 es razonable pero necesita monitoreo.
4. **Requirements sin tope superior (`>=`)**: Podria instalar versiones futuras con breaking changes o vulnerabilidades.
5. **ESLint 8.x en EOL**: No es un riesgo de seguridad directo pero indica que las dependencias no se actualizan proactivamente.
6. **No se ejecuto `npm audit` ni `pip-audit`** en esta evaluacion; los puntajes podrian bajar con un analisis de CVEs real.

### Recomendaciones

1. Ejecutar `npm audit` y `pip-audit` regularmente; integrar en CI/CD.
2. Pinear versiones con rangos acotados en `requirements.txt` (ej. `fastapi>=0.111.0,<1.0`).
3. Configurar Dependabot o Renovate para actualizaciones automaticas con PRs.
4. Migrar ESLint a version 9.x.
5. Monitorear especificamente Pillow y TensorFlow.js por su historial de vulnerabilidades.

---

## Resumen de Acciones Prioritarias

| Prioridad | Accion | Area |
|-----------|--------|------|
| P0 - Inmediata | Agregar autenticacion a todos los endpoints de la API | Control de Acceso |
| P0 - Inmediata | Eliminar `VITE_ADMIN_API_TOKEN` del frontend | Credenciales |
| P0 - Inmediata | Reemplazar token admin trivial por token criptografico | Credenciales |
| P1 - Urgente | Agregar middleware de access logging | Auditoria |
| P1 - Urgente | Implementar rate limiting en endpoints criticos | Superficie de Ataque |
| P1 - Urgente | Cifrar credenciales RTSP en base de datos | Credenciales |
| P2 - Importante | Agregar pre-commit hook para bloquear archivos `.env` | Credenciales |
| P2 - Importante | Configurar `npm audit` / `pip-audit` en CI/CD | Dependencias |
| P2 - Importante | Agregar CSP header y autenticacion inter-servicios | Superficie de Ataque |
| P3 - Mejora | Implementar audit trail completo para operaciones destructivas | Auditoria |
| P3 - Mejora | Integrar monitoreo externo (Sentry) | Auditoria |
