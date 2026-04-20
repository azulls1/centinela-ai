-- ============================================================
-- SCRIPT DE CONFIGURACIÓN COMPLETA PARA SUPABASE
-- Vision Human Insight - IAGENTEK
-- ============================================================
-- INSTRUCCIONES:
-- 1. Abre el SQL Editor en tu proyecto Supabase
-- 2. Copia y pega este script completo
-- 3. Ejecuta el script (botón Run o Execute)
-- ============================================================

-- ============================================================
-- 0. EXTENSIONES REQUERIDAS
-- ============================================================
-- gen_random_uuid requiere la extensión pgcrypto
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================================
-- 1. TABLA PRINCIPAL: vishum_events
-- ============================================================
-- Almacena todos los eventos detectados por el sistema
-- NOTA: Usamos nombre directo con prefijo vishum_ (sin sinónimos)

CREATE TABLE IF NOT EXISTS vishum_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(), -- ID único del evento
    user_id TEXT NOT NULL DEFAULT 'anonymous', -- ID del usuario (puede ser 'anonymous' o UUID de auth)
    event_type TEXT NOT NULL, -- Tipo de evento (person_detected, emotion_detected, etc.)
    camera_id TEXT NOT NULL DEFAULT 'default_camera', -- Identificador de la cámara que generó el evento
    payload JSONB NOT NULL DEFAULT '{}', -- Payload con datos del evento (JSON)
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW() -- Timestamp de creación
);

-- ============================================================
-- 2. ÍNDICES PARA MEJORAR RENDIMIENTO
-- ============================================================

-- Índice por usuario (para filtrar eventos por usuario)
CREATE INDEX IF NOT EXISTS idx_vishum_events_user_id ON vishum_events(user_id);

-- Índice por tipo de evento (para agrupar y filtrar)
CREATE INDEX IF NOT EXISTS idx_vishum_events_event_type ON vishum_events(event_type);

-- Índice por cámara
CREATE INDEX IF NOT EXISTS idx_vishum_events_camera_id ON vishum_events(camera_id);

-- Índice por fecha (para ordenar y filtrar por tiempo)
CREATE INDEX IF NOT EXISTS idx_vishum_events_created_at ON vishum_events(created_at DESC);

-- Índice GIN para búsquedas en JSONB (payload)
CREATE INDEX IF NOT EXISTS idx_vishum_events_payload ON vishum_events USING GIN(payload);

