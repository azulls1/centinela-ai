-- ============================================================================
-- NXT Telemetry - Setup SQL para Supabase
-- ============================================================================
-- Ejecutar este SQL en la consola de PostgreSQL del servidor
-- (NO en el SQL Editor de Supabase Studio ya que requiere los roles activos)
--
-- Conexión directa al servidor:
--   psql -h localhost -U postgres -d postgres
-- ============================================================================

-- ============================================================================
-- PASO 1: Crear roles faltantes de Supabase (si no existen)
-- ============================================================================

-- Rol authenticator (requerido por PostgREST)
DO $$
BEGIN
  IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'authenticator') THEN
    CREATE ROLE authenticator NOINHERIT LOGIN;
    COMMENT ON ROLE authenticator IS 'PostgREST connection role';
  END IF;
END
$$;

-- Rol anon (requerido para acceso sin auth)
DO $$
BEGIN
  IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'anon') THEN
    CREATE ROLE anon NOLOGIN NOINHERIT;
    COMMENT ON ROLE anon IS 'Anonymous/public role';
  END IF;
END
$$;

-- Rol authenticated (requerido para acceso con auth)
DO $$
BEGIN
  IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'authenticated') THEN
    CREATE ROLE authenticated NOLOGIN NOINHERIT;
    COMMENT ON ROLE authenticated IS 'Authenticated user role';
  END IF;
END
$$;

-- Rol service_role (acceso total)
DO $$
BEGIN
  IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'service_role') THEN
    CREATE ROLE service_role NOLOGIN NOINHERIT BYPASSRLS;
    COMMENT ON ROLE service_role IS 'Service role with bypass RLS';
  END IF;
END
$$;

-- Rol supabase_admin (requerido por pg-meta)
DO $$
BEGIN
  IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'supabase_admin') THEN
    CREATE ROLE supabase_admin NOLOGIN NOINHERIT BYPASSRLS;
    COMMENT ON ROLE supabase_admin IS 'Supabase admin role for pg-meta';
  END IF;
END
$$;

-- Grants necesarios
GRANT anon TO authenticator;
GRANT authenticated TO authenticator;
GRANT service_role TO authenticator;
GRANT supabase_admin TO postgres;

-- Schema public permissions
GRANT USAGE ON SCHEMA public TO anon, authenticated, service_role;
GRANT ALL ON SCHEMA public TO supabase_admin;

-- ============================================================================
-- PASO 2: Crear tabla de telemetría
-- ============================================================================

CREATE TABLE IF NOT EXISTS public.nxt_devai_telemetry (
    id              BIGSERIAL PRIMARY KEY,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),

    -- Evento
    event_type      TEXT NOT NULL,
    event_ts        TIMESTAMPTZ NOT NULL,
    session_id      TEXT,
    fw_version      TEXT DEFAULT '3.8.0',

    -- Usuario
    user_name       TEXT NOT NULL,
    user_email      TEXT,
    user_os         TEXT,
    user_machine    TEXT,

    -- Proyecto
    project_name    TEXT,

    -- Datos del evento (flexible)
    agent           TEXT,
    phase           TEXT,
    task_scale      TEXT,
    command         TEXT,
    is_slash_command BOOLEAN DEFAULT false,
    task            TEXT,
    step            TEXT,
    total_steps     INTEGER,
    artifacts_count INTEGER,
    duration_ms     INTEGER,

    -- Metadata extra (JSON para datos no estructurados)
    extra_data      JSONB DEFAULT '{}'::jsonb
);

