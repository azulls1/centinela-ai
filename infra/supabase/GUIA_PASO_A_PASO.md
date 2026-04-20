# 🚀 Guía Paso a Paso - Configuración Completa de Supabase

## 📋 Pre-requisitos

Antes de empezar, asegúrate de tener:
- ✅ Acceso a tu proyecto Supabase
- ✅ Permisos de administrador en el SQL Editor
- ✅ Los buckets `vishum-images` y `vishum-models` ya creados (o los crearemos)

---

## 🔍 PASO 0: Verificar Estado Actual

Antes de empezar, verifica qué tienes actualmente:

### 0.1. Verificar Tablas Existentes

Ejecuta en el SQL Editor:

```sql
-- Ver qué tablas vishum_* ya existen
SELECT 
    table_name,
    table_type
FROM information_schema.tables
WHERE table_schema = 'public'
    AND (table_name LIKE 'vishum_%' OR table_name = 'events' OR table_name LIKE 'ml_%')
ORDER BY table_name;
```

### 0.2. Verificar Buckets de Storage

```sql
-- Ver qué buckets ya existen
SELECT 
    id,
    name,
    public,
    file_size_limit
FROM storage.buckets
WHERE id IN ('vishum-images', 'vishum-models')
ORDER BY id;
```

### 0.3. Decidir Ruta

**Si ves tablas `events` o `ml_*` sin prefijo `vishum_`:**
→ Necesitas ejecutar `limpiar_redundantes.sql` primero

**Si NO ves tablas antiguas:**
→ Puedes saltar directamente a `setup.sql`

---

## 📝 PASO 1: Limpiar Redundancias (SI ES NECESARIO)

**¿Cuándo ejecutar esto?**
- Si ya ejecutaste scripts anteriores
- Si ves tablas `events`, `ml_*` sin prefijo `vishum_`
- Si ves vistas sinónimos redundantes

**Si es tu primera vez**, puedes saltar este paso.

### 1.1. Abrir SQL Editor en Supabase

1. Ve a tu proyecto Supabase
2. Click en **SQL Editor** (icono de terminal/editor)
3. Click en **New Query**

### 1.2. Ejecutar Script de Limpieza

1. Abre el archivo: `infra/supabase/limpiar_redundantes.sql`
2. Copia TODO el contenido
3. Pega en el SQL Editor
4. Click en **Run** o presiona `Ctrl+Enter` (Windows) / `Cmd+Enter` (Mac)

**✅ Qué hace:**
- Elimina tablas antiguas (`events`, `ml_*`)
- Elimina vistas redundantes
- Elimina políticas RLS antiguas
- **NO elimina** tablas `vishum_*` reales

**⏱️ Tiempo estimado:** 5-10 segundos

### 1.3. Verificar Limpieza

Ejecuta:

```sql
-- Debe mostrar 0 tablas ml_* (sin prefijo vishum_)
SELECT COUNT(*) as tablas_ml_antiguas
FROM information_schema.tables
WHERE table_schema = 'public'
    AND table_name LIKE 'ml_%'
    AND table_name NOT LIKE 'vishum_ml_%';
```

**Resultado esperado:** `0` ✅

---

## 🗄️ PASO 2: Configurar Tabla Principal de Eventos

### 2.1. Ejecutar setup.sql

1. Abre el archivo: `infra/supabase/setup.sql`
2. Copia TODO el contenido
3. Pega en el SQL Editor
4. Click en **Run**

**✅ Qué crea:**
- Tabla `vishum_events` (eventos detectados)
- Vista materializada `vishum_recent_events` (optimización)
- Índices para rendimiento
- Políticas RLS (permite anónimos para desarrollo)
- Funciones: `get_event_stats()`, `get_recent_events()`

**⏱️ Tiempo estimado:** 10-15 segundos

### 2.2. Verificar Creación

Ejecuta:

```sql
-- Verificar que la tabla existe
SELECT 
    table_name,
    column_name,
    data_type
FROM information_schema.columns
WHERE table_name = 'vishum_events'
ORDER BY ordinal_position;
```

**Resultado esperado:** Debe mostrar 5 columnas (id, user_id, event_type, payload, created_at) ✅

### 2.3. Probar Inserción

```sql
-- Insertar evento de prueba
INSERT INTO vishum_events (event_type, payload, user_id) 
VALUES (
    'test_event',
    '{"test": true, "message": "Configuración exitosa"}'::jsonb,
    'anonymous'
)
RETURNING id, event_type, created_at;
```

**Resultado esperado:** Debe insertar y mostrar el evento ✅

---

## 🪣 PASO 3: Configurar Storage (Buckets)

### 3.1. Verificar si los Buckets Ya Existen

