# Centinela IAGENTEK – Contexto del Proyecto

## Descripción general
Plataforma web que permite lanzar sesiones de demostración, conectar cámaras (navegador o externas), analizar video con modelos de ML y presentar métricas en tiempo real. Incluye un panel administrativo protegido para monitorear y gestionar sesiones.

## Componentes
- **Frontend (`apps/web`)**  
  Vite + React. Se publica en `https://centinela.iagentek.com.mx`. Variables configuradas vía `.env.production`. Rutas principales:
  - `/` landing
  - `/live` captura y procesamiento de cámaras
  - `/dashboard` métricas y eventos
  - `/admin` panel administrativo (requiere login contra backend)

- **Backend (`apps/api`)**  
  FastAPI + Uvicorn, expuesto como `https://apicentinela.iagentek.com.mx/api`. Funciones clave:
  - Sesiones (`/api/sessions/*`): init, heartbeat, alertas, bloqueos.
  - Cámaras externas (`/api/external-cameras/*`).
  - Métricas y reportes.
  - **Login admin** `POST /api/sessions/admin/auth/login`: verifica usuario en Supabase, compara hash `bcrypt` y entrega `{ token: ADMIN_API_TOKEN, username }`. El token se usa en header `x-admin-token` para los endpoints administrativos.

- **Stream Gateway (`apps/stream-gateway`)**  
  Servicio Python que gestiona streams HLS para cámaras externas.

- **Infraestructura (`infra/`)**  
  - `stack.yml`: definición Docker Swarm con Traefik.
  - `.env.production`: variables de despliegue.
  - Guías: `DEPLOY_BACKEND.md` y `DEPLOY_BACKEND_STEP_BY_STEP.md`.

- **Supabase**  
  - Tablas principales  
    - `vishum_sessions`: registros de cada demo (campos clave: `session_id`, `status`, `cameras_active`, `tokens_used`, `metadata`).  
    - `vishum_session_events`: historial de eventos por sesión.  
    - `vishum_admin_users`: credenciales administrativas (`username`, `password_hash`).  
  - Políticas y seguridad  
    - `vishum_sessions` y `vishum_session_events` se consumen con la `service_role` key, por lo que no dependen de políticas adicionales para el backend.  
    - `vishum_admin_users` tiene política “service role only”, permitiendo acceso únicamente cuando el claim `role` es `service_role`.  
  - Claves (`SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE_KEY`) se gestionan en `.env` del frontend y backend.
  - Ya no se usa la RPC anterior; el backend consulta la tabla y valida el hash con `bcrypt`.

## Flujo de login administrativo
1. Frontend envía `username` y `password` a `/api/sessions/admin/auth/login`.
2. FastAPI obtiene `password_hash` de `vishum_admin_users`, valida con `bcrypt`.
3. Si es correcto, retorna `token = ADMIN_API_TOKEN`.
4. Frontend guarda el token y lo envía en `x-admin-token`.
5. Las rutas admin (`/api/sessions/admin/...`) confirman el token antes de responder.

## Notas de despliegue
1. Subir cambios al VPS (WinSCP).
2. Ejecutar:
   ```
   cd /root/vision-backend/source
   docker build --no-cache -t vision-api:latest ./apps/api
   docker service update --force vision-stack_api
   docker service logs -f --tail 50 vision-stack_api
   ```
3. Verificar con:
   ```
   curl -k -X POST https://apicentinela.iagentek.com.mx/api/sessions/admin/auth/login \
     -H "Content-Type: application/json" \
     -d '{"username":"iagentek_admin","password":"iagentek_123"}'
   ```
4. `npm run build` en `apps/web` y subir `dist/` a Hostinger (`public_html`). Limpiar caché y hacer hard reload.

## Buenas prácticas y recordatorios
- Mantener `ADMIN_API_TOKEN` y claves Supabase fuera del repositorio público (`.env`).
- Si se añaden funciones RPC nuevas y se usa PostgREST, ejecutar `select pg_notify('pgrst','reload schema');` o reiniciar el servicio `postgrest` en Portainer.
- Hash de nuevos usuarios admin: `update public.vishum_admin_users set password_hash = crypt('NUEVA', gen_salt('bf')) where username = '...';`.
- Logs backend: `docker service logs vision-stack_api`.
- Frontend: hard reload (`Ctrl+Shift+R`) tras desplegar para evitar caché.

## Estado actual
- Login administradores funcionando (hash `bcrypt` en Supabase).
- API y frontend desplegados con las últimas versiones.
- Documentación de despliegue actualizada y accesible en `infra/`.

