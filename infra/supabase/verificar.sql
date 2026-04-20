-- ============================================================
-- SCRIPT DE VERIFICACIÓN COMPLETA
-- Vision Human Insight - IAGENTEK
-- ============================================================
-- INSTRUCCIONES:
-- Ejecuta este script después de ejecutar los scripts SQL:
-- 1. setup.sql (requerido)
-- 2. storage_setup.sql (opcional)
-- 3. ml_training_setup.sql (opcional)
-- 
-- Este script verifica que todo se configuró correctamente
-- ============================================================

-- 1. Verificar que la tabla existe
SELECT 
    table_name,
    column_name,
    data_type
FROM information_schema.columns
WHERE table_name = 'vishum_events'
ORDER BY ordinal_position;

-- 2. Verificar índices
SELECT 
    indexname,
    indexdef
FROM pg_indexes
WHERE tablename = 'vishum_events';

-- 3. Verificar políticas RLS
SELECT 
    schemaname,
    tablename,
    policyname,
    permissive,
    roles,
    cmd,
    qual
FROM pg_policies
WHERE tablename = 'vishum_events';

-- 4. Verificar funciones
SELECT 
    routine_name,
    routine_type,
    data_type
FROM information_schema.routines
WHERE routine_schema = 'public'
    AND routine_name IN ('get_event_stats', 'get_recent_events', 'refresh_vishum_recent_events')
ORDER BY routine_name;

-- 5. Verificar vista materializada
SELECT 
    schemaname,
    matviewname
FROM pg_matviews
WHERE matviewname = 'vishum_recent_events';

-- 6. Insertar evento de prueba
INSERT INTO vishum_events (event_type, payload, user_id) 
VALUES (
    'test_event',
    '{"test": true, "message": "Verificación exitosa"}'::jsonb,
    'anonymous'
)
RETURNING id, event_type, created_at;

-- 7. Verificar que se puede leer el evento
SELECT 
    id,
    event_type,
    camera_id,
    payload,
    created_at
FROM vishum_events
WHERE event_type = 'test_event'
ORDER BY created_at DESC
LIMIT 1;

-- 8. Probar función de estadísticas
SELECT * FROM get_event_stats(24, NULL);

-- 9. Probar función de eventos recientes
SELECT * FROM get_recent_events(5, 0, NULL, NULL);

-- 10. Verificar tablas/vistas con prefijo vishum_
SELECT 
    table_name,
    table_type
FROM information_schema.tables
WHERE table_schema = 'public'
    AND table_name LIKE 'vishum_%'
ORDER BY table_name;

-- 11. Verificar tabla vishum_events
SELECT 
    'vishum_events' as table_name,
    COUNT(*) as total_rows
FROM vishum_events;

-- 12. Verificar vista materializada vishum_recent_events
SELECT 
    'vishum_recent_events' as view_name,
    COUNT(*) as total_rows
FROM vishum_recent_events;

-- 13. Verificar tabla vishum_external_cameras
SELECT 
    'vishum_external_cameras' AS table_name,
    COUNT(*) AS total_rows
FROM vishum_external_cameras;

-- 13. Verificar configuración de Storage (opcional)
-- Verificar que los buckets existen (requiere permisos de administrador)
SELECT 
    id,
    name,
    public,
    file_size_limit,
    allowed_mime_types,
    created_at
FROM storage.buckets
WHERE id IN ('vishum-images', 'vishum-models')
ORDER BY id;

-- Verificar políticas RLS de Storage
SELECT 
    schemaname,
    tablename,
    policyname,
    cmd
FROM pg_policies
WHERE tablename = 'objects'
    AND schemaname = 'storage'
    AND policyname LIKE '%vishum%'
ORDER BY policyname;

-- Verificar función helper de Storage
SELECT 
    routine_name,
    routine_type
FROM information_schema.routines
WHERE routine_schema = 'public'
    AND routine_name = 'get_image_url';

-- 14. Limpiar evento de prueba (opcional)
-- DELETE FROM vishum_events WHERE event_type = 'test_event';

-- ============================================================
-- Si todos los queries anteriores funcionan sin errores,
-- la configuración está correcta ✅
-- ============================================================

