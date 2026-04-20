# Guía paso a paso para desplegar el backend en producción

Esta guía resume exactamente los pasos que debemos seguir cada vez que preparemos el backend en el VPS, usando Portainer y la misma arquitectura que ya tienes en tus otros stacks (Traefik + red `iagenteknet`).

> **Importante:** No cambies el orden. Después de cada paso puedes anotar evidencias (capturas, logs) para validar que todo quedó bien.

---

## Paso 0. Prerrequisitos

1. Traefik corriendo en el VPS, usando la red overlay `iagenteknet` y el certresolver `letsencryptresolver`.
2. Acceso SSH (PuTTY) y SFTP (WinSCP) al VPS como `root`.
3. Repositorio actualizado en tu PC con los archivos:
   - `apps/api`
   - `apps/stream-gateway`
   - `infra/stack.yml`
   - `infra/.env.production` (variables reales)
4. Subdominio `apicentinela.iagentek.com.mx` apuntando a la IP del VPS.

---

## Paso 1. Crear carpeta del proyecto en el VPS

1. Conéctate por PuTTY.
2. Ejecuta:
   ```bash
   mkdir -p /root/vision-backend/source
   ls -lah /root/vision-backend
   ```
3. Si ya existía y está limpia, continúa. Si hay archivos viejos, decide si se borran o se respaldan antes de seguir.

---

## Paso 2. Subir el código con WinSCP

1. Abre WinSCP → conéctate vía SFTP.
2. Ve a `/root/vision-backend/source`.
3. Copia estos elementos desde tu PC:
   - Carpeta `apps/api`
   - Carpeta `apps/stream-gateway`
   - Archivo `infra/stack.yml`
   - Archivo `infra/.env.production`
4. De regreso en PuTTY:
   ```bash
   cd /root/vision-backend/source
   chmod 600 .env.production
   ls -lah .env.production
   ```
5. Guarda la salida para verificar que el archivo está protegido.

---

## Paso 3. Construir imágenes Docker en el VPS

1. En PuTTY (ubicado en `/root/vision-backend/source`):
   ```bash
   docker build -t vision-api:latest ./apps/api
   docker build -t vision-stream-gateway:latest ./apps/stream-gateway
   ```
2. Lleva registro de las últimas líneas de cada build (deben terminar con `Successfully tagged ...`).
3. Si aparece un error, detente y repórtalo antes de continuar.

---

## Paso 4. Exportar variables (sesión actual)

1. Aún en PuTTY:
   ```bash
   set -a
   source .env.production
   set +a
   ```
2. Esto solo aplica al entorno de la sesión actual; sirve si luego reintentas el deploy desde CLI.

---

## Paso 5. Crear el stack en Portainer

