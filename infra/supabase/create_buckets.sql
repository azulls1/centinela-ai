-- ============================================================
-- SCRIPT PARA CREAR BUCKETS DE STORAGE
-- Vision Human Insight - IAGENTEK
-- ============================================================
-- INSTRUCCIONES:
-- Este script crea automáticamente los buckets necesarios
-- Ejecuta este script después de setup.sql
-- ============================================================

-- ============================================================
-- 1. BUCKET PARA IMÁGENES (vishum-images)
-- ============================================================

DO $$
BEGIN
    -- Verificar si el bucket ya existe
    IF NOT EXISTS (
        SELECT 1 FROM storage.buckets WHERE id = 'vishum-images'
    ) THEN
        -- Crear el bucket para imágenes
        INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
        VALUES (
            'vishum-images',
            'vishum-images',
            true,  -- Bucket público (lectura pública)
            5242880,  -- 5MB límite por archivo
            ARRAY['image/jpeg', 'image/png', 'image/webp', 'image/jpg']
        );
        RAISE NOTICE '✅ Bucket vishum-images creado exitosamente';
    ELSE
        RAISE NOTICE 'ℹ️  Bucket vishum-images ya existe';
    END IF;
EXCEPTION
    WHEN OTHERS THEN
        RAISE WARNING '⚠️  Error al crear bucket vishum-images: %', SQLERRM;
        RAISE NOTICE '💡 Si el error es de permisos, crea el bucket manualmente desde el Dashboard';
END $$;

-- ============================================================
-- 2. BUCKET PARA MODELOS (vishum-models)
-- ============================================================

DO $$
BEGIN
    -- Verificar si el bucket ya existe
    IF NOT EXISTS (
        SELECT 1 FROM storage.buckets WHERE id = 'vishum-models'
    ) THEN
        -- Crear el bucket para modelos de ML
        INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
        VALUES (
            'vishum-models',
            'vishum-models',
            false,  -- Bucket privado (los modelos no deben ser públicos)
            524288000,  -- 500MB límite por archivo (los modelos pueden ser grandes)
            ARRAY['application/octet-stream', 'application/x-tar', 'application/zip', 'application/gzip']
        );
        RAISE NOTICE '✅ Bucket vishum-models creado exitosamente';
    ELSE
        RAISE NOTICE 'ℹ️  Bucket vishum-models ya existe';
    END IF;
EXCEPTION
    WHEN OTHERS THEN
        RAISE WARNING '⚠️  Error al crear bucket vishum-models: %', SQLERRM;
        RAISE NOTICE '💡 Si el error es de permisos, crea el bucket manualmente desde el Dashboard';
END $$;

-- ============================================================
-- 3. VERIFICACIÓN DE BUCKETS CREADOS
-- ============================================================

-- Listar todos los buckets creados
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

-- ============================================================
-- SCRIPT COMPLETADO
-- ============================================================
-- Si ves los buckets listados arriba, se crearon correctamente
-- Si no aparecen, verifica los permisos o créalos manualmente
-- ============================================================