-- ============================================================
-- 1.1 TABLA: vishum_external_cameras
-- ============================================================
CREATE TABLE IF NOT EXISTS vishum_external_cameras (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL DEFAULT 'anonymous',
    name TEXT NOT NULL,
    source_url TEXT NOT NULL,
    auth_username TEXT,
    auth_password TEXT,
    stream_id TEXT,
    hls_url TEXT,
    status TEXT NOT NULL DEFAULT 'stopped',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_vishum_external_cameras_user_id ON vishum_external_cameras(user_id);
CREATE INDEX IF NOT EXISTS idx_vishum_external_cameras_status ON vishum_external_cameras(status);

-- ============================================================
-- 1.2 TABLA: vishum_sessions
-- ============================================================
-- Registra las sesiones activas de usuarios utilizando la demo
CREATE TABLE IF NOT EXISTS vishum_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id TEXT NOT NULL UNIQUE,
    name TEXT,
    email TEXT,
    plan TEXT,
    ip_address TEXT,
    user_agent TEXT,
    referer TEXT,
    cameras_active INTEGER DEFAULT 0,
    fps_average NUMERIC,
    tokens_used BIGINT DEFAULT 0,
    status TEXT NOT NULL DEFAULT 'active',
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    admin_note TEXT,
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_ping_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_vishum_sessions_session_id ON vishum_sessions(session_id);
CREATE INDEX IF NOT EXISTS idx_vishum_sessions_status ON vishum_sessions(status);
CREATE INDEX IF NOT EXISTS idx_vishum_sessions_last_ping ON vishum_sessions(last_ping_at DESC);
CREATE INDEX IF NOT EXISTS idx_vishum_sessions_email ON vishum_sessions(email);

-- ============================================================
-- 1.3 TABLA: vishum_session_events
-- ============================================================
-- Historial de acciones o eventos asociados a una sesión
CREATE TABLE IF NOT EXISTS vishum_session_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id TEXT NOT NULL,
    event_type TEXT NOT NULL,
    payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_vishum_session_events_session_id ON vishum_session_events(session_id);
CREATE INDEX IF NOT EXISTS idx_vishum_session_events_created_at ON vishum_session_events(created_at DESC);

-- ============================================================
-- 3. ROW LEVEL SECURITY (RLS)
-- ============================================================
-- Habilitar RLS en la tabla
ALTER TABLE vishum_events ENABLE ROW LEVEL SECURITY;

-- Política: Usuarios autenticados pueden ver sus propios eventos
-- y eventos anónimos (para compatibilidad)
CREATE POLICY "Users can view own events"
    ON vishum_events
    FOR SELECT
    USING (
        auth.uid()::text = user_id 
        OR user_id = 'anonymous'
    );

-- Política: Usuarios pueden insertar eventos (incluyendo anónimos)
-- IMPORTANTE: Esta política permite inserciones anónimas para desarrollo
CREATE POLICY "Users can insert events"
    ON vishum_events
    FOR INSERT
    WITH CHECK (
        auth.uid()::text = user_id 
        OR user_id = 'anonymous'
        OR auth.uid() IS NULL  -- Permitir cuando no hay usuario autenticado
    );

-- Política: Usuarios pueden eliminar sus propios eventos
CREATE POLICY "Users can delete own events"
    ON vishum_events
    FOR DELETE
    USING (
        auth.uid()::text = user_id
    );

-- NOTA: La service_role_key del backend bypassa RLS automáticamente
-- No necesitas una política específica para service_role

-- RLS para cámaras externas
ALTER TABLE vishum_external_cameras ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own external cameras"
    ON vishum_external_cameras
    FOR SELECT
    USING (
        auth.uid()::text = user_id
        OR user_id = 'anonymous'
    );

CREATE POLICY "Users can insert external cameras"
    ON vishum_external_cameras
    FOR INSERT
    WITH CHECK (
        auth.uid()::text = user_id
        OR user_id = 'anonymous'
        OR auth.uid() IS NULL
    );

CREATE POLICY "Users can update own external cameras"
    ON vishum_external_cameras
    FOR UPDATE
    USING (auth.uid()::text = user_id);

CREATE POLICY "Users can delete own external cameras"
    ON vishum_external_cameras
    FOR DELETE
    USING (auth.uid()::text = user_id);

-- RLS para sesiones - por ahora solo accesibles vía service role
ALTER TABLE vishum_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE vishum_session_events ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Service role manages sessions"
    ON vishum_sessions
    FOR ALL
    USING (auth.role() = 'service_role')
    WITH CHECK (auth.role() = 'service_role');

CREATE POLICY "Service role manages session events"
    ON vishum_session_events
    FOR ALL
    USING (auth.role() = 'service_role')
    WITH CHECK (auth.role() = 'service_role');

-- ============================================================
-- 4. FUNCIONES ÚTILES
-- ============================================================

-- Función para obtener estadísticas de eventos
CREATE OR REPLACE FUNCTION get_event_stats(
    p_hours INTEGER DEFAULT 24,
    p_user_id TEXT DEFAULT NULL
)
RETURNS TABLE (
    total BIGINT,
    by_type JSONB,
    by_camera JSONB
) 
LANGUAGE plpgsql
AS $$
DECLARE
    type_json JSONB;
    camera_json JSONB;
BEGIN
    WITH filtered AS (
        SELECT
            event_type,
            COALESCE(camera_id, 'default_camera') AS cam
        FROM vishum_events
        WHERE created_at >= NOW() - (p_hours || ' hours')::INTERVAL
            AND (p_user_id IS NULL OR user_id = p_user_id)
    ),
    type_counts AS (
        SELECT event_type, COUNT(*)::INTEGER AS count
        FROM filtered
        GROUP BY event_type
    ),
    camera_counts AS (
        SELECT cam AS camera_id, COUNT(*)::INTEGER AS count
        FROM filtered
        GROUP BY cam
    )
    SELECT COALESCE(jsonb_object_agg(event_type, count), '{}'::jsonb)
    INTO type_json
    FROM type_counts;

    SELECT COALESCE(jsonb_object_agg(camera_id, count), '{}'::jsonb)
    INTO camera_json
    FROM camera_counts;

    RETURN QUERY
    SELECT
        (SELECT COUNT(*)::BIGINT FROM filtered),
        COALESCE(type_json, '{}'::jsonb),
        COALESCE(camera_json, '{}'::jsonb);
END;
$$;

-- Función para obtener eventos recientes con paginación
CREATE OR REPLACE FUNCTION get_recent_events(
    p_limit INTEGER DEFAULT 50,
    p_offset INTEGER DEFAULT 0,
    p_event_type TEXT DEFAULT NULL,
    p_user_id TEXT DEFAULT NULL
)
RETURNS TABLE (
    id UUID,
    user_id TEXT,
    event_type TEXT,
    camera_id TEXT,
    payload JSONB,
    created_at TIMESTAMPTZ
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        e.id,
        e.user_id,
        e.event_type,
        COALESCE(e.camera_id, 'default_camera') AS camera_id,
        e.payload,
        e.created_at
    FROM vishum_events e
    WHERE (p_event_type IS NULL OR e.event_type = p_event_type)
        AND (p_user_id IS NULL OR e.user_id = p_user_id)
    ORDER BY e.created_at DESC
    LIMIT p_limit
    OFFSET p_offset;
END;
$$;

-- ============================================================
-- 5. VISTA MATERIALIZADA PARA RENDIMIENTO (OPCIONAL)
-- ============================================================
-- Útil si hay muchos eventos y necesitas estadísticas rápidas
-- NOTA: Usamos nombre directo con prefijo vishum_

CREATE MATERIALIZED VIEW IF NOT EXISTS vishum_recent_events AS
SELECT
    id,
    user_id,
    event_type,
    camera_id,
    payload,
    created_at
FROM vishum_events
WHERE created_at >= NOW() - INTERVAL '24 hours'
ORDER BY created_at DESC;

-- Índice para la vista materializada
CREATE INDEX IF NOT EXISTS idx_vishum_recent_events_created_at 
    ON vishum_recent_events(created_at DESC);

-- Índice único requerido para REFRESH CONCURRENTLY
CREATE UNIQUE INDEX IF NOT EXISTS idx_vishum_recent_events_id
    ON vishum_recent_events(id);

-- Función para refrescar la vista materializada
CREATE OR REPLACE FUNCTION refresh_vishum_recent_events()
RETURNS void 
LANGUAGE plpgsql
AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY vishum_recent_events;
END;
$$;

-- ============================================================
-- 6. COMENTARIOS DE DOCUMENTACIÓN
-- ============================================================

COMMENT ON TABLE vishum_events IS 'Tabla principal de eventos detectados por el sistema de visión por computadora';
COMMENT ON COLUMN vishum_events.id IS 'UUID único del evento';
COMMENT ON COLUMN vishum_events.user_id IS 'ID del usuario (anonymous si no está autenticado)';
COMMENT ON COLUMN vishum_events.event_type IS 'Tipo de evento: person_detected, emotion_detected, movement_detected, etc.';
COMMENT ON COLUMN vishum_events.camera_id IS 'Identificador de la cámara que generó el evento';
COMMENT ON COLUMN vishum_events.payload IS 'Datos del evento en formato JSON (confianza, bounding boxes, emociones, etc.)';
COMMENT ON COLUMN vishum_events.created_at IS 'Timestamp de creación del evento';
COMMENT ON TABLE vishum_external_cameras IS 'Registro de cámaras IP/RTSP externas configuradas por el usuario';
COMMENT ON TABLE vishum_sessions IS 'Sesiones activas/recientes de usuarios que utilizan la demo en vivo';
COMMENT ON COLUMN vishum_sessions.session_id IS 'Identificador único proporcionado por el frontend';
COMMENT ON COLUMN vishum_sessions.status IS 'Estado actual de la sesión: active, limit, banned, terminated, etc.';
COMMENT ON TABLE vishum_session_events IS 'Historial de eventos y acciones sobre las sesiones (heartbeats, acciones admin, etc.)';

-- ============================================================
-- 7. CONFIGURACIÓN DE STORAGE (OPCIONAL)
-- ============================================================
-- NOTA: La configuración completa de Storage está en: infra/supabase/storage_setup.sql
-- 
-- Para habilitar almacenamiento de imágenes:
-- 1. Crea el bucket "vishum-images" desde el Dashboard de Supabase
-- 2. Ejecuta el script: infra/supabase/storage_setup.sql
--
-- Las políticas RLS para storage.objects se configuran en storage_setup.sql

-- ============================================================
-- 8. NOTA: SINÓNIMOS NO NECESARIOS
-- ============================================================
-- Las tablas ya se crearon con nombres vishum_* directamente
-- No necesitamos vistas/sinónimos adicionales (eso era redundante)
-- ============================================================

-- ============================================================
-- 9. DATOS DE PRUEBA (OPCIONAL - COMENTAR SI NO SE DESEAN)
-- ============================================================

-- INSERT INTO vishum_events (event_type, payload, user_id) VALUES
-- ('person_detected', '{"confidence": 0.85, "persons": 1}', 'anonymous'),
-- ('emotion_detected', '{"emotion": "happy", "confidence": 0.72}', 'anonymous'),
-- ('movement_detected', '{"activity": "active", "confidence": 0.68}', 'anonymous'),
-- ('object_detected', '{"objects": [{"label": "laptop", "confidence": 0.92}]}', 'anonymous');

-- ============================================================
-- SCRIPT COMPLETADO
-- ============================================================
-- Verifica que todas las tablas, índices y políticas se crearon correctamente
-- Puedes verificar ejecutando:
-- SELECT * FROM vishum_events LIMIT 1;
-- SELECT * FROM vishum_recent_events LIMIT 1;
-- 
-- NOTA: Las tablas se crean directamente con prefijo vishum_
-- NO se crean tablas sin prefijo ni vistas sinónimos redundantes
-- ============================================================

