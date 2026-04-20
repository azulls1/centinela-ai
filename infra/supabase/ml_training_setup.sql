-- ============================================================
-- CONFIGURACIÓN PARA MACHINE LEARNING Y ENTRENAMIENTO
-- Vision Human Insight - IAGENTEK
-- ============================================================
-- INSTRUCCIONES:
-- 1. Ejecuta PRIMERO: setup.sql (requerido)
-- 2. Opcional: create_buckets.sql (para crear bucket de modelos)
-- 3. Luego ejecuta este script en el SQL Editor de Supabase
-- 
-- Este script crea las tablas necesarias para:
-- 1. Almacenar datasets de entrenamiento
-- 2. Guardar anotaciones de imágenes/videos
-- 3. Rastrear versiones de modelos entrenados
-- 4. Registrar métricas de entrenamiento
-- ============================================================

-- ============================================================
-- 1. TABLA: vishum_ml_datasets
-- ============================================================
-- Almacena información sobre datasets de entrenamiento
-- NOTA: Usamos nombres directos con prefijo vishum_ en lugar de sinónimos
CREATE TABLE IF NOT EXISTS vishum_ml_datasets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL UNIQUE, -- Nombre del dataset
    description TEXT, -- Descripción del dataset
    source_type TEXT NOT NULL, -- 'scraped', 'user_uploaded', 'generated', 'public'
    total_samples INTEGER DEFAULT 0, -- Número total de muestras
    categories JSONB DEFAULT '[]', -- Categorías/clases del dataset
    metadata JSONB DEFAULT '{}', -- Metadatos adicionales
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by TEXT DEFAULT 'system' -- Usuario o sistema que creó el dataset
);

COMMENT ON TABLE vishum_ml_datasets IS 'Almacena información sobre datasets de entrenamiento para ML';
COMMENT ON COLUMN vishum_ml_datasets.source_type IS 'Tipo de fuente: scraped, user_uploaded, generated, public';

-- ============================================================
-- 2. TABLA: vishum_ml_training_samples
-- ============================================================
-- Almacena muestras individuales de entrenamiento (imágenes/videos)
CREATE TABLE IF NOT EXISTS vishum_ml_training_samples (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    dataset_id UUID NOT NULL REFERENCES vishum_ml_datasets(id) ON DELETE CASCADE,
    file_path TEXT NOT NULL, -- Ruta al archivo en Storage
    file_type TEXT NOT NULL, -- 'image', 'video', 'frame'
    file_format TEXT NOT NULL, -- 'jpg', 'png', 'mp4', etc.
    storage_bucket TEXT DEFAULT 'vishum-images', -- Bucket de Supabase Storage
    width INTEGER, -- Ancho de imagen/video
    height INTEGER, -- Alto de imagen/video
    duration FLOAT, -- Duración en segundos (para video)
    labels JSONB DEFAULT '[]', -- Etiquetas/annotaciones
    metadata JSONB DEFAULT '{}', -- Metadatos adicionales
    quality_score FLOAT, -- Score de calidad (0-1)
    is_annotated BOOLEAN DEFAULT FALSE, -- Si está completamente anotado
    annotation_status TEXT DEFAULT 'pending', -- 'pending', 'in_progress', 'completed', 'reviewed'
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    annotated_at TIMESTAMPTZ,
    annotated_by TEXT -- Usuario que anotó
);

COMMENT ON TABLE vishum_ml_training_samples IS 'Almacena muestras individuales de entrenamiento';
COMMENT ON COLUMN vishum_ml_training_samples.labels IS 'Array de etiquetas con bounding boxes, clases, etc.';

-- ============================================================
-- 3. TABLA: vishum_ml_annotations
-- ============================================================
-- Almacena anotaciones detalladas de cada muestra
CREATE TABLE IF NOT EXISTS vishum_ml_annotations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sample_id UUID NOT NULL REFERENCES vishum_ml_training_samples(id) ON DELETE CASCADE,
    annotation_type TEXT NOT NULL, -- 'object', 'face', 'emotion', 'pose', 'hand', 'activity'
    label TEXT NOT NULL, -- Etiqueta de la clase
    confidence FLOAT, -- Confianza de la anotación (si es automática)
    bbox JSONB, -- Bounding box: {x, y, width, height}
    landmarks JSONB, -- Landmarks/puntos clave (para faces, poses, hands)
    attributes JSONB DEFAULT '{}', -- Atributos adicionales
    is_manual BOOLEAN DEFAULT FALSE, -- Si fue anotado manualmente
    is_verified BOOLEAN DEFAULT FALSE, -- Si fue verificado por humano
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by TEXT DEFAULT 'system' -- Usuario o sistema que creó la anotación
);

