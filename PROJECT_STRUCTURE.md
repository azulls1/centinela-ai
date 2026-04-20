# 📁 Estructura del Proyecto

Este documento describe la estructura completa del proyecto **Vision Human Insight**.

## 📂 Estructura de Directorios

```
vision-aiagentek/
├── apps/                          # Aplicaciones principales
│   ├── web/                       # Frontend React + Vite
│   │   ├── src/
│   │   │   ├── components/        # Componentes React
│   │   │   │   ├── PrivacyBanner.tsx
│   │   │   │   ├── Navbar.tsx
│   │   │   │   ├── CameraView.tsx
│   │   │   │   ├── DetectionPanel.tsx
│   │   │   │   ├── Toggle.tsx
│   │   │   │   └── Slider.tsx
│   │   │   ├── pages/             # Páginas principales
│   │   │   │   ├── LivePage.tsx
│   │   │   │   ├── DashboardPage.tsx
│   │   │   │   └── SettingsPage.tsx
│   │   │   ├── lib/               # Utilidades y librerías
│   │   │   │   ├── supabase.ts    # Cliente de Supabase
│   │   │   │   └── ml/            # Modelos de ML
│   │   │   │       └── processors.ts
│   │   │   ├── store/             # Estado global (Zustand)
│   │   │   │   └── appStore.ts
│   │   │   ├── types.ts           # Tipos TypeScript
│   │   │   ├── App.tsx            # Componente principal
│   │   │   └── main.tsx           # Punto de entrada
│   │   ├── public/                # Archivos estáticos
│   │   ├── index.html
│   │   ├── package.json
│   │   ├── vite.config.ts
│   │   ├── tsconfig.json
│   │   ├── tailwind.config.js
│   │   └── .env.example
│   │
│   └── api/                       # Backend FastAPI
│       ├── routers/               # Routers de endpoints
│       │   ├── __init__.py
│       │   ├── events.py          # Endpoints de eventos
│       │   ├── analytics.py       # Endpoints de análisis
│       │   └── reports.py         # Endpoints de reportes
│       ├── main.py                # Aplicación FastAPI principal
│       ├── models.py              # Modelos Pydantic
│       ├── supabase_client.py     # Cliente de Supabase
│       ├── requirements.txt       # Dependencias Python
│       ├── Dockerfile             # Docker para backend
│       └── .env.example
│
├── packages/                      # Paquetes compartidos
│   └── shared/                    # Tipos y esquemas compartidos
│       ├── package.json
│       └── README.md
│
├── infra/                         # Infraestructura
│   ├── supabase/                  # Esquemas de base de datos
│   │   └── schema.sql
│   └── docker-compose.yml        # Docker Compose (opcional)
│
├── .gitignore
├── package.json                   # Workspace root
├── README.md                      # Documentación principal
├── INSTALLATION.md               # Guía de instalación
├── DEPLOYMENT.md                 # Guía de despliegue
├── PROJECT_STRUCTURE.md          # Este archivo
└── LICENSE                       # Licencia MIT
```

## 📝 Descripción de Módulos Principales

### Frontend (`apps/web/`)

#### Componentes (`src/components/`)
- **PrivacyBanner.tsx**: Banner de privacidad que se muestra al inicio
- **Navbar.tsx**: Barra de navegación principal
- **CameraView.tsx**: Componente de captura y visualización de video
- **DetectionPanel.tsx**: Panel lateral con detecciones actuales
- **Toggle.tsx**: Componente de toggle reutilizable
- **Slider.tsx**: Componente de slider reutilizable

#### Páginas (`src/pages/`)
- **LivePage.tsx**: Página principal de análisis en tiempo real
- **DashboardPage.tsx**: Dashboard con estadísticas y gráficas
- **SettingsPage.tsx**: Página de configuración

#### Librerías (`src/lib/`)
- **supabase.ts**: Cliente y funciones de Supabase
- **ml/processors.ts**: Procesadores de modelos de ML

#### Store (`src/store/`)
- **appStore.ts**: Store global de Zustand con estado de la aplicación

### Backend (`apps/api/`)

#### Routers (`routers/`)
- **events.py**: Endpoints CRUD para eventos
- **analytics.py**: Endpoints de análisis y estadísticas
- **reports.py**: Endpoints para generación de reportes

#### Archivos Principales
- **main.py**: Aplicación FastAPI principal
- **models.py**: Modelos Pydantic para validación
- **supabase_client.py**: Cliente de Supabase para backend

### Infraestructura (`infra/`)

- **supabase/schema.sql**: Esquema SQL para crear tablas en Supabase
- **docker-compose.yml**: Configuración Docker Compose (opcional)

## 🔄 Flujo de Datos

1. **Captura**: `CameraView` captura video de la cámara
2. **Procesamiento**: `processors.ts` procesa frames con modelos ML
3. **Estado**: Detecciones se actualizan en `appStore`
4. **Almacenamiento**: Eventos significativos se guardan en Supabase
5. **Visualización**: Dashboard muestra estadísticas y gráficas

## 📦 Dependencias Principales

### Frontend
- React 18.3
- Vite 5.2
- TypeScript 5.4
- Tailwind CSS 3.4
- Zustand 4.5 (estado)
- Supabase JS 2.39
- ONNX Runtime Web 1.19
- MediaPipe Tasks Vision 0.10
- TensorFlow.js 4.15
- Recharts 2.12 (gráficas)

### Backend
- FastAPI 0.111
- Uvicorn 0.30
- Supabase Python 2.3
- Pydantic 2.7
- OpenAI 1.35 (opcional)
- OpenCV Python 4.9 (opcional)

## 🎯 Próximas Mejoras

- [ ] Implementar modelos ML reales (YOLO, MediaPipe)
- [ ] Generación de reportes PDF
- [ ] Text-to-Speech para resúmenes
- [ ] WebSocket para actualizaciones en tiempo real
- [ ] Soporte para múltiples cámaras IP
- [ ] Tests unitarios y de integración

---

**Última actualización**: 2024