Ejecuta:

```sql
SELECT 
    id,
    name,
    public,
    file_size_limit
FROM storage.buckets
WHERE id IN ('vishum-images', 'vishum-models');
```

**Si ves ambos buckets:** ✅ Ya existen, salta al Paso 3.3

**Si NO ves los buckets:** Continúa con el Paso 3.2

### 3.2. Crear Buckets (Si No Existen)

1. Abre el archivo: `infra/supabase/create_buckets.sql`
2. Copia TODO el contenido
3. Pega en el SQL Editor
4. Click en **Run**

**✅ Qué crea:**
- Bucket `vishum-images` (público, 5MB, para imágenes)
- Bucket `vishum-models` (privado, 500MB, para modelos)

**⏱️ Tiempo estimado:** 5 segundos

**⚠️ Si hay error de permisos:**
- Crea los buckets manualmente desde el Dashboard:
  1. Ve a **Storage** → **Buckets**
  2. Click en **New Bucket**
  3. Configura según `create_buckets.sql`

### 3.3. Limpiar Políticas RLS Antiguas (OPCIONAL)

**¿Cuándo ejecutar esto?**
- Si ya tenías políticas RLS configuradas manualmente antes
- Si quieres asegurar políticas limpias

**Si es tu primera vez**, puedes saltar este paso.

1. Abre el archivo: `infra/supabase/limpiar_storage_policies.sql`
2. Copia TODO el contenido
3. Pega en el SQL Editor
4. Click en **Run**

**✅ Qué hace:**
- Elimina solo políticas RLS antiguas
- **NO elimina buckets** (son necesarios)

**⏱️ Tiempo estimado:** 3 segundos

### 3.4. Configurar Políticas RLS de Storage

1. Abre el archivo: `infra/supabase/storage_setup.sql`
2. Copia TODO el contenido
3. Pega en el SQL Editor
4. Click en **Run**

**✅ Qué crea:**
- Políticas RLS para `vishum-images`:
  - Lectura pública (cualquiera puede leer)
  - Escritura solo autenticada
  - Actualización solo autenticada
  - Eliminación solo autenticada
- Función helper `get_image_url()`

**⏱️ Tiempo estimado:** 5 segundos

### 3.5. Verificar Políticas de Storage

```sql
-- Verificar políticas creadas
SELECT 
    policyname,
    cmd
FROM pg_policies
WHERE tablename = 'objects'
    AND schemaname = 'storage'
    AND policyname LIKE '%vishum%'
ORDER BY policyname;
```

**Resultado esperado:** Debe mostrar 4 políticas para `vishum-images` ✅

---

## 🤖 PASO 4: Configurar Sistema de ML (OPCIONAL)

**¿Cuándo ejecutar esto?**
- Si vas a usar el sistema de entrenamiento de modelos
- Si vas a recolectar datos para ML
- Si necesitas las tablas de datasets y anotaciones

**Si NO necesitas ML**, puedes saltar este paso.

### 4.1. Ejecutar ml_training_setup.sql

1. Abre el archivo: `infra/supabase/ml_training_setup.sql`
2. Copia TODO el contenido
3. Pega en el SQL Editor
4. Click en **Run**

**✅ Qué crea:**
- Tablas: `vishum_ml_datasets`, `vishum_ml_training_samples`, `vishum_ml_annotations`, `vishum_ml_models`, `vishum_ml_training_runs`, `vishum_ml_scraped_data`
- Índices para todas las tablas
- Políticas RLS
- Funciones: `get_dataset_stats()`, `get_active_model()`
- Trigger para actualizar `updated_at` automáticamente

**⏱️ Tiempo estimado:** 15-20 segundos

### 4.2. Verificar Tablas ML

```sql
-- Verificar que todas las tablas ML fueron creadas
SELECT 
    table_name,
    table_type
FROM information_schema.tables
WHERE table_schema = 'public'
    AND table_name LIKE 'vishum_ml_%'
ORDER BY table_name;
```

**Resultado esperado:** Debe mostrar 6 tablas ✅

---

## ✅ PASO 5: Verificación Final Completa

### 5.1. Ejecutar Script de Verificación

1. Abre el archivo: `infra/supabase/verificar.sql`
2. Copia TODO el contenido
3. Pega en el SQL Editor
4. Click en **Run**

**✅ Qué verifica:**
- Tablas creadas
- Índices creados
- Políticas RLS
- Funciones creadas
- Vista materializada
- Buckets de Storage
- Inserción/lectura de eventos

**⏱️ Tiempo estimado:** 10 segundos

### 5.2. Checklist Manual

Verifica que todo esté correcto:

#### ✅ Tablas Principales
```sql
-- Debe mostrar vishum_events y vishum_recent_events
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name LIKE 'vishum_%'
AND table_type IN ('BASE TABLE', 'MATERIALIZED VIEW')
ORDER BY table_name;
```

#### ✅ Políticas RLS de Eventos
```sql
-- Debe mostrar 3 políticas
SELECT policyname FROM pg_policies 
WHERE tablename = 'vishum_events';
```

#### ✅ Funciones
```sql
-- Debe mostrar las funciones principales
SELECT routine_name FROM information_schema.routines
WHERE routine_schema = 'public'
AND routine_name IN ('get_event_stats', 'get_recent_events', 'refresh_vishum_recent_events')
ORDER BY routine_name;
```

#### ✅ Buckets de Storage
```sql
-- Debe mostrar ambos buckets
SELECT id, public FROM storage.buckets
WHERE id IN ('vishum-images', 'vishum-models')
ORDER BY id;
```

#### ✅ Políticas de Storage
```sql
-- Debe mostrar 4 políticas para vishum-images
SELECT COUNT(*) as total_politicas FROM pg_policies
WHERE tablename = 'objects'
AND schemaname = 'storage'
AND policyname LIKE '%vishum%';
```

---

## 🎯 Resumen de Pasos Completos

### Configuración Mínima (Solo Eventos)
```
1. setup.sql
2. create_buckets.sql (o verificar que existan)
3. storage_setup.sql
4. verificar.sql
```

### Configuración Completa (Con ML)
```
1. limpiar_redundantes.sql (si es necesario)
2. setup.sql
3. create_buckets.sql (o verificar que existan)
4. limpiar_storage_policies.sql (OPCIONAL)
5. storage_setup.sql
6. ml_training_setup.sql
7. verificar.sql
```

---

## ⚠️ Problemas Comunes y Soluciones

### Error: "relation already exists"
**Solución:** El script usa `IF NOT EXISTS`, así que es seguro. Puedes ignorar el warning o ejecutar `limpiar_redundantes.sql` primero.

### Error: "permission denied" al crear buckets
**Solución:** Crea los buckets manualmente desde el Dashboard de Supabase:
1. Storage → Buckets → New Bucket
2. Configura según `create_buckets.sql`

### Error: "policy already exists" en storage
**Solución:** El script usa `DROP POLICY IF EXISTS` antes de crear, así que debería funcionar. Si persiste, ejecuta `limpiar_storage_policies.sql` primero.

### No veo las tablas en el Dashboard
**Solución:** 
1. Verifica que ejecutaste `setup.sql` correctamente
2. Ejecuta `verificar.sql` para diagnosticar
3. Revisa los mensajes de error en el SQL Editor

### Los buckets no aparecen
**Solución:**
1. Verifica permisos de administrador
2. Crea los buckets manualmente desde el Dashboard
3. Luego ejecuta `storage_setup.sql` para las políticas

---

## ✅ Estado Final Esperado

Después de completar todos los pasos, deberías tener:

### Tablas
- ✅ `vishum_events` (eventos detectados)
- ✅ `vishum_recent_events` (vista materializada)
- ✅ `vishum_ml_datasets` (si ejecutaste ML)
- ✅ `vishum_ml_training_samples` (si ejecutaste ML)
- ✅ `vishum_ml_annotations` (si ejecutaste ML)
- ✅ `vishum_ml_models` (si ejecutaste ML)
- ✅ `vishum_ml_training_runs` (si ejecutaste ML)
- ✅ `vishum_ml_scraped_data` (si ejecutaste ML)

### Buckets
- ✅ `vishum-images` (público, 5MB)
- ✅ `vishum-models` (privado, 500MB)

### Funciones
- ✅ `get_event_stats()`
- ✅ `get_recent_events()`
- ✅ `refresh_vishum_recent_events()`
- ✅ `get_image_url()` (Storage)
- ✅ `get_dataset_stats()` (si ejecutaste ML)
- ✅ `get_active_model()` (si ejecutaste ML)

### Políticas RLS
- ✅ 3 políticas para `vishum_events`
- ✅ 4 políticas para Storage (`vishum-images`)
- ✅ Políticas para todas las tablas ML (si ejecutaste ML)

---

## 🎉 ¡Listo!

Tu Supabase está configurado al 100%. Puedes:
- ✅ Usar el frontend para insertar eventos
- ✅ Almacenar imágenes en Storage
- ✅ Entrenar modelos de ML (si configuraste ML)
- ✅ Consultar estadísticas y eventos

**¿Necesitas ayuda?** Revisa `INSTRUCCIONES.md` o `README_SCRIPTS.md` para más detalles.

