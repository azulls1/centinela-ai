# 📋 Instrucciones para Configurar Supabase

Esta guía te llevará paso a paso para configurar tu proyecto Supabase con las credenciales proporcionadas.

## 🔑 Credenciales de Supabase

- **URL del Proyecto**: `https://iagenteksupabase.iagentek.com.mx`
- **Anon Key**: `eyJhbGciOiJlUzI1NilsInR5cCl6lkpXVCJ9.ewoglCJyb2xlljogImFub24iLAogICJpc3MiOiAic3VwYWJhc2UiLAogICJpYXQiOiAxNzE1MDUwODAwLAogICJleHAiOiAxODcyODE3MjAwCn0.23LYnOepZ9yTJObLFoTnszO5WdHpbekvgwMt8bn2o_k`
- **Service Role Key**: `eyJhbGciOiJlUzI1NilsInR5cCl6IkpXVCJ9.ewoglCJyb2xlljogInNlcnZpY2Vfcm9sZSIsCiAglmlzcyI6ICJzdXBhYmFzZSIsCiAglmlhdC16IDE3MTUwNTA4MDAsCiAglmV4cCI6IDE4NzI4MTcyMDAKfQ.82nFc9RPC-OtzNOsvrqQrnHUHHe51bJkpCUiC_uTypo`

## 📝 Paso 1: Ejecutar los Scripts SQL

### ⚠️ Orden de Ejecución Importante

**IMPORTANTE:** Si ya ejecutaste scripts anteriores, ejecuta primero `limpiar_redundantes.sql` para limpiar las tablas antiguas.

Ejecuta los scripts en este orden:

1. **`limpiar_redundantes.sql`** - Limpiar tablas/vistas redundantes (si ya ejecutaste scripts anteriores) ⚠️
2. **`setup.sql`** - Script principal (crea vishum_events, vishum_recent_events) ✅ REQUERIDO
3. **`create_buckets.sql`** - Crear buckets de Storage automáticamente (opcional)
4. **`storage_setup.sql`** - Configuración de Storage y políticas RLS (opcional)
5. **`ml_training_setup.sql`** - Sistema de ML y entrenamiento (opcional)

### Opción A: Usando el SQL Editor de Supabase (Recomendado)

#### 1.1. Script Principal (`setup.sql`)