-- Indices para queries frecuentes
CREATE INDEX IF NOT EXISTS idx_devai_telemetry_user ON public.nxt_devai_telemetry(user_name);
CREATE INDEX IF NOT EXISTS idx_devai_telemetry_event ON public.nxt_devai_telemetry(event_type);
CREATE INDEX IF NOT EXISTS idx_devai_telemetry_created ON public.nxt_devai_telemetry(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_devai_telemetry_project ON public.nxt_devai_telemetry(project_name);
CREATE INDEX IF NOT EXISTS idx_devai_telemetry_agent ON public.nxt_devai_telemetry(agent);
CREATE INDEX IF NOT EXISTS idx_devai_telemetry_session ON public.nxt_devai_telemetry(session_id);
CREATE INDEX IF NOT EXISTS idx_devai_telemetry_slash_cmd ON public.nxt_devai_telemetry(is_slash_command);

-- ============================================================================
-- PASO 3: Row Level Security (RLS)
-- ============================================================================

ALTER TABLE public.nxt_devai_telemetry ENABLE ROW LEVEL SECURITY;

-- service_role puede todo (usado por el framework)
CREATE POLICY "service_role_all" ON public.nxt_devai_telemetry
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

-- anon puede insertar (para los hooks que usan anon key)
CREATE POLICY "anon_insert" ON public.nxt_devai_telemetry
    FOR INSERT
    TO anon
    WITH CHECK (true);

-- anon puede leer (para stats)
CREATE POLICY "anon_select" ON public.nxt_devai_telemetry
    FOR SELECT
    TO anon
    USING (true);

-- ============================================================================
-- PASO 4: Vistas de estadísticas
-- ============================================================================

-- Telemetry Stats: stats agregadas por usuario, proyecto y día
CREATE OR REPLACE VIEW public.nxt_devai_telemetry_stats AS
SELECT
    user_name,
    user_email,
    project_name,
    COUNT(*) as total_events,
    COUNT(DISTINCT session_id) as total_sessions,
    COUNT(*) FILTER (WHERE event_type = 'user_message') as total_messages,
    COUNT(*) FILTER (WHERE event_type = 'agent_activated') as total_agent_activations,
    MIN(event_ts) as first_seen,
    MAX(event_ts) as last_seen,
    DATE(event_ts) as activity_date
FROM public.nxt_devai_telemetry
GROUP BY user_name, user_email, project_name, DATE(event_ts)
ORDER BY activity_date DESC;

-- Team Overview: status per user (activo if seen in last 24h, inactivo if 1-7 days, dormido if 7+ days)
CREATE OR REPLACE VIEW public.nxt_devai_team_overview AS
SELECT
    user_name,
    user_email,
    user_machine,
    COUNT(*) as total_events,
    COUNT(DISTINCT session_id) as total_sessions,
    MAX(event_ts) as last_seen,
    MIN(event_ts) as first_seen,
    CASE
        WHEN MAX(event_ts) > now() - interval '24 hours' THEN 'activo'
        WHEN MAX(event_ts) > now() - interval '7 days' THEN 'inactivo'
        ELSE 'dormido'
    END as status
FROM public.nxt_devai_telemetry
GROUP BY user_name, user_email, user_machine
ORDER BY last_seen DESC;

-- Agent Ranking: most used agents
CREATE OR REPLACE VIEW public.nxt_devai_agent_ranking AS
SELECT
    agent,
    COUNT(*) as total_activations,
    COUNT(DISTINCT user_name) as unique_users,
    COUNT(DISTINCT project_name) as unique_projects,
    AVG(duration_ms) as avg_duration_ms,
    MAX(event_ts) as last_used
FROM public.nxt_devai_telemetry
WHERE agent IS NOT NULL AND agent != ''
GROUP BY agent
ORDER BY total_activations DESC;

-- Daily Activity: team activity per day
CREATE OR REPLACE VIEW public.nxt_devai_daily_activity AS
SELECT
    DATE(event_ts) as activity_date,
    COUNT(*) as total_events,
    COUNT(DISTINCT user_name) as active_users,
    COUNT(*) FILTER (WHERE event_type = 'slash_command') as slash_commands,
    COUNT(*) FILTER (WHERE event_type = 'user_message') as messages,
    COUNT(*) FILTER (WHERE event_type = 'agent_completed') as agents_completed,
    COUNT(DISTINCT agent) FILTER (WHERE agent IS NOT NULL) as unique_agents
FROM public.nxt_devai_telemetry
GROUP BY DATE(event_ts)
ORDER BY activity_date DESC;

-- Command Ranking: most used /nxt/ commands
CREATE OR REPLACE VIEW public.nxt_devai_command_ranking AS
SELECT
    command,
    agent,
    COUNT(*) as total_uses,
    COUNT(DISTINCT user_name) as unique_users,
    MAX(event_ts) as last_used
FROM public.nxt_devai_telemetry
WHERE command IS NOT NULL AND command != ''
GROUP BY command, agent
ORDER BY total_uses DESC;

-- Project Usage: framework usage by project
CREATE OR REPLACE VIEW public.nxt_devai_project_usage AS
SELECT
    project_name,
    COUNT(*) as total_events,
    COUNT(DISTINCT user_name) as unique_users,
    COUNT(DISTINCT session_id) as total_sessions,
    COUNT(DISTINCT agent) FILTER (WHERE agent IS NOT NULL) as agents_used,
    MIN(event_ts) as first_used,
    MAX(event_ts) as last_used
FROM public.nxt_devai_telemetry
GROUP BY project_name
ORDER BY total_events DESC;

-- Grants para todas las vistas
GRANT SELECT ON public.nxt_devai_telemetry_stats TO anon, authenticated, service_role;
GRANT SELECT ON public.nxt_devai_team_overview TO anon, authenticated, service_role;
GRANT SELECT ON public.nxt_devai_agent_ranking TO anon, authenticated, service_role;
GRANT SELECT ON public.nxt_devai_daily_activity TO anon, authenticated, service_role;
GRANT SELECT ON public.nxt_devai_command_ranking TO anon, authenticated, service_role;
GRANT SELECT ON public.nxt_devai_project_usage TO anon, authenticated, service_role;

-- ============================================================================
-- PASO 5: Función RPC para stats agregadas
-- ============================================================================

CREATE OR REPLACE FUNCTION public.nxt_devai_telemetry_summary(days_back INTEGER DEFAULT 30)
RETURNS JSON
LANGUAGE sql
STABLE
AS $$
    SELECT json_build_object(
        'total_events', COUNT(*),
        'total_sessions', COUNT(DISTINCT session_id),
        'total_users', COUNT(DISTINCT user_name),
        'top_users', (
            SELECT json_agg(row_to_json(u))
            FROM (
                SELECT user_name, user_email, COUNT(*) as events
                FROM public.nxt_devai_telemetry
                WHERE created_at > now() - (days_back || ' days')::interval
                GROUP BY user_name, user_email
                ORDER BY events DESC
                LIMIT 20
            ) u
        ),
        'top_agents', (
            SELECT json_agg(row_to_json(a))
            FROM (
                SELECT agent, COUNT(*) as activations
                FROM public.nxt_devai_telemetry
                WHERE agent IS NOT NULL
                AND created_at > now() - (days_back || ' days')::interval
                GROUP BY agent
                ORDER BY activations DESC
                LIMIT 15
            ) a
        ),
        'daily_activity', (
            SELECT json_agg(row_to_json(d))
            FROM (
                SELECT DATE(event_ts) as day, COUNT(*) as events
                FROM public.nxt_devai_telemetry
                WHERE created_at > now() - (days_back || ' days')::interval
                GROUP BY DATE(event_ts)
                ORDER BY day DESC
                LIMIT 30
            ) d
        )
    )
    FROM public.nxt_devai_telemetry
    WHERE created_at > now() - (days_back || ' days')::interval;
$$;

GRANT EXECUTE ON FUNCTION public.nxt_devai_telemetry_summary TO anon, authenticated, service_role;

-- ============================================================================
-- VERIFICACIÓN
-- ============================================================================

-- Verificar que la tabla existe
SELECT 'nxt_devai_telemetry table created' AS status
WHERE EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'nxt_devai_telemetry');

-- Verificar roles
SELECT rolname, rolcanlogin FROM pg_roles
WHERE rolname IN ('authenticator', 'anon', 'authenticated', 'service_role', 'supabase_admin');