COMMENT ON TABLE vishum_ml_annotations IS 'Anotaciones detalladas de cada muestra de entrenamiento';
COMMENT ON COLUMN vishum_ml_annotations.bbox IS 'Bounding box en formato {x, y, width, height}';
COMMENT ON COLUMN vishum_ml_annotations.landmarks IS 'Landmarks en formato [[x1,y1], [x2,y2], ...]';

-- ============================================================
-- 4. TABLA: vishum_ml_models
-- ============================================================
-- Almacena información sobre modelos entrenados
CREATE TABLE IF NOT EXISTS vishum_ml_models (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL, -- Nombre del modelo
    version TEXT NOT NULL, -- Versión del modelo (ej: 'v1.0.0')
    model_type TEXT NOT NULL, -- 'yolo', 'mediapipe', 'custom', 'emotion', 'pose'
    architecture TEXT, -- Arquitectura específica (ej: 'YOLOv8n', 'ResNet50')
    base_model TEXT, -- Modelo base usado para fine-tuning
    dataset_ids UUID[], -- IDs de datasets usados para entrenar
    training_config JSONB DEFAULT '{}', -- Configuración de entrenamiento
    metrics JSONB DEFAULT '{}', -- Métricas de evaluación (accuracy, mAP, etc.)
    model_path TEXT, -- Ruta al modelo en Storage o externo
    storage_bucket TEXT DEFAULT 'vishum-models', -- Bucket donde está almacenado
    file_size BIGINT, -- Tamaño del archivo del modelo en bytes
    is_active BOOLEAN DEFAULT FALSE, -- Si es el modelo activo en producción
    is_public BOOLEAN DEFAULT FALSE, -- Si es público/descargable
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by TEXT DEFAULT 'system',
    notes TEXT -- Notas sobre el modelo
);

COMMENT ON TABLE vishum_ml_models IS 'Almacena información sobre modelos de ML entrenados';
COMMENT ON COLUMN vishum_ml_models.metrics IS 'Métricas: {accuracy, precision, recall, mAP, f1_score, etc.}';

-- ============================================================
-- 5. TABLA: vishum_ml_training_runs
-- ============================================================
-- Registra ejecuciones de entrenamiento
CREATE TABLE IF NOT EXISTS vishum_ml_training_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    model_id UUID REFERENCES vishum_ml_models(id) ON DELETE SET NULL,
    dataset_id UUID NOT NULL REFERENCES vishum_ml_datasets(id),
    status TEXT NOT NULL DEFAULT 'pending', -- 'pending', 'running', 'completed', 'failed'
    training_config JSONB DEFAULT '{}', -- Configuración específica de este entrenamiento
    start_time TIMESTAMPTZ,
    end_time TIMESTAMPTZ,
    duration_seconds INTEGER, -- Duración en segundos
    epochs INTEGER, -- Número de épocas
    batch_size INTEGER, -- Tamaño de batch
    learning_rate FLOAT, -- Learning rate
    loss_history JSONB DEFAULT '[]', -- Historial de pérdida
    metrics_history JSONB DEFAULT '[]', -- Historial de métricas
    logs TEXT, -- Logs de entrenamiento
    error_message TEXT, -- Mensaje de error si falló
    hardware_info JSONB DEFAULT '{}', -- Info de hardware usado (GPU, CPU, RAM)
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by TEXT DEFAULT 'system'
);

COMMENT ON TABLE vishum_ml_training_runs IS 'Registra ejecuciones de entrenamiento de modelos';
COMMENT ON COLUMN vishum_ml_training_runs.loss_history IS 'Historial de pérdida por época';
COMMENT ON COLUMN vishum_ml_training_runs.metrics_history IS 'Historial de métricas por época';

-- ============================================================
-- 6. TABLA: vishum_ml_scraped_data
-- ============================================================
-- Almacena información sobre datos scrapeados
CREATE TABLE IF NOT EXISTS vishum_ml_scraped_data (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_url TEXT NOT NULL, -- URL de origen
    source_type TEXT NOT NULL, -- 'image', 'video', 'dataset'
    source_platform TEXT, -- 'unsplash', 'pexels', 'kaggle', 'custom', etc.
    file_path TEXT, -- Ruta al archivo descargado
    metadata JSONB DEFAULT '{}', -- Metadatos del scraping
    tags TEXT[], -- Tags extraídos
    license TEXT, -- Licencia del contenido
    is_processed BOOLEAN DEFAULT FALSE, -- Si fue procesado
    is_used_in_training BOOLEAN DEFAULT FALSE, -- Si se usó en entrenamiento
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    scraped_by TEXT DEFAULT 'system'
);

