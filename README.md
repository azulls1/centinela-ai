# 🎯 IAGENTEK Vision Human Insight

Plataforma de inteligencia artificial con visión por computadora capaz de detectar personas, rostros, emociones, objetos, movimiento, estado de salud aparente y acciones humanas en tiempo real, utilizando la cámara del navegador o una cámara IP, con procesamiento local (edge AI) y registro inteligente en Supabase.

## 🚀 Características Principales

- ✅ **Detección en Tiempo Real**: Personas, rostros, objetos, manos y poses
- ✅ **Detección de Objetos**: YOLO detecta más de 80 clases de objetos (personas, vehículos, dispositivos, muebles, comida, ropa, herramientas, y más)
- ✅ **Análisis Emocional**: Clasificación de emociones basada en landmarks faciales
- ✅ **Detección de Movimiento**: Patrones de actividad (activo, inactivo, caída, sentado)
- ✅ **Estado de Salud Estimado**: Signos de cansancio, concentración o alerta
- ✅ **Procesamiento Local**: Edge AI sin enviar imágenes a servidores
- ✅ **Dashboard Interactivo**: Métricas, estadísticas y alertas en tiempo real
- ✅ **Registro Automático**: Eventos guardados en Supabase con timestamps
- ✅ **Configuración Dinámica**: Umbrales, frecuencia, modelos activados
- 🧠 **Sistema de ML y Entrenamiento**: Recolección de datos, fine-tuning de modelos y mejora continua
- 📊 **Gestión de Datasets**: Almacenamiento y anotación de datos para entrenamiento
- 🔄 **Aprendizaje Continuo**: El sistema mejora con el uso

## 📋 Requisitos Previos

- **Node.js**: 22.x
- **Python**: 3.11+
- **npm** o **yarn**
- **Cuenta de Supabase** (gratuita)

## 🛠️ Instalación

### 1. Clonar e Instalar Dependencias

```bash
# Instalar dependencias del workspace
npm install

# Instalar dependencias del frontend
cd apps/web
npm install

# Instalar dependencias del backend
cd ../api
pip install -r requirements.txt
```

### 2. Configurar Supabase

1. Crea un proyecto en [Supabase](https://supabase.com)
2. Ejecuta el SQL de inicialización (ver `infra/supabase/schema.sql`)
3. Obtén tu URL y anon key desde el dashboard

### 3. Configurar Variables de Entorno

#### Frontend (`apps/web/.env`)

```env
VITE_SUPABASE_URL=tu_url_de_supabase
VITE_SUPABASE_ANON_KEY=tu_anon_key
VITE_API_URL=http://localhost:8000
```

#### Backend (`apps/api/.env`)

```env
SUPABASE_URL=tu_url_de_supabase
SUPABASE_SERVICE_ROLE_KEY=tu_service_role_key
OPENAI_API_KEY=tu_openai_key_opcional
```

### 4. Ejecutar el Proyecto

#### Terminal 1 - Frontend
```bash
npm run dev:web
```
El frontend estará disponible en `http://localhost:5173`

#### Terminal 2 - Backend
```bash
npm run dev:api
```
El backend estará disponible en `http://localhost:8000`

## 📁 Estructura del Proyecto

```
vision-aiagentek/
├── apps/
│   ├── web/              # React + Vite + TypeScript
│   │   ├── src/
│   │   │   ├── components/    # Componentes UI
│   │   │   ├── pages/         # Páginas principales
│   │   │   ├── store/         # Zustand state management
│   │   │   ├── lib/           # Utilidades y hooks
│   │   │   └── types.ts       # Tipos TypeScript
│   │   └── package.json
│   └── api/              # FastAPI Backend
│       ├── main.py
│       ├── models.py
│       ├── routers/
│       └── requirements.txt
├── packages/
│   └── shared/           # Tipos compartidos
├── infra/
│   └── supabase/         # Esquemas SQL
└── README.md
```

## 🎮 Uso

1. **Aceptar Privacidad**: Al iniciar, acepta el banner de privacidad
2. **Permitir Cámara**: El navegador solicitará acceso a la cámara
3. **Activar Modelos**: Usa los toggles para activar detecciones específicas
4. **Ver Dashboard**: Navega a la sección de eventos para ver métricas
5. **Configurar**: Ajusta umbrales y frecuencia en la sección de configuración

## 🔧 Modelos de IA Utilizados

- **YOLOv8n/YOLO11n**: Detección de objetos y personas (ONNX Runtime Web)
- **MediaPipe Face Landmarker**: Detección facial y landmarks
- **MediaPipe Pose**: Detección de postura corporal
- **MediaPipe Hands**: Detección de manos
- **TensorFlow.js**: Clasificación de emociones (7 clases)
- **OpenCV.js**: Detección de movimiento por diferencia de frames

## 📊 Base de Datos

El sistema utiliza Supabase (PostgreSQL) con las siguientes tablas:

- **events**: Registro de eventos detectados
- **users**: Usuarios (manejado por Supabase Auth)

## 🔒 Privacidad y Ética

- ✅ **Procesamiento Local**: Inferencia en el navegador (edge AI)
- ✅ **Sin Almacenamiento de Imágenes**: Solo metadatos por defecto
- ✅ **Consentimiento Explícito**: Banner de privacidad visible
- ✅ **Modo Anonimizado**: Opción para ocultar datos sensibles
- ✅ **Código Abierto**: Transparencia total del código

## 🚧 Roadmap Futuro

- [ ] Generación de reportes PDF mensuales
- [ ] Resúmenes por voz con Text-to-Speech (ElevenLabs/OpenAI)
- [ ] Autoaprendizaje básico con reentrenamiento local
- [ ] Alertas en tiempo real con WebSocket
- [ ] Soporte para múltiples cámaras IP
- [ ] Panel analítico avanzado con gráficas interactivas

## 📝 Licencia

MIT License - Ver `LICENSE` para más detalles

## 🤝 Contribuciones

Este es un proyecto de demostración. Las contribuciones son bienvenidas.

## ⚠️ Avisos Importantes

1. **Privacidad**: Este sistema procesa datos biométricos. Úsalo de forma responsable y con consentimiento explícito.
2. **Rendimiento**: El procesamiento local puede ser intensivo. Se recomienda usar hardware moderno.
3. **Precisión**: Los modelos son aproximaciones. No deben usarse para diagnósticos médicos reales.
4. **Dependencias**: Todas las dependencias base son gratuitas, pero algunas funcionalidades opcionales (OpenAI, ElevenLabs) pueden requerir API keys.

## 📧 Soporte

Para preguntas o problemas, consulta la documentación o crea un issue en el repositorio.

---

**Desarrollado con ❤️ por IAGENTEK**

