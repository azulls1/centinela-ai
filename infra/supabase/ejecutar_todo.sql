-- ============================================================
-- SCRIPT MAESTRO - EJECUTAR TODO AUTOMÁTICAMENTE
-- Vision Human Insight - IAGENTEK
-- ============================================================
-- INSTRUCCIONES:
-- Este script ejecuta todos los scripts de configuración en orden
-- Solo ejecuta este script si quieres configurar TODO de una vez
-- ============================================================
-- ⚠️ ADVERTENCIA: Este script ejecuta múltiples scripts
-- Asegúrate de tener permisos de administrador
-- ============================================================

\echo '🚀 Iniciando configuración completa de Supabase...'
\echo ''

-- ============================================================
-- PASO 0: LIMPIEZA (OPCIONAL - Descomentar si es necesario)
-- ============================================================
-- Descomenta si ya ejecutaste scripts anteriores y quieres limpiar:
-- \echo '🧹 Paso 0/5: Limpiando tablas redundantes...'
-- \i limpiar_redundantes.sql
-- \echo '✅ Limpieza completada'
-- \echo ''

-- ============================================================
-- PASO 1: SETUP PRINCIPAL
-- ============================================================
\echo '📋 Paso 1/5: Ejecutando setup.sql...'
\i setup.sql
\echo '✅ Setup principal completado'
\echo ''

-- ============================================================
-- PASO 2: CREAR BUCKETS
-- ============================================================
\echo '📦 Paso 2/5: Creando buckets de Storage...'
\i create_buckets.sql
\echo '✅ Buckets creados'
\echo ''

-- ============================================================
-- PASO 3: CONFIGURAR STORAGE
-- ============================================================
\echo '🔒 Paso 3/5: Configurando políticas de Storage...'
\i storage_setup.sql
\echo '✅ Storage configurado'
\echo ''

-- ============================================================
-- PASO 4: CONFIGURAR ML (OPCIONAL)
-- ============================================================
-- Descomenta las siguientes líneas si quieres configurar ML:
-- \echo '🧠 Paso 4/5: Configurando sistema de ML...'
-- \i ml_training_setup.sql
-- \echo '✅ Sistema de ML configurado'
-- \echo ''

-- ============================================================
-- PASO 5: VERIFICACIÓN
-- ============================================================

\echo '🔍 Paso 5/5: Verificando configuración...'
\i verificar.sql
\echo ''
\echo '✅ ✅ ✅ Configuración completa finalizada! ✅ ✅ ✅'
\echo ''
\echo '📝 Próximos pasos:'
\echo '1. Verifica las tablas en Table Editor'
\echo '2. Verifica los buckets en Storage'
\echo '3. Configura las variables de entorno en .env'
\echo '4. Prueba la conexión desde frontend/backend'
\echo ''

-- ============================================================
-- NOTA: Este script requiere psql
-- Si usas el SQL Editor de Supabase, ejecuta cada script por separado
-- ============================================================