COMMENT ON TABLE vishum_ml_scraped_data IS 'Registra datos scrapeados de fuentes externas';
COMMENT ON COLUMN vishum_ml_scraped_data.license IS 'Licencia del contenido (CC0, CC-BY, etc.)';

-- ============================================================
-- 7. ÍNDICES PARA MEJORAR RENDIMIENTO
-- ============================================================

-- Índices para vishum_ml_training_samples
CREATE INDEX IF NOT EXISTS idx_samples_dataset_id ON vishum_ml_training_samples(dataset_id);
CREATE INDEX IF NOT EXISTS idx_samples_annotation_status ON vishum_ml_training_samples(annotation_status);
CREATE INDEX IF NOT EXISTS idx_samples_is_annotated ON vishum_ml_training_samples(is_annotated);
CREATE INDEX IF NOT EXISTS idx_samples_file_type ON vishum_ml_training_samples(file_type);

-- Índices para vishum_ml_annotations
CREATE INDEX IF NOT EXISTS idx_annotations_sample_id ON vishum_ml_annotations(sample_id);
CREATE INDEX IF NOT EXISTS idx_annotations_type ON vishum_ml_annotations(annotation_type);
CREATE INDEX IF NOT EXISTS idx_annotations_label ON vishum_ml_annotations(label);
CREATE INDEX IF NOT EXISTS idx_annotations_is_manual ON vishum_ml_annotations(is_manual);

-- Índices para vishum_ml_models
CREATE INDEX IF NOT EXISTS idx_models_type ON vishum_ml_models(model_type);
CREATE INDEX IF NOT EXISTS idx_models_is_active ON vishum_ml_models(is_active);
CREATE INDEX IF NOT EXISTS idx_models_version ON vishum_ml_models(version);

-- Índices para vishum_ml_training_runs
CREATE INDEX IF NOT EXISTS idx_runs_model_id ON vishum_ml_training_runs(model_id);
CREATE INDEX IF NOT EXISTS idx_runs_dataset_id ON vishum_ml_training_runs(dataset_id);
CREATE INDEX IF NOT EXISTS idx_runs_status ON vishum_ml_training_runs(status);

-- Índices para vishum_ml_scraped_data
CREATE INDEX IF NOT EXISTS idx_scraped_source_type ON vishum_ml_scraped_data(source_type);
CREATE INDEX IF NOT EXISTS idx_scraped_is_processed ON vishum_ml_scraped_data(is_processed);

-- Índices GIN para búsquedas en JSONB
CREATE INDEX IF NOT EXISTS idx_samples_labels_gin ON vishum_ml_training_samples USING GIN(labels);
CREATE INDEX IF NOT EXISTS idx_annotations_bbox_gin ON vishum_ml_annotations USING GIN(bbox);
CREATE INDEX IF NOT EXISTS idx_models_metrics_gin ON vishum_ml_models USING GIN(metrics);

-- ============================================================
-- 8. ROW LEVEL SECURITY (RLS)
-- ============================================================

-- Habilitar RLS en todas las tablas
ALTER TABLE vishum_ml_datasets ENABLE ROW LEVEL SECURITY;
ALTER TABLE vishum_ml_training_samples ENABLE ROW LEVEL SECURITY;
ALTER TABLE vishum_ml_annotations ENABLE ROW LEVEL SECURITY;
ALTER TABLE vishum_ml_models ENABLE ROW LEVEL SECURITY;
ALTER TABLE vishum_ml_training_runs ENABLE ROW LEVEL SECURITY;
ALTER TABLE vishum_ml_scraped_data ENABLE ROW LEVEL SECURITY;

-- Políticas para vishum_ml_datasets (lectura pública, escritura autenticada)
CREATE POLICY "Public read access for datasets"
    ON vishum_ml_datasets FOR SELECT
    USING (true);

CREATE POLICY "Authenticated users can insert datasets"
    ON vishum_ml_datasets FOR INSERT
    WITH CHECK (auth.role() = 'authenticated');

-- Políticas para vishum_ml_training_samples
CREATE POLICY "Public read access for training samples"
    ON vishum_ml_training_samples FOR SELECT
    USING (true);

CREATE POLICY "Authenticated users can insert samples"
    ON vishum_ml_training_samples FOR INSERT
    WITH CHECK (auth.role() = 'authenticated');

-- Políticas para vishum_ml_annotations
CREATE POLICY "Public read access for annotations"
    ON vishum_ml_annotations FOR SELECT
    USING (true);

CREATE POLICY "Authenticated users can insert annotations"
    ON vishum_ml_annotations FOR INSERT
    WITH CHECK (auth.role() = 'authenticated');

-- Políticas para vishum_ml_models (lectura pública, escritura autenticada)
CREATE POLICY "Public read access for models"
    ON vishum_ml_models FOR SELECT
    USING (true);

