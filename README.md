# Centinela AI — Vision Human Insight

Plataforma de visión por computadora en tiempo real con procesamiento de IA en el navegador (edge AI). Detecta personas, rostros, emociones, objetos y movimiento usando la cámara del navegador o cámaras IP, sin enviar imágenes a servidores.

## Stack Tecnologico

| Capa | Tecnologia |
|---|---|
| Frontend | React 18 + Vite 5 + TypeScript + Tailwind CSS 4 |
| Estado | Zustand |
| ML (browser) | YOLOv8n (ONNX Runtime Web/WebGPU), TinyFaceDetector, FaceExpressionNet (TF.js) |
| Backend | FastAPI + Uvicorn |
| Base de datos | Supabase (PostgreSQL) |
| Stream Gateway | FastAPI + FFmpeg (RTSP/RTMP a HLS) |
| Infraestructura | Docker Compose (dev), Docker Swarm + Traefik (prod) |
| Monitoreo | Prometheus |

## Arquitectura

```
Browser (Edge AI)                          Backend
-----------------                          -------
Camera -> Video Canvas (60fps)
       -> ML Snapshot (480x360)
       -> YOLOv8n (WebGPU/WASM)  ------>  FastAPI (port 9301)
       -> TinyFaceDetector (TF.js)            |
       -> FaceExpressionNet (TF.js)           v
       -> Overlay Canvas (separado)       Supabase (PostgreSQL)
       -> Zustand Store -> UI

IP Cameras -> Stream Gateway (port 9302) -> HLS -> Browser
```

El video y las detecciones se renderizan en **canvas separados** (dual-canvas). El canvas de video se redibuja a 60fps, el canvas de overlays solo se actualiza cuando ML produce resultados. Esto elimina parpadeo de bounding boxes.

## Modelos de IA

| Modelo | Runtime | Funcion | Tamanio |
|---|---|---|---|
| YOLOv8n | ONNX Runtime Web (WebGPU o WASM) | Deteccion de personas y 80+ objetos COCO | ~13MB |
| TinyFaceDetector | TF.js (WebGL) | Deteccion facial | ~190KB |
| FaceExpressionNet | TF.js (WebGL) | Clasificacion de 7 emociones | ~330KB |

YOLOv8n intenta usar **WebGPU** primero (5-19x mas rapido). Si no esta disponible, usa WASM con multi-threading.

## Requisitos

- **Docker Desktop** (recomendado) o Node.js 20+ y Python 3.11+
- **Navegador moderno** (Chrome 113+ para WebGPU)
- **Cuenta de Supabase** con las tablas creadas (`infra/supabase/setup.sql`)

## Inicio Rapido con Docker

```bash
# Clonar
git clone https://github.com/azulls1/centinela-ai.git
cd centinela-ai

# Configurar variables de entorno
cp apps/web/.env.example apps/web/.env
cp apps/api/.env.example apps/api/.env
# Editar con tus credenciales de Supabase

# Levantar todo
cd infra
docker compose up --build -d
```

| Servicio | URL |
|---|---|
| Frontend | http://localhost:9300 |
| API | http://localhost:9301 |
| Stream Gateway | http://localhost:9302 |

## Inicio sin Docker

```bash
# Frontend
cd apps/web
npm install
npm run dev    # http://localhost:9300

# Backend (otra terminal)
cd apps/api
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Stream Gateway (otra terminal, opcional)
cd apps/stream-gateway
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8081 --reload
```

## Variables de Entorno

### Frontend (`apps/web/.env`)

```env
VITE_API_BASE_URL=http://localhost:9301/api
VITE_SUPABASE_URL=https://tu-proyecto.supabase.co
VITE_SUPABASE_ANON_KEY=tu_anon_key
VITE_ADMIN_API_TOKEN=tu_token_admin
```

### Backend (`apps/api/.env`)

```env
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_SERVICE_ROLE_KEY=tu_service_role_key
ADMIN_API_TOKEN=tu_token_admin
STREAM_GATEWAY_URL=http://localhost:9302
OPENAI_API_KEY=tu_key_opcional
```

## Estructura del Proyecto

