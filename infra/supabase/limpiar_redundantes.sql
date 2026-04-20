-- ============================================================
-- SCRIPT DE LIMPIEZA - ELIMINAR TABLAS Y VISTAS REDUNDANTES
-- Vision Human Insight - IAGENTEK
-- ============================================================
-- INSTRUCCIONES:
-- Este script elimina SOLO las tablas y vistas redundantes que creamos
-- NO toca ninguna tabla que ya existía antes (iainmobiliaria_*, talentmatcher_*, etc.)
-- 
-- ⚠️ ADVERTENCIA: Este script eliminará:
-- - Tabla events (antigua, será reemplazada por vishum_events)
-- - Tablas ml_* (redundantes, las vistas vishum_ml_* apuntan a ellas)
-- - Vistas vishum_ml_* que apuntan a ml_* (redundantes)
-- - Vista materializada recent_events (antigua)
-- - Sinónimos vishum_events, vishum_recent_events, vishum_storage_objects (vistas redundantes)
-- - Políticas RLS de esas tablas antiguas
-- - Funciones que dependan de esas tablas antiguas
-- 
-- MANTIENE:
-- - Tablas vishum_* reales (vishum_events, vishum_recent_events, vishum_ml_*, etc.)
-- - Todas las demás tablas que ya existían (iainmobiliaria_*, talentmatcher_*, etc.)
-- ============================================================

-- ============================================================
-- 1. ELIMINAR VISTAS REDUNDANTES
-- ============================================================

-- Vistas vishum_ml_* que apuntan a ml_* (redundantes)
DROP VIEW IF EXISTS vishum_ml_datasets CASCADE;
DROP VIEW IF EXISTS vishum_ml_training_samples CASCADE;
DROP VIEW IF EXISTS vishum_ml_annotations CASCADE;
DROP VIEW IF EXISTS vishum_ml_models CASCADE;
DROP VIEW IF EXISTS vishum_ml_training_runs CASCADE;
DROP VIEW IF EXISTS vishum_ml_scraped_data CASCADE;

-- Sinónimos vishum_* adicionales (vistas redundantes - eliminamos)
-- NOTA: Estas son vistas que apuntan a tablas antiguas, no las tablas reales
-- IMPORTANTE: Solo eliminamos VISTAS, NO las tablas reales ni MATERIALIZED VIEWS
-- Si vishum_recent_events es una MATERIALIZED VIEW real, no se eliminará aquí
-- Si vishum_events es una tabla real, no se eliminará aquí
DROP VIEW IF EXISTS vishum_storage_objects CASCADE;

-- ============================================================
-- 2. ELIMINAR POLÍTICAS RLS DE TABLAS ml_* (si existen)
-- ============================================================

-- Políticas de ml_datasets
DROP POLICY IF EXISTS "Public read access for datasets" ON ml_datasets;
DROP POLICY IF EXISTS "Authenticated users can insert datasets" ON ml_datasets;

-- Políticas de ml_training_samples
DROP POLICY IF EXISTS "Public read access for training samples" ON ml_training_samples;
DROP POLICY IF EXISTS "Authenticated users can insert samples" ON ml_training_samples;

-- Políticas de ml_annotations
DROP POLICY IF EXISTS "Public read access for annotations" ON ml_annotations;
DROP POLICY IF EXISTS "Authenticated users can insert annotations" ON ml_annotations;

-- Políticas de ml_models
DROP POLICY IF EXISTS "Public read access for models" ON ml_models;
DROP POLICY IF EXISTS "Authenticated users can insert models" ON ml_models;

-- Políticas de ml_training_runs
DROP POLICY IF EXISTS "Public read access for training runs" ON ml_training_runs;
DROP POLICY IF EXISTS "Authenticated users can insert training runs" ON ml_training_runs;

-- Políticas de ml_scraped_data
DROP POLICY IF EXISTS "Public read access for scraped data" ON ml_scraped_data;
DROP POLICY IF EXISTS "Authenticated users can insert scraped data" ON ml_scraped_data;

-- ============================================================
-- 3. ELIMINAR TRIGGERS DE TABLAS ml_* (si existen)
-- ============================================================
-- NOTA: Estos triggers son de las tablas ml_* antiguas (sin prefijo vishum_)
-- Los triggers de las tablas vishum_ml_* se crean en ml_training_setup.sql

DROP TRIGGER IF EXISTS update_ml_datasets_updated_at ON ml_datasets;
DROP TRIGGER IF EXISTS update_ml_training_samples_updated_at ON ml_training_samples;
DROP TRIGGER IF EXISTS update_ml_annotations_updated_at ON ml_annotations;
DROP TRIGGER IF EXISTS update_ml_models_updated_at ON ml_models;
DROP TRIGGER IF EXISTS update_ml_training_runs_updated_at ON ml_training_runs;
DROP TRIGGER IF EXISTS update_ml_scraped_data_updated_at ON ml_scraped_data;