CREATE POLICY "Authenticated users can insert models"
    ON vishum_ml_models FOR INSERT
    WITH CHECK (auth.role() = 'authenticated');

-- Políticas para vishum_ml_training_runs
CREATE POLICY "Public read access for training runs"
    ON vishum_ml_training_runs FOR SELECT
    USING (true);

CREATE POLICY "Authenticated users can insert training runs"
    ON vishum_ml_training_runs FOR INSERT
    WITH CHECK (auth.role() = 'authenticated');

-- Políticas para vishum_ml_scraped_data
CREATE POLICY "Public read access for scraped data"
    ON vishum_ml_scraped_data FOR SELECT
    USING (true);

CREATE POLICY "Authenticated users can insert scraped data"
    ON vishum_ml_scraped_data FOR INSERT
    WITH CHECK (auth.role() = 'authenticated');

-- ============================================================
-- 9. FUNCIONES ÚTILES
-- ============================================================

-- Función para obtener estadísticas de un dataset
CREATE OR REPLACE FUNCTION get_dataset_stats(p_dataset_id UUID)
RETURNS TABLE (
    total_samples BIGINT,
    annotated_samples BIGINT,
    pending_samples BIGINT,
    categories_count JSONB,
    avg_quality_score FLOAT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_total_samples BIGINT;
    v_annotated_samples BIGINT;
    v_pending_samples BIGINT;
    v_avg_quality_score FLOAT;
    v_categories_count JSONB;
BEGIN
    -- Obtener estadísticas de muestras
    SELECT
        COUNT(*)::BIGINT,
        COUNT(*) FILTER (WHERE is_annotated = true)::BIGINT,
        COUNT(*) FILTER (WHERE annotation_status = 'pending')::BIGINT,
        AVG(quality_score)
    INTO
        v_total_samples,
        v_annotated_samples,
        v_pending_samples,
        v_avg_quality_score
    FROM vishum_ml_training_samples
    WHERE dataset_id = p_dataset_id;
    
    -- Obtener conteo de categorías de anotaciones
    SELECT COALESCE(
        jsonb_object_agg(annotation_type, count),
        '{}'::jsonb
    )
    INTO v_categories_count
    FROM (
        SELECT
            a.annotation_type,
            COUNT(*)::INTEGER as count
        FROM vishum_ml_annotations a
        INNER JOIN vishum_ml_training_samples s ON a.sample_id = s.id
        WHERE s.dataset_id = p_dataset_id
        GROUP BY a.annotation_type
    ) subquery;
    
    -- Retornar resultado
    RETURN QUERY
    SELECT
        v_total_samples,
        v_annotated_samples,
        v_pending_samples,
        v_categories_count,
        v_avg_quality_score;
END;
$$;

-- Función para obtener el modelo activo de un tipo
CREATE OR REPLACE FUNCTION get_active_model(p_model_type TEXT)
RETURNS TABLE (
    id UUID,
    name TEXT,
    version TEXT,
    model_path TEXT,
    metrics JSONB
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        m.id,
        m.name,
        m.version,
        m.model_path,
        m.metrics
    FROM vishum_ml_models m
    WHERE m.model_type = p_model_type
        AND m.is_active = true
    ORDER BY m.created_at DESC
    LIMIT 1;
END;
$$;

-- Función para actualizar timestamp automáticamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger para actualizar updated_at en vishum_ml_datasets
CREATE TRIGGER update_vishum_ml_datasets_updated_at
    BEFORE UPDATE ON vishum_ml_datasets
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================
-- 10. NOTA: SINÓNIMOS NO NECESARIOS
-- ============================================================
-- Las tablas ya se crearon con nombres vishum_ml_* directamente
-- No necesitamos vistas/sinónimos adicionales (eso era redundante)
-- ============================================================

-- ============================================================
-- 11. COMENTARIOS DE DOCUMENTACIÓN
-- ============================================================

COMMENT ON FUNCTION get_dataset_stats IS 'Obtiene estadísticas de un dataset de entrenamiento';
COMMENT ON FUNCTION get_active_model IS 'Obtiene el modelo activo de un tipo específico';
COMMENT ON FUNCTION update_updated_at_column IS 'Actualiza automáticamente el campo updated_at';

-- ============================================================
-- SCRIPT COMPLETADO
-- ============================================================
-- Verifica que todas las tablas se crearon correctamente:
-- SELECT table_name FROM information_schema.tables 
-- WHERE table_schema = 'public' AND table_name LIKE 'vishum_ml_%';
-- 
-- NOTA: Las tablas se crean directamente con prefijo vishum_ml_
-- NO se crean tablas ml_* redundantes ni vistas sinónimos
-- ============================================================

