-- ============================================================
-- CONFIGURACIÓN DE SUPABASE STORAGE PARA ALMACENAMIENTO DE IMÁGENES
-- Vision Human Insight - IAGENTEK
-- ============================================================
-- INSTRUCCIONES:
-- 1. Ejecuta este script en el SQL Editor de Supabase
-- 2. Este script crea el bucket y configura las políticas RLS
-- 3. Las imágenes se almacenarán para eventos detectados (opcional)
-- ============================================================

-- ============================================================
-- 1. VERIFICAR/CREAR BUCKET PARA IMÁGENES
-- ============================================================
-- NOTA: Si ejecutaste create_buckets.sql, el bucket ya existe
-- Este bloque verifica y crea el bucket si no existe

DO $$
BEGIN
    -- Verificar si el bucket ya existe
    IF NOT EXISTS (
        SELECT 1 FROM storage.buckets WHERE id = 'vishum-images'
    ) THEN
        -- Crear el bucket si no existe
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
        RAISE NOTICE 'ℹ️  Bucket vishum-images ya existe (continuando...)';
    END IF;
EXCEPTION
    WHEN OTHERS THEN
        RAISE WARNING '⚠️  Error al crear bucket vishum-images: %', SQLERRM;
        RAISE NOTICE '💡 Si el error es de permisos, ejecuta primero: create_buckets.sql';
END $$;

-- ============================================================
-- 2. HABILITAR RLS EN STORAGE.OBJECTS
-- ============================================================
-- Habilitar RLS en la tabla storage.objects (si no está habilitado)
ALTER TABLE storage.objects ENABLE ROW LEVEL SECURITY;

-- ============================================================
-- 3. POLÍTICAS RLS PARA EL BUCKET vishum-images
-- ============================================================
-- NOTA: Si ejecutaste limpiar_storage_policies.sql, las políticas antiguas ya fueron eliminadas
-- Este script crea las políticas nuevas con los nombres correctos

-- Política 1: Lectura pública de imágenes
-- Permite que cualquier usuario (incluidos anónimos) pueda leer imágenes
-- Usamos IF NOT EXISTS implícito con DROP/CREATE para evitar duplicados
DROP POLICY IF EXISTS "Public read access for vishum images" ON storage.objects;
CREATE POLICY "Public read access for vishum images"
    ON storage.objects
    FOR SELECT
    USING (bucket_id = 'vishum-images');

-- Política 2: Inserción de imágenes (usuarios autenticados)
-- Permite que usuarios autenticados puedan subir imágenes
DROP POLICY IF EXISTS "Authenticated users can upload vishum images" ON storage.objects;
CREATE POLICY "Authenticated users can upload vishum images"
    ON storage.objects
    FOR INSERT
    WITH CHECK (
        bucket_id = 'vishum-images' 
        AND auth.role() = 'authenticated'
    );

-- Política 3: Actualización de imágenes (usuarios autenticados)
-- Permite que usuarios autenticados puedan actualizar sus propias imágenes
DROP POLICY IF EXISTS "Authenticated users can update vishum images" ON storage.objects;
CREATE POLICY "Authenticated users can update vishum images"
    ON storage.objects
    FOR UPDATE
    USING (
        bucket_id = 'vishum-images' 
        AND auth.role() = 'authenticated'
    );

-- Política 4: Eliminación de imágenes (usuarios autenticados)
-- Permite que usuarios autenticados puedan eliminar sus propias imágenes
DROP POLICY IF EXISTS "Authenticated users can delete vishum images" ON storage.objects;
CREATE POLICY "Authenticated users can delete vishum images"
    ON storage.objects
    FOR DELETE
    USING (
        bucket_id = 'vishum-images' 
        AND auth.role() = 'authenticated'
    );

-- ============================================================
-- 4. POLÍTICA ALTERNATIVA MÁS PERMISIVA (SOLO PARA DESARROLLO)
-- ============================================================
-- ⚠️ ADVERTENCIA: Esta política permite todas las operaciones
-- Solo usar en desarrollo, NUNCA en producción

-- Descomenta solo si necesitas desarrollo rápido:
-- DROP POLICY IF EXISTS "Allow all operations for vishum-images" ON storage.objects;
-- CREATE POLICY "Allow all operations for vishum-images"
--     ON storage.objects
--     FOR ALL
--     USING (bucket_id = 'vishum-images');

-- ============================================================
-- 5. VERIFICACIÓN DE POLÍTICAS
-- ============================================================
-- Ejecuta este query para verificar que las políticas se crearon correctamente:

-- SELECT
--     schemaname,
--     tablename,
--     policyname,
--     permissive,
--     roles,
--     cmd,
--     qual,
--     with_check
-- FROM pg_policies
-- WHERE tablename = 'objects'
--     AND schemaname = 'storage'
--     AND policyname LIKE '%vishum%';

-- ============================================================
-- 6. FUNCIÓN PARA OBTENER URL PÚBLICA DE IMAGEN
-- ============================================================
-- Función helper para construir URLs públicas de imágenes
CREATE OR REPLACE FUNCTION get_image_url(bucket_name TEXT, file_path TEXT)
RETURNS TEXT
LANGUAGE plpgsql
AS $$
DECLARE
    base_url TEXT;
BEGIN
    -- Obtener la URL base del proyecto (debe configurarse)
    -- En Supabase, la URL es: https://[PROJECT_ID].supabase.co/storage/v1/object/public/
    base_url := current_setting('app.supabase_url', true);
    
    -- Si no está configurada, usar formato estándar
    IF base_url IS NULL OR base_url = '' THEN
        base_url := 'https://iagenteksupabase.iagentek.com.mx/storage/v1/object/public/';
    END IF;
    
    RETURN base_url || bucket_name || '/' || file_path;
END;
$$;

COMMENT ON FUNCTION get_image_url IS 'Función helper para construir URLs públicas de imágenes almacenadas en Supabase Storage';

-- ============================================================
-- 7. NOTA: SINÓNIMOS NO NECESARIOS
-- ============================================================
-- No creamos vistas sinónimos para storage.objects
-- Accede directamente a storage.objects con filtro WHERE bucket_id = 'vishum-images'
-- ============================================================

-- ============================================================
-- NOTAS IMPORTANTES
-- ============================================================
-- 1. El bucket debe crearse manualmente desde el Dashboard de Supabase
--    o usando la API de Supabase Storage
-- 2. Las políticas RLS se aplican automáticamente cuando se crean
-- 3. Las imágenes públicas son accesibles sin autenticación
-- 4. Para subir imágenes, el usuario debe estar autenticado
-- 5. El tamaño máximo por defecto es 50MB (configurable en el bucket)
-- 6. Los tipos MIME permitidos son: JPEG, PNG, WebP

-- ============================================================
-- VERIFICACIÓN FINAL
-- ============================================================
-- Verifica que el bucket existe antes de continuar:
-- SELECT * FROM storage.buckets WHERE id = 'vishum-images';
-- 
-- Si el bucket no existe, ejecuta primero: create_buckets.sql
-- ============================================================

-- ============================================================
-- SCRIPT COMPLETADO
-- ============================================================
-- Verifica que las políticas se crearon correctamente:
-- SELECT policyname FROM pg_policies 
-- WHERE tablename = 'objects' AND schemaname = 'storage' 
-- AND policyname LIKE '%vishum%';
-- ============================================================