1. **Accede a tu proyecto Supabase:**
   - Ve a [https://supabase.com](https://supabase.com)
   - Inicia sesión con tus credenciales
   - Selecciona tu proyecto

2. **Abre el SQL Editor:**
   - En el menú lateral izquierdo, haz clic en **"SQL Editor"**
   - O ve directamente a: `https://supabase.com/dashboard/project/[tu-proyecto-id]/sql`

3. **Crea un nuevo query:**
   - Haz clic en el botón **"+ New Query"** (o "+ Nuevo Query")

4. **Copia y ejecuta el script principal:**
   - Abre el archivo `infra/supabase/setup.sql` en tu editor
   - Selecciona todo el contenido (Ctrl+A / Cmd+A)
   - Copia el contenido (Ctrl+C / Cmd+C)
   - Pega en el editor de SQL de Supabase (Ctrl+V / Cmd+V)
   - Haz clic en **"Run"** (o presiona Ctrl+Enter / Cmd+Enter)
   - Espera a que se complete la ejecución

5. **Verifica la ejecución:**
   - Deberías ver mensajes de éxito como "Success. No rows returned"
   - Si hay errores, se mostrarán en rojo

#### 1.2. Crear Buckets (`create_buckets.sql`) - Opcional

Si quieres usar Storage para imágenes o modelos:

1. **Ejecuta el script de creación de buckets:**
   - Abre el archivo `infra/supabase/create_buckets.sql`
   - Copia y pega el contenido en el SQL Editor
   - Ejecuta el script
   - Esto creará automáticamente:
     - `vishum-images` (público, para imágenes)
     - `vishum-models` (privado, para modelos de ML)

2. **Verifica que se crearon:**
   - Deberías ver un mensaje de éxito
   - O verifica en **Storage** > **Buckets** del Dashboard

#### 1.3. Script de Storage (`storage_setup.sql`) - Opcional

Si quieres almacenar imágenes de eventos:

1. **Ejecuta el script de Storage:**
   - Abre el archivo `infra/supabase/storage_setup.sql`
   - Copia y pega el contenido en el SQL Editor
   - Ejecuta el script
   - Esto creará el bucket automáticamente (si no existe) y configurará las políticas RLS y funciones helper
   - **Nota:** Si ya ejecutaste `create_buckets.sql`, el bucket ya existe y el script lo detectará

#### 1.4. Script de ML (`ml_training_setup.sql`) - Opcional

Si quieres usar el sistema de Machine Learning y entrenamiento:

1. **Ejecuta el script de ML:**
   - Abre el archivo `infra/supabase/ml_training_setup.sql`
   - Copia y pega el contenido en el SQL Editor
   - Ejecuta el script
   - Esto creará todas las tablas, funciones y sinónimos de ML

2. **Nota sobre el bucket de modelos:**
   - El bucket `vishum-models` se crea automáticamente con `create_buckets.sql`
   - Si no ejecutaste `create_buckets.sql`, el bucket se creará cuando sea necesario

### Opción B: Usando psql (Línea de comandos)

Si tienes acceso a la base de datos directamente:

```bash
# Conectar a la base de datos
psql -h db.iagenteksupabase.iagentek.com.mx -U admin -d postgres

# Cuando te pida la contraseña, ingresa: lagentek_123

# Opción 1: Ejecutar scripts individuales
\i infra/supabase/setup.sql
\i infra/supabase/create_buckets.sql
\i infra/supabase/storage_setup.sql
\i infra/supabase/ml_training_setup.sql  # Opcional

# Opción 2: Ejecutar todo de una vez (script maestro)
\i infra/supabase/ejecutar_todo.sql
```

**Nota:** El script `ejecutar_todo.sql` ejecuta todos los scripts en orden automáticamente.

## ✅ Paso 2: Verificar la Configuración

### Verificar que la tabla se creó:

1. En Supabase, ve a **Table Editor**
2. Deberías ver la tabla **`events`**
3. Haz clic en ella para ver su estructura

### Verificar que RLS está activado:

1. En Supabase, ve a **Authentication** > **Policies**
2. O en **Table Editor**, haz clic en la tabla `events`
3. Ve a la pestaña **"RLS"** o **"Policies"**
4. Deberías ver las políticas creadas:
   - "Users can view own events"
   - "Users can insert events"
   - "Users can delete own events"

### Verificar funciones:

1. En Supabase, ve a **Database** > **Functions**
2. Deberías ver:
   - `get_event_stats`
   - `get_recent_events`
   - `refresh_recent_events`

### Verificar sinónimos (vistas con prefijo vishum_):

1. En Supabase, ve a **Table Editor** o **Database** > **Views**
2. Deberías ver las vistas:
   - `vishum_events` (sinónimo de `events`)
   - `vishum_recent_events` (sinónimo de `recent_events`)
   - `vishum_storage_objects` (si ejecutaste storage_setup.sql)
   - `vishum_ml_datasets`, `vishum_ml_training_samples`, etc. (si ejecutaste ml_training_setup.sql)
3. Puedes probar los sinónimos ejecutando:
   ```sql
   SELECT COUNT(*) FROM vishum_events;
   SELECT COUNT(*) FROM vishum_recent_events;
   ```

## 🔧 Paso 3: Configurar Variables de Entorno

Los archivos `.env` ya están configurados con tus credenciales:

- **Frontend**: `apps/web/.env` ✅ (ya configurado)
- **Backend**: `apps/api/.env` ✅ (ya configurado)

**No necesitas hacer nada más**, los archivos ya contienen tus credenciales.

## 🧪 Paso 4: Probar la Conexión

### Desde el Frontend:

1. Inicia el frontend: `cd apps/web && npm run dev`
2. Abre la consola del navegador (F12)
3. Deberías ver que se conecta a Supabase sin errores

### Desde el Backend:

1. Inicia el backend: `cd apps/api && python main.py`
2. Visita: `http://localhost:8000/api/health`
3. Deberías ver: `{"status": "healthy", "database": "connected"}`

### Insertar un evento de prueba:

Puedes usar el SQL Editor para insertar un evento de prueba:

```sql
INSERT INTO events (event_type, payload, user_id) 
VALUES (
    'person_detected',
    '{"confidence": 0.85, "persons": 1, "timestamp": "2024-01-01T00:00:00Z"}'::jsonb,
    'anonymous'
);

-- Verificar que se insertó
SELECT * FROM events ORDER BY created_at DESC LIMIT 1;
```

## 📊 Paso 5: Verificar Funciones y Sinónimos

### Probar función de estadísticas:

```sql
SELECT * FROM get_event_stats(24, NULL);
```

### Probar función de eventos recientes:

```sql
SELECT * FROM get_recent_events(10, 0, NULL, NULL);
```

### Probar sinónimos (vistas con prefijo vishum_):

```sql
-- Verificar que los sinónimos funcionan
SELECT COUNT(*) FROM vishum_events;
SELECT COUNT(*) FROM vishum_recent_events;

-- Comparar que retornan los mismos datos
SELECT * FROM events LIMIT 5;
SELECT * FROM vishum_events LIMIT 5;
```

**Nota:** Los sinónimos son vistas de solo lectura. Para INSERT/UPDATE/DELETE, usa las tablas originales (`events`).

## ⚠️ Notas Importantes

1. **Service Role Key**: 
   - Esta clave tiene permisos completos
   - **NUNCA** la expongas en el frontend
   - Solo úsala en el backend (FastAPI)

2. **Anon Key**:
   - Esta clave es segura para usar en el frontend
   - Está limitada por las políticas RLS

3. **RLS (Row Level Security)**:
   - Las políticas aseguran que los usuarios solo vean sus propios eventos
   - El backend con service_role_key puede ver todo

4. **Vista Materializada**:
   - Se actualiza periódicamente
   - Puedes refrescarla manualmente con: `SELECT refresh_recent_events();`

## 🐛 Solución de Problemas

### Error: "relation already exists"
- La tabla ya existe. Puedes eliminarla primero:
  ```sql
  DROP TABLE IF EXISTS events CASCADE;
  ```
  Luego ejecuta el script nuevamente.

### Error: "permission denied"
- Verifica que estás usando la cuenta correcta
- Asegúrate de tener permisos de administrador

### Error: "function already exists"
- Las funciones ya existen. Puedes eliminarlas primero:
  ```sql
  DROP FUNCTION IF EXISTS get_event_stats;
  DROP FUNCTION IF EXISTS get_recent_events;
  DROP FUNCTION IF EXISTS refresh_recent_events;
  DROP FUNCTION IF EXISTS get_image_url;
  DROP FUNCTION IF EXISTS get_dataset_stats;
  DROP FUNCTION IF EXISTS get_active_model;
  DROP FUNCTION IF EXISTS update_updated_at_column;
  ```

### Error: "policy already exists"
- Las políticas ya existen. Puedes eliminarlas primero:
  ```sql
  -- Para Storage
  DROP POLICY IF EXISTS "Public read access for vishum images" ON storage.objects;
  DROP POLICY IF EXISTS "Authenticated users can upload vishum images" ON storage.objects;
  DROP POLICY IF EXISTS "Authenticated users can update vishum images" ON storage.objects;
  DROP POLICY IF EXISTS "Authenticated users can delete vishum images" ON storage.objects;
  ```

### Error: "view already exists"
- Las vistas (sinónimos) ya existen. Puedes eliminarlas primero:
  ```sql
  DROP VIEW IF EXISTS vishum_events CASCADE;
  DROP VIEW IF EXISTS vishum_recent_events CASCADE;
  DROP VIEW IF EXISTS vishum_storage_objects CASCADE;
  DROP VIEW IF EXISTS vishum_ml_datasets CASCADE;
  DROP VIEW IF EXISTS vishum_ml_training_samples CASCADE;
  DROP VIEW IF EXISTS vishum_ml_annotations CASCADE;
  DROP VIEW IF EXISTS vishum_ml_models CASCADE;
  DROP VIEW IF EXISTS vishum_ml_training_runs CASCADE;
  DROP VIEW IF EXISTS vishum_ml_scraped_data CASCADE;
  ```

## ✅ Checklist Final

### Configuración Básica (Requerida)
- [ ] Script `setup.sql` ejecutado exitosamente
- [ ] Tabla `events` creada y visible
- [ ] RLS habilitado y políticas creadas
- [ ] Funciones creadas y verificadas:
  - [ ] `get_event_stats`
  - [ ] `get_recent_events`
  - [ ] `refresh_recent_events`
- [ ] Sinónimos `vishum_events` y `vishum_recent_events` creados y funcionando
- [ ] Variables de entorno configuradas
- [ ] Conexión desde frontend funciona
- [ ] Conexión desde backend funciona
- [ ] Evento de prueba insertado correctamente

### Configuración de Storage (Opcional)
- [ ] Script `create_buckets.sql` ejecutado (crea buckets automáticamente)
- [ ] Buckets `vishum-images` y `vishum-models` creados y verificados
- [ ] Script `storage_setup.sql` ejecutado
- [ ] Políticas RLS para Storage configuradas y verificadas
- [ ] Sinónimo `vishum_storage_objects` creado
- [ ] Función `get_image_url()` creada

### Configuración de ML (Opcional)
- [ ] Script `ml_training_setup.sql` ejecutado
- [ ] Tablas de ML creadas:
  - [ ] `ml_datasets`
  - [ ] `ml_training_samples`
  - [ ] `ml_annotations`
  - [ ] `ml_models`
  - [ ] `ml_training_runs`
  - [ ] `ml_scraped_data`
- [ ] Sinónimos `vishum_ml_*` creados
- [ ] Funciones de ML creadas:
  - [ ] `get_dataset_stats()`
  - [ ] `get_active_model()`
- [ ] Bucket `vishum-models` creado (opcional, para almacenar modelos)

## 📦 Paso 6: Configurar Storage (Opcional)

Si quieres almacenar imágenes de eventos detectados:

### 6.1. Crear buckets automáticamente:

**Opción A: Usando script SQL (Recomendado)**

1. Ejecuta el script `infra/supabase/create_buckets.sql`
2. Esto creará automáticamente:
   - `vishum-images` (público, 5MB, para imágenes)
   - `vishum-models` (privado, 500MB, para modelos)

**Opción B: Manual desde Dashboard (Alternativa)**

Si el script SQL falla por permisos:
1. Ve a **Storage** en el Dashboard de Supabase
2. Haz clic en **"New Bucket"**
3. Configura:
   - **Nombre**: `vishum-images`
   - **Público**: Sí (para lectura pública)
   - **File size limit**: 5MB
   - **Allowed MIME types**: `image/jpeg, image/png, image/webp`
4. Haz clic en **"Create bucket"**

### 6.2. Limpiar políticas RLS antiguas (OPCIONAL pero recomendado):

Si ya tenías políticas RLS configuradas manualmente antes:

1. Abre el SQL Editor
2. Ejecuta el script `infra/supabase/limpiar_storage_policies.sql`
3. Esto eliminará solo las políticas antiguas (NO elimina los buckets)
4. ⚠️ **IMPORTANTE**: Los buckets `vishum-images` y `vishum-models` NO deben eliminarse, son necesarios

### 6.3. Configurar políticas RLS para Storage:

1. Abre el SQL Editor
2. Copia y ejecuta el contenido de `infra/supabase/storage_setup.sql`
3. Esto creará las políticas RLS actualizadas para el bucket `vishum-images`

### 6.4. Verificar políticas de Storage:

```sql
SELECT
    schemaname,
    tablename,
    policyname,
    cmd,
    qual
FROM pg_policies
WHERE tablename = 'objects'
    AND schemaname = 'storage'
    AND policyname LIKE '%vishum%';
```

Deberías ver 4 políticas:
- `Public read access for vishum images`
- `Authenticated users can upload vishum images`
- `Authenticated users can update vishum images`
- `Authenticated users can delete vishum images`

### 6.5. Verificar función helper:

```sql
-- Probar la función get_image_url
SELECT get_image_url('vishum-images', 'test.jpg');
```

## 🧠 Paso 7: Configurar Sistema de ML (Opcional)

Si quieres usar el sistema de Machine Learning y entrenamiento:

### 7.1. Ejecutar script de ML:

1. Abre el SQL Editor
2. Copia y ejecuta el contenido de `infra/supabase/ml_training_setup.sql`
3. Esto creará todas las tablas necesarias para ML

### 7.2. Verificar tablas de ML:

```sql
-- Verificar que las tablas se crearon
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
  AND table_name LIKE 'ml_%'
ORDER BY table_name;
```

Deberías ver 6 tablas:
- `ml_datasets`
- `ml_training_samples`
- `ml_annotations`
- `ml_models`
- `ml_training_runs`
- `ml_scraped_data`

### 7.3. Verificar sinónimos de ML:

```sql
-- Verificar sinónimos
SELECT table_name 
FROM information_schema.views 
WHERE table_schema = 'public' 
  AND table_name LIKE 'vishum_ml_%'
ORDER BY table_name;
```

Deberías ver 6 vistas:
- `vishum_ml_datasets`
- `vishum_ml_training_samples`
- `vishum_ml_annotations`
- `vishum_ml_models`
- `vishum_ml_training_runs`
- `vishum_ml_scraped_data`

### 7.4. Bucket para modelos:

El bucket `vishum-models` se crea automáticamente con el script `create_buckets.sql`.
Si no lo ejecutaste, puedes crearlo manualmente o ejecutar `create_buckets.sql`.

### 7.5. Probar funciones de ML:

```sql
-- Probar función de estadísticas de dataset
SELECT * FROM get_dataset_stats('dataset-id-aqui');

-- Probar función de modelo activo
SELECT * FROM get_active_model('yolo');
```

### 7.6. Documentación adicional:

Para más información sobre el sistema de ML, consulta:
- 📖 [docs/ML_TRAINING_GUIDE.md](../../docs/ML_TRAINING_GUIDE.md) - Guía completa de entrenamiento

## 📚 Recursos Adicionales

### Documentación General
- [Documentación de Supabase](https://supabase.com/docs)
- [Guía de RLS](https://supabase.com/docs/guides/auth/row-level-security)
- [Supabase Storage](https://supabase.com/docs/guides/storage)
- [SQL Editor de Supabase](https://supabase.com/docs/guides/database/overview)

### Documentación del Proyecto
- [README.md](../../README.md) - Documentación principal del proyecto
- [INSTALLATION.md](../../INSTALLATION.md) - Guía de instalación detallada
- [docs/ML_TRAINING_GUIDE.md](../../docs/ML_TRAINING_GUIDE.md) - Guía de Machine Learning y entrenamiento

### Scripts SQL Disponibles

Para más detalles sobre cada script, consulta: [README_SCRIPTS.md](README_SCRIPTS.md)

**Scripts Activos (Usar):**
- `limpiar_redundantes.sql` - Limpiar tablas/vistas redundantes (ejecutar primero si ya tienes datos) ⚠️
- `setup.sql` - Script principal (crea vishum_events, vishum_recent_events) ✅ **REQUERIDO**
- `create_buckets.sql` - Crear buckets de Storage automáticamente (opcional)
- `storage_setup.sql` - Configuración de Storage y políticas RLS (opcional)
- `ml_training_setup.sql` - Sistema de ML y entrenamiento (opcional)
- `verificar.sql` - Script de verificación de configuración completa
- `ejecutar_todo.sql` - Script maestro que ejecuta todo automáticamente (solo para psql)

**Scripts Eliminados (Ya no se usan):**
- ~~`schema.sql`~~ - Versión antigua, usar `setup.sql`
- ~~`limpiar.sql`~~ - Versión antigua, usar `limpiar_redundantes.sql`
- ~~`synonyms.sql`~~ - Ya no se crean sinónimos, todo es directo

## 🔄 Resumen de Scripts SQL

### Orden de Ejecución Recomendado:

1. **`limpiar_redundantes.sql`** (OPCIONAL - Solo si ya ejecutaste scripts anteriores) ⚠️
   - Elimina tablas antiguas: `events`, `ml_*`, `recent_events`
   - Elimina vistas sinónimos redundantes
   - Prepara para migración a nombres vishum_*

2. **`setup.sql`** (REQUERIDO) ✅
   - Crea tablas principales: `vishum_events` (tabla real, no sinónimo)
   - Crea vista materializada: `vishum_recent_events` (vista real, no sinónimo)
   - Funciones: `get_event_stats`, `get_recent_events`, `refresh_vishum_recent_events`
   - RLS y políticas básicas
   - **NO crea sinónimos** (todo con nombres directos vishum_*)

3. **`create_buckets.sql`** (OPCIONAL)
   - Crea buckets automáticamente: `vishum-images`, `vishum-models`
   - No requiere configuración manual

4. **`storage_setup.sql`** (OPCIONAL)
   - Políticas RLS para `storage.objects`
   - Función `get_image_url()`
   - **NO crea sinónimos** (acceso directo a storage.objects)

5. **`ml_training_setup.sql`** (OPCIONAL)
   - Tablas de ML: `vishum_ml_datasets`, `vishum_ml_training_samples`, etc. (tablas reales)
   - Funciones de ML: `get_dataset_stats`, `get_active_model`
   - **NO crea sinónimos** (todo con nombres directos vishum_ml_*)
   - El bucket `vishum-models` se crea con `create_buckets.sql`

### Verificación Rápida:

Ejecuta el script `verificar.sql` para verificar toda la configuración:

```sql
-- Ejecuta el contenido de: infra/supabase/verificar.sql
```

---

**¿Problemas?** Revisa los logs en Supabase Dashboard > Logs para ver errores específicos.

**¿Necesitas ayuda?** Revisa la documentación del proyecto o consulta los scripts SQL que contienen comentarios detallados.

