-- ============================================================
-- SCRIPT PARA LIMPIAR POLÍTICAS RLS ANTIGUAS DE STORAGE
-- Vision Human Insight - IAGENTEK
-- ============================================================
-- INSTRUCCIONES:
-- Este script elimina SOLO las políticas RLS antiguas de storage
-- NO elimina los buckets (vishum-images y vishum-models son necesarios)
-- 
-- ⚠️ IMPORTANTE: Los buckets NO deben eliminarse
-- Este script solo limpia políticas RLS obsoletas
-- 
-- Ejecuta este script ANTES de ejecutar storage_setup.sql
-- para asegurar políticas limpias y actualizadas
-- ============================================================

-- ============================================================
-- 1. ELIMINAR POLÍTICAS RLS ANTIGUAS DE vishum-images
-- ============================================================

-- Políticas de lectura
DROP POLICY IF EXISTS "Public read access for vishum images" ON storage.objects;
DROP POLICY IF EXISTS "public_read_vishum_images" ON storage.objects;
DROP POLICY IF EXISTS "vishum_images_read" ON storage.objects;
DROP POLICY IF EXISTS "Allow public read vishum-images" ON storage.objects;

-- Políticas de inserción
DROP POLICY IF EXISTS "Authenticated users can upload vishum images" ON storage.objects;
DROP POLICY IF EXISTS "authenticated_upload_vishum_images" ON storage.objects;
DROP POLICY IF EXISTS "vishum_images_insert" ON storage.objects;
DROP POLICY IF EXISTS "Allow authenticated upload vishum-images" ON storage.objects;

-- Políticas de actualización
DROP POLICY IF EXISTS "Authenticated users can update vishum images" ON storage.objects;
DROP POLICY IF EXISTS "authenticated_update_vishum_images" ON storage.objects;
DROP POLICY IF EXISTS "vishum_images_update" ON storage.objects;
DROP POLICY IF EXISTS "Allow authenticated update vishum-images" ON storage.objects;

-- Políticas de eliminación
DROP POLICY IF EXISTS "Authenticated users can delete vishum images" ON storage.objects;
DROP POLICY IF EXISTS "authenticated_delete_vishum_images" ON storage.objects;
DROP POLICY IF EXISTS "vishum_images_delete" ON storage.objects;
DROP POLICY IF EXISTS "Allow authenticated delete vishum-images" ON storage.objects;

-- Políticas permisivas (desarrollo)
DROP POLICY IF EXISTS "Allow all operations for vishum-images" ON storage.objects;
DROP POLICY IF EXISTS "Allow all vishum-images" ON storage.objects;
DROP POLICY IF EXISTS "vishum_images_all" ON storage.objects;

-- ============================================================
-- 2. ELIMINAR POLÍTICAS RLS ANTIGUAS DE vishum-models
-- ============================================================

-- Políticas de lectura (modelos son privados)
DROP POLICY IF EXISTS "Authenticated users can read vishum models" ON storage.objects;
DROP POLICY IF EXISTS "authenticated_read_vishum_models" ON storage.objects;
DROP POLICY IF EXISTS "vishum_models_read" ON storage.objects;
DROP POLICY IF EXISTS "Allow authenticated read vishum-models" ON storage.objects;

-- Políticas de inserción
DROP POLICY IF EXISTS "Authenticated users can upload vishum models" ON storage.objects;
DROP POLICY IF EXISTS "authenticated_upload_vishum_models" ON storage.objects;
DROP POLICY IF EXISTS "vishum_models_insert" ON storage.objects;
DROP POLICY IF EXISTS "Allow authenticated upload vishum-models" ON storage.objects;

-- Políticas de actualización
DROP POLICY IF EXISTS "Authenticated users can update vishum models" ON storage.objects;
DROP POLICY IF EXISTS "authenticated_update_vishum_models" ON storage.objects;
DROP POLICY IF EXISTS "vishum_models_update" ON storage.objects;
DROP POLICY IF EXISTS "Allow authenticated update vishum-models" ON storage.objects;

-- Políticas de eliminación
DROP POLICY IF EXISTS "Authenticated users can delete vishum models" ON storage.objects;
DROP POLICY IF EXISTS "authenticated_delete_vishum_models" ON storage.objects;
DROP POLICY IF EXISTS "vishum_models_delete" ON storage.objects;
DROP POLICY IF EXISTS "Allow authenticated delete vishum-models" ON storage.objects;

-- Políticas permisivas (desarrollo)
DROP POLICY IF EXISTS "Allow all operations for vishum-models" ON storage.objects;
DROP POLICY IF EXISTS "Allow all vishum-models" ON storage.objects;
DROP POLICY IF EXISTS "vishum_models_all" ON storage.objects;

-- ============================================================
-- 3. VERIFICACIÓN
-- ============================================================

-- Verificar que las políticas fueron eliminadas
SELECT 
    'Políticas RLS de storage eliminadas' as accion,
    CASE 
        WHEN COUNT(*) = 0 THEN '✅ Correcto: No hay políticas antiguas de vishum'
        ELSE '⚠️  Advertencia: Aún existen ' || COUNT(*) || ' políticas antiguas'
    END as estado,
    STRING_AGG(policyname, ', ' ORDER BY policyname) as políticas_restantes
FROM pg_policies
WHERE tablename = 'objects'
    AND schemaname = 'storage'
    AND (
        policyname LIKE '%vishum%' 
        OR policyname LIKE '%Vishum%'
        OR policyname LIKE '%VISHUM%'
    );

-- Verificar que los buckets siguen existiendo (NO deben eliminarse)
SELECT 
    'Buckets vishum verificados' as accion,
    CASE 
        WHEN COUNT(*) = 2 THEN '✅ Correcto: Ambos buckets existen'
        WHEN COUNT(*) = 1 THEN '⚠️  Advertencia: Solo existe 1 bucket (verificar cuál falta)'
        ELSE '❌ Error: Los buckets no existen (deben crearse con create_buckets.sql)'
    END as estado,
    STRING_AGG(id, ', ' ORDER BY id) as buckets
FROM storage.buckets
WHERE id IN ('vishum-images', 'vishum-models');

-- ============================================================
-- SCRIPT COMPLETADO
-- ============================================================
-- Después de ejecutar este script:
-- 1. Las políticas RLS antiguas fueron eliminadas
-- 2. Los buckets vishum-images y vishum-models siguen existiendo (correcto)
-- 3. Ejecuta storage_setup.sql para crear las nuevas políticas RLS
-- ============================================================