-- ============================================================
-- 4. DESHABILITAR RLS EN TABLAS ml_* (si existen)
-- ============================================================

ALTER TABLE IF EXISTS ml_datasets DISABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS ml_training_samples DISABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS ml_annotations DISABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS ml_models DISABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS ml_training_runs DISABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS ml_scraped_data DISABLE ROW LEVEL SECURITY;

-- ============================================================
-- 5. ELIMINAR ÍNDICES DE TABLAS ml_* (si existen)
-- ============================================================

-- Índices de ml_training_samples
DROP INDEX IF EXISTS idx_samples_dataset_id;
DROP INDEX IF EXISTS idx_samples_annotation_status;
DROP INDEX IF EXISTS idx_samples_is_annotated;
DROP INDEX IF EXISTS idx_samples_file_type;
DROP INDEX IF EXISTS idx_samples_labels_gin;

-- Índices de ml_annotations
DROP INDEX IF EXISTS idx_annotations_sample_id;
DROP INDEX IF EXISTS idx_annotations_type;
DROP INDEX IF EXISTS idx_annotations_label;
DROP INDEX IF EXISTS idx_annotations_is_manual;
DROP INDEX IF EXISTS idx_annotations_bbox_gin;

-- Índices de ml_models
DROP INDEX IF EXISTS idx_models_type;
DROP INDEX IF EXISTS idx_models_is_active;
DROP INDEX IF EXISTS idx_models_version;
DROP INDEX IF EXISTS idx_models_metrics_gin;

-- Índices de ml_training_runs
DROP INDEX IF EXISTS idx_runs_model_id;
DROP INDEX IF EXISTS idx_runs_dataset_id;
DROP INDEX IF EXISTS idx_runs_status;

-- Índices de ml_scraped_data
DROP INDEX IF EXISTS idx_scraped_source_type;
DROP INDEX IF EXISTS idx_scraped_is_processed;

-- ============================================================
-- 6. ELIMINAR FUNCIONES QUE DEPENDEN DE TABLAS ml_* (si existen)
-- ============================================================

-- NOTA IMPORTANTE: 
-- Solo eliminamos funciones si usan tablas ml_* directamente (antiguas)
-- Si las funciones ya fueron actualizadas para usar vishum_ml_*, 
-- ml_training_setup.sql las recreará con CREATE OR REPLACE (correcto)
--
-- ORDEN DE EJECUCIÓN RECOMENDADO:
-- 1. limpiar_redundantes.sql (elimina funciones antiguas)
-- 2. setup.sql
-- 3. ml_training_setup.sql (recrea funciones con tablas vishum_ml_*)

-- Función get_dataset_stats (versión antigua que usa ml_training_samples)
-- Si ya fue actualizada para usar vishum_ml_*, ml_training_setup.sql la recreará
DROP FUNCTION IF EXISTS get_dataset_stats(UUID);

-- Función get_active_model (versión antigua que usa ml_models)
-- Si ya fue actualizada para usar vishum_ml_*, ml_training_setup.sql la recreará
DROP FUNCTION IF EXISTS get_active_model(TEXT);

-- ============================================================
-- 7. ELIMINAR TABLA ANTIGUA events (si existe)
-- ============================================================
-- ⚠️ ADVERTENCIA: Esto eliminará la tabla events antigua
-- Si ya migraste a vishum_events, ejecuta esto
-- Si no, primero ejecuta setup.sql actualizado para crear vishum_events

-- Primero eliminar políticas RLS de events
DROP POLICY IF EXISTS "Users can view own events" ON events;
DROP POLICY IF EXISTS "Users can insert events" ON events;
DROP POLICY IF EXISTS "Users can delete own events" ON events;

-- Deshabilitar RLS
ALTER TABLE IF EXISTS events DISABLE ROW LEVEL SECURITY;

-- Eliminar índices de events
DROP INDEX IF EXISTS idx_events_user_id;
DROP INDEX IF EXISTS idx_events_event_type;
DROP INDEX IF EXISTS idx_events_created_at;
DROP INDEX IF EXISTS idx_events_payload;

-- Eliminar tabla events (antigua)
DROP TABLE IF EXISTS events CASCADE;

-- ============================================================
-- 8. ELIMINAR VISTA MATERIALIZADA recent_events (antigua)
-- ============================================================
-- ⚠️ ADVERTENCIA: Esto eliminará la vista materializada antigua
-- Si ya migraste a vishum_recent_events, ejecuta esto
DROP MATERIALIZED VIEW IF EXISTS recent_events CASCADE;

-- Eliminar función de refresh antigua
DROP FUNCTION IF EXISTS refresh_recent_events() CASCADE;

-- Eliminar índice de recent_events antigua
DROP INDEX IF EXISTS idx_recent_events_created_at;

