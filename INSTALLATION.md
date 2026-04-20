# 📦 Guía de Instalación Detallada

Esta guía te llevará paso a paso para configurar y ejecutar el proyecto **Vision Human Insight**.

## 📋 Requisitos Previos

### Software Necesario

1. **Node.js 22.x**
   - Descargar desde [nodejs.org](https://nodejs.org/)
   - Verificar instalación: `node --version`

2. **Python 3.11+**
   - Descargar desde [python.org](https://www.python.org/downloads/)
   - Verificar instalación: `python --version`

3. **npm** (viene con Node.js)
   - Verificar instalación: `npm --version`

4. **Git** (opcional, para clonar repositorio)
   - Descargar desde [git-scm.com](https://git-scm.com/)

### Cuenta de Supabase

1. Crear cuenta gratuita en [supabase.com](https://supabase.com)
2. Crear un nuevo proyecto
3. Anotar la URL del proyecto y las API keys

## 🚀 Instalación Paso a Paso

### Paso 1: Clonar o Descargar el Proyecto

```bash
# Si usas Git
git clone <url-del-repositorio>
cd vision-aiagentek

# O simplemente navegar a la carpeta del proyecto
cd "Vision Human Insight"
```

### Paso 2: Instalar Dependencias del Frontend

```bash
# Navegar a la carpeta del frontend
cd apps/web

# Instalar dependencias de Node.js
npm install

# Esto instalará:
# - React, Vite, TypeScript
# - Tailwind CSS
# - Supabase client
# - Modelos de ML (onnxruntime-web, mediapipe, etc.)
# - Otras dependencias
```

### Paso 3: Instalar Dependencias del Backend

```bash
# Abrir nueva terminal
# Navegar a la carpeta del backend
cd apps/api

# Crear entorno virtual de Python (recomendado)
python -m venv venv

# Activar entorno virtual
# En Windows:
venv\Scripts\activate
# En Linux/Mac:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Esto instalará:
# - FastAPI
# - Supabase Python client
# - OpenAI SDK (opcional)
# - Otras dependencias
```

### Paso 4: Configurar Supabase

1. **Crear la Base de Datos:**
   - Ir a tu proyecto en Supabase
   - Abrir el **SQL Editor**
   - Copiar y pegar el contenido de `infra/supabase/schema.sql`
   - Ejecutar el script

2. **Obtener Credenciales:**
   - Ir a **Settings** > **API**
   - Copiar:
     - **Project URL**
     - **anon/public key** (para frontend)
     - **service_role key** (para backend - mantener segura)

### Paso 5: Configurar Variables de Entorno

#### Frontend (`apps/web/.env`)

Crear archivo `.env` en `apps/web/`:

```env
VITE_SUPABASE_URL=https://tu-proyecto.supabase.co
VITE_SUPABASE_ANON_KEY=tu_anon_key_aqui
VITE_API_URL=http://localhost:8000
```

#### Backend (`apps/api/.env`)

Crear archivo `.env` en `apps/api/`:

```env
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_SERVICE_ROLE_KEY=tu_service_role_key_aqui
OPENAI_API_KEY=tu_openai_key_opcional
FRONTEND_URL=http://localhost:5173
```

### Paso 6: Ejecutar el Proyecto

#### Terminal 1 - Backend (FastAPI)

```bash
# Desde la raíz del proyecto
cd apps/api

# Activar entorno virtual (si no está activo)
# Windows: venv\Scripts\activate
# Linux/Mac: source venv/bin/activate

# Ejecutar servidor
python main.py
# O alternativamente:
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

El backend estará disponible en: `http://localhost:8000`

Verificar que funciona: `http://localhost:8000/api/health`

#### Terminal 2 - Frontend (React + Vite)

```bash
# Desde la raíz del proyecto
cd apps/web

# Ejecutar servidor de desarrollo
npm run dev
```

El frontend estará disponible en: `http://localhost:5173`

### Paso 7: Probar la Aplicación

1. Abrir navegador en `http://localhost:5173`
2. Aceptar el banner de privacidad
3. Permitir acceso a la cámara cuando se solicite
4. Verificar que la cámara se active y muestre video
5. Navegar a diferentes secciones:
   - **Live**: Análisis en tiempo real
   - **Dashboard**: Estadísticas y gráficas
   - **Configuración**: Ajustar modelos y parámetros

## 🐛 Solución de Problemas

### Error: "No se puede acceder a la cámara"

- Verificar permisos del navegador
- Asegurarse de usar HTTPS o localhost (no IP)
- Cerrar otras aplicaciones que usen la cámara

### Error: "Faltan variables de entorno"

- Verificar que los archivos `.env` existen
- Verificar que las variables están correctamente escritas
- Reiniciar el servidor después de cambiar `.env`

### Error: "Error conectando con Supabase"

- Verificar que la URL y keys son correctas
- Verificar que el esquema SQL se ejecutó correctamente
- Verificar que RLS (Row Level Security) está configurado

### Error: "Modelos no cargan"

- Verificar conexión a internet (los modelos se descargan)
- Verificar la consola del navegador para errores específicos
- Los modelos pueden tardar en cargar la primera vez

### Backend no inicia

- Verificar que Python 3.11+ está instalado
- Verificar que todas las dependencias están instaladas: `pip install -r requirements.txt`
- Verificar que el puerto 8000 no está en uso

### Frontend no inicia

- Verificar que Node.js 22.x está instalado
- Eliminar `node_modules` y `package-lock.json`, luego `npm install`
- Verificar que el puerto 5173 no está en uso

## 📝 Notas Importantes

1. **Primera Ejecución**: Los modelos de ML pueden tardar en descargarse la primera vez
2. **Rendimiento**: El procesamiento local puede ser intensivo. Se recomienda hardware moderno
3. **Privacidad**: Las imágenes se procesan localmente, no se envían a servidores
4. **Datos**: Los eventos se guardan en Supabase con los permisos configurados

## 🎯 Próximos Pasos

Una vez instalado y funcionando:

1. Explorar la sección **Live** para ver detecciones en tiempo real
2. Configurar modelos en **Settings** según tus necesidades
3. Revisar el **Dashboard** para ver estadísticas
4. Consultar el código para entender cómo funciona cada módulo

## 📚 Recursos Adicionales

- [Documentación de Supabase](https://supabase.com/docs)
- [Documentación de FastAPI](https://fastapi.tiangolo.com/)
- [Documentación de React](https://react.dev/)
- [Documentación de MediaPipe](https://developers.google.com/mediapipe)

---

**¿Problemas?** Revisa los logs en la consola del navegador y terminales para más detalles.

