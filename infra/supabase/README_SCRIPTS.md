# 📜 Guía de Scripts SQL - Vision Human Insight

Esta guía explica todos los scripts SQL disponibles y cómo ejecutarlos.

## 📋 Scripts Disponibles

### 1. `limpiar_redundantes.sql` ⚠️ OPCIONAL
**Descripción:** Limpia tablas y vistas redundantes creadas anteriormente.

**Contenido:**
- Elimina tabla `events` antigua
- Elimina tablas `ml_*` redundantes
- Elimina vistas sinónimos `vishum_*` redundantes
- Elimina vista materializada `recent_events` antigua

**Ejecutar:** Solo si ya ejecutaste scripts anteriores y quieres migrar a la nueva estructura.

### 2. `setup.sql` ✅ REQUERIDO
**Descripción:** Script principal que configura la base de datos básica.

**Contenido:**
- Tabla `vishum_events` para almacenar eventos detectados (tabla real, no sinónimo)
- Vista materializada `vishum_recent_events` (vista real, no sinónimo)
- Índices para mejorar rendimiento
- Políticas RLS (Row Level Security)
- Funciones: `get_event_stats`, `get_recent_events`, `refresh_vishum_recent_events`
- **NO crea sinónimos** (todo con nombres directos vishum_*)

**Ejecutar:** Siempre debe ejecutarse (después de limpiar si es necesario).

---

### 3. `create_buckets.sql` (Opcional)
**Descripción:** Crea los buckets de Storage automáticamente.

**Contenido:**
- Crea bucket `vishum-images` (público, para imágenes)
- Crea bucket `vishum-models` (privado, para modelos de ML)
- Verificación de buckets creados

**Ejecutar:** Antes de `storage_setup.sql` si quieres usar Storage.

---

### 4. `limpiar_storage_policies.sql` ⚠️ OPCIONAL
**Descripción:** Limpia políticas RLS antiguas de Storage (NO elimina buckets).

**Contenido:**
- Elimina políticas RLS antiguas de `vishum-images`
- Elimina políticas RLS antiguas de `vishum-models`
- Verifica que los buckets siguen existiendo (correcto)
- **NO elimina buckets** (son necesarios)

**Ejecutar:** Solo si ya tenías políticas configuradas manualmente antes. Ejecutar ANTES de `storage_setup.sql`.

---

### 5. `storage_setup.sql` (Opcional)
**Descripción:** Configura Storage con políticas RLS y funciones helper.

**Contenido:**
- Crea bucket `vishum-images` si no existe (idempotente)
- Habilita RLS en `storage.objects`
- Políticas RLS para lectura/escritura (con DROP IF EXISTS para evitar duplicados)
- Función `get_image_url()` helper
- **NO crea sinónimos** (acceso directo a storage.objects)

**Ejecutar:** Después de `create_buckets.sql` y opcionalmente `limpiar_storage_policies.sql`.

---

### 6. `ml_training_setup.sql` (Opcional)
**Descripción:** Configura el sistema completo de Machine Learning.

**Contenido:**
- Tablas: `vishum_ml_datasets`, `vishum_ml_training_samples`, `vishum_ml_annotations`, `vishum_ml_models`, `vishum_ml_training_runs`, `vishum_ml_scraped_data` (tablas reales, no sinónimos)
- Índices para todas las tablas
- Políticas RLS para todas las tablas
- Funciones: `get_dataset_stats`, `get_active_model`, `update_updated_at_column`
- **NO crea sinónimos** (todo con nombres directos vishum_ml_*)

**Ejecutar:** Después de `setup.sql` si quieres usar ML.

---

### 7. `verificar.sql` (Opcional)
**Descripción:** Script de verificación completa de la configuración.

**Contenido:**
- Verifica tablas creadas
- Verifica índices
- Verifica políticas RLS
- Verifica funciones
- Verifica vistas materializadas
- Verifica sinónimos
- Verifica buckets de Storage
- Verifica tablas de ML (si se ejecutó `ml_training_setup.sql`)

**Ejecutar:** Después de ejecutar todos los scripts que necesites.

---