```
centinela-ai/
├── apps/
│   ├── web/                    # Frontend React + ML en browser
│   │   ├── src/
│   │   │   ├── components/
│   │   │   │   ├── CameraFeed.tsx      # Video + ML processing + dual-canvas
│   │   │   │   ├── CameraManager.tsx   # Multi-camera management
│   │   │   │   ├── DetectionPanel.tsx   # Detection info display
│   │   │   │   └── ...
│   │   │   ├── pages/
│   │   │   │   ├── LivePage.tsx        # Real-time detection
│   │   │   │   ├── DashboardPage.tsx   # Analytics
│   │   │   │   ├── SettingsPage.tsx    # Configuration
│   │   │   │   └── AdminPage.tsx       # Session management
│   │   │   ├── lib/ml/
│   │   │   │   ├── processors.ts       # ML pipeline orchestrator
│   │   │   │   └── models/
│   │   │   │       ├── yolov8.ts       # ONNX Runtime (WebGPU/WASM)
│   │   │   │       ├── mediapipe-face.ts  # TinyFaceDetector
│   │   │   │       └── emotion-model.ts   # FaceExpressionNet
│   │   │   └── store/appStore.ts       # Zustand global state
│   │   └── public/models/              # ML model weights
│   │
│   ├── api/                    # Backend FastAPI
│   │   ├── main.py
│   │   ├── routers/
│   │   │   ├── events.py       # CRUD eventos de deteccion
│   │   │   ├── analytics.py    # Health summaries, trends
│   │   │   ├── sessions.py     # Demo session management
│   │   │   ├── ai_summary.py   # OpenAI summaries
│   │   │   └── external_cameras.py
│   │   └── middleware/         # Rate limiting, CORS, audit, metrics
│   │
│   └── stream-gateway/        # RTSP/RTMP to HLS conversion
│       └── main.py
│
├── infra/
│   ├── docker-compose.yml      # Local development
│   ├── stack.yml               # Production (Docker Swarm)
│   └── supabase/setup.sql      # Database schema
│
└── docs/                       # Architecture docs, runbooks, model cards
```

## API Endpoints

| Metodo | Ruta | Descripcion |
|---|---|---|
| POST | `/api/events` | Crear evento de deteccion |
| GET | `/api/events` | Listar eventos (filtros: type, camera, session) |
| GET | `/api/analytics/health-summary` | Resumen de emociones/actividad |
| GET | `/api/analytics/trends` | Tendencias temporales |
| POST | `/api/sessions/init` | Iniciar sesion demo |
| POST | `/api/sessions/heartbeat` | Keep-alive de sesion |
| GET | `/api/health` | Health check |
| GET | `/metrics` | Prometheus metrics |

## Funcionalidades

- **Deteccion de personas**: YOLOv8n identifica personas con bounding boxes persistentes
- **Deteccion facial**: TinyFaceDetector localiza rostros en el frame
- **Clasificacion de emociones**: 7 emociones (happy, sad, angry, surprised, fearful, disgusted, neutral/focused)
- **Deteccion de objetos**: 80+ clases COCO (laptops, phones, furniture, vehicles, etc.)
- **Deteccion de movimiento**: Diferencia de frames para clasificar actividad (active, standing, sitting, inactive)
- **Multi-camara**: Hasta 3 camaras activas (browser + IP cameras via HLS)
- **Panel admin**: Monitoreo de sesiones, ban/unban, analytics
- **Dashboard**: Graficas de tendencias, resumen de salud, eventos por tipo

## Privacidad

- Todo el procesamiento ML ocurre **en el navegador** (edge AI)
- **No se almacenan imagenes** — solo metadatos de eventos
- Banner de consentimiento obligatorio
- Modo de anonimizacion disponible

## Produccion

El proyecto se despliega en Docker Swarm con Traefik como reverse proxy:

```bash
docker stack deploy -c infra/stack.yml centinela
```

- **Frontend**: https://iris.iagentek.com.mx
- **API**: https://iris-api.iagentek.com.mx

## Licencia

MIT — ver `LICENSE`

---

Desarrollado por **IAGENTEK**
