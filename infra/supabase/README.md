# 📚 Scripts SQL - Vision Human Insight

Este directorio contiene todos los scripts SQL necesarios para configurar la base de datos Supabase.

## 📋 Scripts Disponibles

### Scripts Principales

1. **`setup.sql`** ✅ **REQUERIDO**
   - Script principal que crea todas las tablas básicas
   - Crea `vishum_events` (tabla real)
   - Crea `vishum_recent_events` (vista materializada)
   - Funciones, índices, políticas RLS

2. **`limpiar_redundantes.sql`** ⚠️ **OPCIONAL**
   - Limpia tablas y vistas redundantes de ejecuciones anteriores
   - Ejecutar **SOLO** si ya ejecutaste scripts anteriores
   - Elimina tablas antiguas: `events`, `ml_*`, `recent_events`
   - Elimina vistas sinónimos redundantes

3. **`create_buckets.sql`** (Opcional)
   - Crea buckets de Storage automáticamente
   - Crea `vishum-images` y `vishum-models`

4. **`storage_setup.sql`** (Opcional)
   - Configura políticas RLS para Storage
   - Función `get_image_url()`

5. **`ml_training_setup.sql`** (Opcional)
   - Crea tablas de ML con nombres `vishum_ml_*`
   - Sistema completo de entrenamiento de modelos

6. **`verificar.sql`** (Recomendado)
   - Verifica que todo esté configurado correctamente

7. **`ejecutar_todo.sql`** (Opcional - Solo psql)
   - Script maestro que ejecuta todo automáticamente
   - Solo funciona con `psql` (línea de comandos)

## 🚀 Orden de Ejecución

### Primera Vez (Instalación Limpia)

```
1. setup.sql
2. create_buckets.sql (opcional)
3. storage_setup.sql (opcional)
4. ml_training_setup.sql (opcional)
5. verificar.sql (recomendado)
```

### Si Ya Ejecutaste Scripts Anteriores (Migración)

```
1. limpiar_redundantes.sql ⚠️
2. setup.sql
3. create_buckets.sql (opcional)
4. storage_setup.sql (opcional)
5. ml_training_setup.sql (opcional)
6. verificar.sql (recomendado)
```

## 📖 Documentación

- **[INSTRUCCIONES.md](INSTRUCCIONES.md)** - Guía paso a paso completa
- **[README_SCRIPTS.md](README_SCRIPTS.md)** - Detalles de cada script

## ✅ Convención de Nombres

**Todas las tablas reales usan el prefijo `vishum_*`:**
- `vishum_events` - Tabla principal de eventos
- `vishum_recent_events` - Vista materializada de eventos recientes
- `vishum_ml_*` - Tablas de Machine Learning

**NO hay sinónimos ni vistas redundantes** - Todo son tablas/vistas reales con nombres directos.

