# Despliegue del backend con Docker Swarm

Esta guía resume el proceso para desplegar manualmente el backend en un VPS (por ejemplo, Contabo) mediante Docker Swarm y Portainer utilizando el stack `vision-stack`.

## 1. Preparar archivos localmente

1. Copia las carpetas de código:
   - `apps/api`
   - `apps/stream-gateway`
2. Confirma que existan los Dockerfile:
   - `apps/api/Dockerfile`
   - `apps/stream-gateway/Dockerfile` (instala `ffmpeg` y publica el servicio en `:8081`).
3. Genera y completa tu `.env.production` tomando como referencia `infra/.env.production` (incluye Supabase, token admin, URL del frontend, dominios HTTPS, etc.).
4. Revisa `infra/stack.yml` por si necesitas añadir servicios adicionales.

## 2. Subir archivos al VPS

1. Conéctate por SFTP/WinSCP.
2. Crea la estructura objetivo (ajusta la ruta a tu preferencia, por ejemplo `/root/vision-backend`):
   ```
   /root/vision-backend/
     └─ source/
         ├─ apps/
         │   ├─ api/
         │   └─ stream-gateway/
         ├─ stack.yml
         └─ .env.production
   ```
3. Sube las carpetas `apps/api`, `apps/stream-gateway`, además del `stack.yml` y tu `.env.production`.
4. Protege el archivo de variables:
   ```bash
   chmod 600 /root/vision-backend/source/.env.production
   ```

## 3. Construir imágenes en el nodo

```bash
cd /root/vision-backend/source
docker build -t vision-api:latest ./apps/api
docker build -t vision-stream-gateway:latest ./apps/stream-gateway
```

Si manejas varios nodos en el swarm, sube estas imágenes a un registry accesible para todos.

## 4. Exportar variables y desplegar el stack

El stack ahora toma las variables desde el entorno. Antes de desplegar:

```bash
cd /root/vision-backend/source
set -a
source .env.production
set +a
docker stack deploy -c stack.yml vision-stack
```

Monitorea el estado:

```bash
docker stack services vision-stack
docker service logs -f vision-stack_api
docker service logs -f vision-stack_stream-gateway
```

## 5. Variables y secretos

- Repite el bloque `set -a ... set +a` cada vez que vuelvas a desplegar para recargar las variables.
- Si quieres evitar exponer credenciales como variables de entorno, considera usar Docker secrets y adaptar `stack.yml`.

## 6. Integración con Portainer

- En Portainer ve a *Stacks* → *Add stack* → *Web editor*.
- Pega el contenido de `stack.yml`.
- Completa manualmente cada variable en la sección *Environment variables*.
- Lanza el stack y verifica que los servicios queden en `Running`.

## 7. Puertos y dominios

- API FastAPI → `8000`.
- Stream Gateway → `8081`.
- Para producción define:
  - `STREAM_GATEWAY_API_URL=http://stream-gateway:8081` (VIP interno del servicio `stream-gateway` en la red `iagenteknet`).
  - `STREAM_GATEWAY_PUBLIC_BASE_URL=https://apicentinela.iagentek.com.mx` (dominio público servido por Traefik).
- En Portainer coloca el stack sobre la red overlay `iagenteknet` (la mis­ma que usan tus otros stacks). Traefik tomará el control mediante las labels incluidas para publicar:
  - `https://apicentinela.iagentek.com.mx/api/*` → servicio FastAPI (`8000`).
  - `https://apicentinela.iagentek.com.mx/streams/*` → servicio Stream Gateway (`8081`).
- Asegúrate de que Traefik tenga activo el `certresolver` que ya usas para Let’s Encrypt; los routers del stack reutilizan `letsencryptresolver`.

## 8. Verificación rápida

```bash
curl https://apicentinela.iagentek.com.mx/api/health
curl https://apicentinela.iagentek.com.mx/streams/health
```

Si todo responde `ok`, actualiza el frontend (`VITE_API_BASE_URL`, `VITE_STREAM_GATEWAY_URL`) para apuntar a estos endpoints públicos.