-- ============================================================
-- 9. ELIMINAR TABLAS ml_* (REDUNDANTES)
-- ============================================================
-- ⚠️ ADVERTENCIA: Esto eliminará TODOS los datos de estas tablas
-- Solo ejecuta si estás seguro de que son redundantes

DROP TABLE IF EXISTS ml_scraped_data CASCADE;
DROP TABLE IF EXISTS ml_training_runs CASCADE;
DROP TABLE IF EXISTS ml_annotations CASCADE;
DROP TABLE IF EXISTS ml_training_samples CASCADE;
DROP TABLE IF EXISTS ml_models CASCADE;
DROP TABLE IF EXISTS ml_datasets CASCADE;

-- ============================================================
-- 10. VERIFICACIÓN
-- ============================================================
-- Verificar que las tablas ml_* fueron eliminadas
SELECT 
    'Tablas ml_* eliminadas' as accion,
    CASE 
        WHEN COUNT(*) = 0 THEN '✅ Correcto: No hay tablas ml_*'
        ELSE '⚠️  Advertencia: Aún existen ' || COUNT(*) || ' tablas ml_*'
    END as estado
FROM information_schema.tables
WHERE table_schema = 'public'
    AND table_name LIKE 'ml_%'
    AND table_name NOT LIKE 'vishum_ml_%';

-- Verificar que las vistas vishum_ml_* redundantes fueron eliminadas
SELECT 
    'Vistas vishum_ml_* redundantes eliminadas' as accion,
    CASE 
        WHEN COUNT(*) = 0 THEN '✅ Correcto: No hay vistas redundantes'
        ELSE '⚠️  Advertencia: Aún existen ' || COUNT(*) || ' vistas redundantes'
    END as estado
FROM information_schema.views
WHERE table_schema = 'public'
    AND table_name LIKE 'vishum_ml_%';

-- Verificar que recent_events fue eliminada
SELECT 
    'Vista materializada recent_events eliminada' as accion,
    CASE 
        WHEN COUNT(*) = 0 THEN '✅ Correcto: recent_events fue eliminada'
        ELSE '⚠️  Advertencia: recent_events aún existe'
    END as estado
FROM pg_matviews
WHERE matviewname = 'recent_events';

-- Verificar que sinónimos vishum_* (vistas redundantes) fueron eliminados
-- NOTA: No confundir con tablas/materialized views reales
SELECT 
    'Sinónimos vishum_* (vistas redundantes) eliminados' as accion,
    CASE 
        WHEN COUNT(*) = 0 THEN '✅ Correcto: No hay vistas sinónimos vishum_* redundantes'
        ELSE '⚠️  Advertencia: Aún existen ' || COUNT(*) || ' vistas sinónimos vishum_*'
    END as estado
FROM information_schema.views
WHERE table_schema = 'public'
    AND table_name LIKE 'vishum_%'
    AND table_name NOT LIKE 'vishum_ml_%';

-- Verificar tablas vishum_* reales (si existen, son correctas)
SELECT 
    'Tablas vishum_* reales' as accion,
    CASE 
        WHEN COUNT(*) > 0 THEN '✅ Correcto: Existen ' || COUNT(*) || ' tablas/vistas vishum_* reales'
        ELSE 'ℹ️  Info: No hay tablas vishum_* (ejecuta setup.sql actualizado)'
    END as estado,
    STRING_AGG(table_name, ', ' ORDER BY table_name) as tablas
FROM information_schema.tables
WHERE table_schema = 'public'
    AND table_name LIKE 'vishum_%'
    AND table_type IN ('BASE TABLE', 'VIEW', 'MATERIALIZED VIEW');

-- Verificar que tabla events antigua fue eliminada
SELECT 
    'Tabla events antigua eliminada' as accion,
    CASE 
        WHEN COUNT(*) = 0 THEN '✅ Correcto: events antigua fue eliminada'
        ELSE '⚠️  Advertencia: events antigua aún existe'
    END as estado
FROM information_schema.tables
WHERE table_schema = 'public'
    AND table_name = 'events'
    AND table_type = 'BASE TABLE';

-- ============================================================
-- SCRIPT COMPLETADO
-- ============================================================
-- Después de ejecutar este script:
-- 1. La tabla events antigua fue eliminada (migra a vishum_events)
-- 2. Las tablas ml_* redundantes fueron eliminadas
-- 3. Las vistas vishum_ml_* redundantes fueron eliminadas
-- 4. La vista materializada recent_events antigua fue eliminada
-- 5. Los sinónimos vishum_* redundantes fueron eliminados
-- 6. Solo quedan las tablas reales con prefijo vishum_* (sin redundancias)
-- 7. Ejecuta setup.sql actualizado para crear vishum_events y vishum_recent_events
-- 8. Si necesitas las tablas de ML, ejecuta ml_training_setup.sql actualizado
-- ============================================================