### 8. `ejecutar_todo.sql` (Opcional - Solo psql)
**Descripción:** Script maestro que ejecuta todos los scripts en orden.

**Contenido:**
- Ejecuta `setup.sql`
- Ejecuta `create_buckets.sql`
- Ejecuta `storage_setup.sql`
- Ejecuta `ml_training_setup.sql` (comentado, descomentar si lo necesitas)
- Ejecuta `verificar.sql`

**Ejecutar:** Solo funciona con `psql` (línea de comandos), no en SQL Editor.

---

## 🔄 Orden de Ejecución Recomendado

### Configuración Mínima (Solo Funcionalidad Básica)
```
1. limpiar_redundantes.sql (si ya ejecutaste scripts anteriores)
2. setup.sql
3. verificar.sql (opcional)
```

### Con Storage (Para Almacenar Imágenes)
```
1. limpiar_redundantes.sql (si es necesario)
2. setup.sql
3. create_buckets.sql (o verifica que los buckets ya existan)
4. limpiar_storage_policies.sql (OPCIONAL - solo si tenías políticas antiguas)
5. storage_setup.sql
6. verificar.sql (opcional)
```

### Con ML (Para Entrenamiento de Modelos)
```
1. limpiar_redundantes.sql (si es necesario)
2. setup.sql
3. create_buckets.sql
4. storage_setup.sql (opcional)
5. ml_training_setup.sql
6. verificar.sql (opcional)
```

### Configuración Completa
```
1. limpiar_redundantes.sql (si es necesario)
2. setup.sql
3. create_buckets.sql (o verifica que los buckets ya existan)
4. limpiar_storage_policies.sql (OPCIONAL - solo si tenías políticas antiguas)
5. storage_setup.sql
6. ml_training_setup.sql
7. verificar.sql
```

---

## 🚀 Cómo Ejecutar

### Opción A: SQL Editor de Supabase (Recomendado)

1. Ve a tu proyecto Supabase
2. Abre **SQL Editor**
3. Copia y pega el contenido del script
4. Haz clic en **Run** (o Ctrl+Enter)

### Opción B: psql (Línea de Comandos)

```bash
# Conectar
psql -h db.iagenteksupabase.iagentek.com.mx -U admin -d postgres

# Ejecutar scripts individuales
\i infra/supabase/setup.sql
\i infra/supabase/create_buckets.sql
\i infra/supabase/storage_setup.sql
\i infra/supabase/ml_training_setup.sql

# O ejecutar todo de una vez
\i infra/supabase/ejecutar_todo.sql
```

---

## ✅ Verificación

Después de ejecutar los scripts, ejecuta `verificar.sql` para verificar que todo se configuró correctamente.

---

## ⚠️ Notas Importantes

1. **Idempotencia:** Todos los scripts son idempotentes (pueden ejecutarse múltiples veces sin problemas).

2. **Permisos:** Algunos scripts requieren permisos de administrador (especialmente para crear buckets).

3. **Dependencias:** 
   - `storage_setup.sql` requiere que `vishum-images` exista (se crea con `create_buckets.sql`)
   - `ml_training_setup.sql` requiere `setup.sql` ejecutado primero

4. **Convención de Nombres:**
   - Todas las tablas reales usan prefijo `vishum_*`
   - NO hay sinónimos ni vistas redundantes
   - Todo son tablas/vistas reales con nombres directos

5. **Errores Comunes:**
   - "relation already exists" → Normal, significa que ya existe
   - "permission denied" → Verifica permisos de administrador
   - "bucket already exists" → Normal, el script verifica antes de crear

## 🗑️ Scripts Eliminados

Los siguientes scripts fueron eliminados por ser redundantes o obsoletos:
- `schema.sql` - Versión antigua, usar `setup.sql`
- `limpiar.sql` - Versión antigua, usar `limpiar_redundantes.sql`
- `synonyms.sql` - Ya no se crean sinónimos, todo es directo

---

## 📚 Más Información

- Ver `INSTRUCCIONES.md` para guía paso a paso completa
- Ver comentarios en cada script SQL para detalles técnicos