1. Entra a Portainer → tu endpoint Docker → `Stacks`.
2. Clic en **Add stack**.
3. Nombre sugerido: `vision-stack`.
4. Copia y pega el contenido de `infra/stack.yml` en el editor Web (el archivo ya está listo para Traefik y la red `iagenteknet`). Referencia:
   ```yaml
   version: '3.8'

   services:
     api:
       image: vision-api:latest
       environment:
         FRONTEND_URL: ${FRONTEND_URL}
         SUPABASE_URL: ${SUPABASE_URL}
         SUPABASE_SERVICE_ROLE_KEY: ${SUPABASE_SERVICE_ROLE_KEY}
         ADMIN_API_TOKEN: ${ADMIN_API_TOKEN}
         SESSION_LIMIT_MINUTES: ${SESSION_LIMIT_MINUTES:-45}
         SESSION_TOKEN_LIMIT: ${SESSION_TOKEN_LIMIT:-15000}
         SESSION_CAMERA_LIMIT: ${SESSION_CAMERA_LIMIT:-3}
         SESSION_INACTIVITY_ALERT_MINUTES: ${SESSION_INACTIVITY_ALERT_MINUTES:-5}
         ADMIN_BANNED_LIMIT_DEFAULT: ${ADMIN_BANNED_LIMIT_DEFAULT:-5}
         STREAM_GATEWAY_API_URL: ${STREAM_GATEWAY_API_URL:-http://stream-gateway:8081}
         STREAM_GATEWAY_FFMPEG_PATH: ${STREAM_GATEWAY_FFMPEG_PATH:-ffmpeg}
         OPENAI_API_KEY: ${OPENAI_API_KEY:-}
       deploy:
         replicas: 1
         restart_policy:
           condition: on-failure
         resources:
           limits:
             cpus: '1.0'
             memory: 1G
           reservations:
             cpus: '0.25'
             memory: 256M
         labels:
           - traefik.enable=true
           - traefik.http.routers.vision_api.rule=Host(`apicentinela.iagentek.com.mx`) && PathPrefix(`/api`)
           - traefik.http.routers.vision_api.entrypoints=websecure
           - traefik.http.routers.vision_api.tls=true
           - traefik.http.routers.vision_api.tls.certresolver=letsencryptresolver
           - traefik.http.services.vision_api.loadbalancer.server.port=8000
       networks:
         vision-net:
           aliases:
             - vision-api

     stream-gateway:
       image: vision-stream-gateway:latest
       environment:
         STREAM_GATEWAY_STREAMS_DIR: /data/streams
         STREAM_GATEWAY_PUBLIC_BASE_URL: ${STREAM_GATEWAY_PUBLIC_BASE_URL:-http://localhost:8081}
         STREAM_GATEWAY_FFMPEG_PATH: ${STREAM_GATEWAY_FFMPEG_PATH:-ffmpeg}
         STREAM_GATEWAY_API_URL: ${STREAM_GATEWAY_API_URL:-http://stream-gateway:8081}
       deploy:
         replicas: 1
         restart_policy:
           condition: on-failure
         resources:
           limits:
             cpus: '1.0'
             memory: 1G
           reservations:
             cpus: '0.25'
             memory: 256M
         labels:
           - traefik.enable=true
           - traefik.http.routers.vision_stream.rule=Host(`apicentinela.iagentek.com.mx`) && PathPrefix(`/streams`)
           - traefik.http.routers.vision_stream.entrypoints=websecure
           - traefik.http.routers.vision_stream.tls=true
           - traefik.http.routers.vision_stream.tls.certresolver=letsencryptresolver
           - traefik.http.services.vision_stream.loadbalancer.server.port=8081
       volumes:
         - stream-data:/data/streams
       networks:
         vision-net:
           aliases:
             - stream-gateway

   networks:
     vision-net:
       external: true
       name: iagenteknet

   volumes:
     stream-data:
       driver: local
   ```
5. En la sección **Environment variables**, pega el contenido completo de tu `infra/.env.production`.
6. Haz clic en **Deploy the stack**.
7. Espera al mensaje de confirmación. Si hay error (por variables o imagen no encontrada), anótalo y corrígelo antes de reintentar.

---

## Paso 6. Supervisión en Portainer

1. En la lista de stacks, verifica que `vision-stack` aparezca.
2. Abre el stack y revisa que los servicios `vision-stack_api` y `vision-stack_stream-gateway` estén en estado **Running**.
3. Si alguno falla, entra a la pestaña *Logs* para ver detalles y corrige en consecuencia.

---

## Paso 7. Verificaciones por terminal (opcional recomendado)

En PuTTY:
```bash
docker stack services vision-stack
docker service logs --tail 50 vision-stack_api
docker service logs --tail 50 vision-stack_stream-gateway
```

Guarda los logs para validaciones futuras.

---

## Paso 8. Pruebas externas

1. Verifica el endpoint de salud:
   ```bash
   curl https://apicentinela.iagentek.com.mx/api/health
   ```
2. Desde el navegador, ingresa a `https://centinela.iagentek.com.mx` y abre la consola para confirmar que ya no haya errores de CORS o contenido mixto.
3. Comprueba que las funciones de cámaras externas generen URLs HLS del tipo `https://apicentinela.iagentek.com.mx/streams/...`.

---

## Paso 9. Después del despliegue

1. Si cambiaste variables críticas, regenera el build del frontend (`npm run build`) y súbelo a Hostinger.
2. Respalda el `.env.production` usado para este despliegue (mantén un duplicado seguro).
3. Considera rotar las credenciales expuestas en los YAML antiguos (Supabase, N8N) si estuvieron compartidas públicamente.

---

## Resumen de comandos

```bash
# Crear carpeta
mkdir -p /root/vision-backend/source

# Permisos del .env
cd /root/vision-backend/source
chmod 600 .env.production

# Construir imágenes
docker build -t vision-api:latest ./apps/api
docker build -t vision-stream-gateway:latest ./apps/stream-gateway

# Exportar variables (sesión actual)
set -a
source .env.production
set +a

# Verificar servicios
docker stack services vision-stack
docker service logs --tail 50 vision-stack_api
docker service logs --tail 50 vision-stack_stream-gateway

# Prueba de salud
curl https://apicentinela.iagentek.com.mx/api/health
```

Con esta guía puedes ir registrando cada avance y comprobar que el despliegue queda concluido al 100 %. Cuando necesites repetir el proceso, solo vuelve aquí y síguelos en orden.

