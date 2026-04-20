import { memo, useMemo, useEffect, useRef, useState } from 'react'
import { useAppStore } from '../store/appStore'
import { Activity, Smile, Heart, AlertCircle, Video, AlertTriangle, CheckCircle2 } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'

/**
 * Panel lateral moderno con animaciones - ESTILO 2025
 */
function DetectionPanelComponent() {
  const detectionState = useAppStore((state) => state.detectionState)
  const aggregated = useAppStore((state) => state.aggregatedDetections)
  const activeCameraIds = useAppStore((state) => state.activeCameraIds)
  const cameraConfigs = useAppStore((state) => state.cameraConfigs)
  const cameraDetections = useAppStore((state) => state.cameraDetections)
  const cameraRuntime = useAppStore((state) => state.cameraRuntime)
  const config = useAppStore((state) => state.config)

  const objectsCount = useMemo(() => aggregated.totalObjects, [aggregated.totalObjects])
  const emotionsCount = useMemo(() => detectionState.detections.emotions.length, [detectionState.detections.emotions.length])
  const fps = useMemo(() => detectionState.currentFPS.toFixed(1), [detectionState.currentFPS])

  const [processingDisplay, setProcessingDisplay] = useState<'scanning' | 'ready'>('ready')
  const processingTimeoutRef = useRef<number | undefined>(undefined)

  useEffect(() => {
    if (detectionState.isProcessing) {
      if (processingTimeoutRef.current !== undefined) {
        window.clearTimeout(processingTimeoutRef.current)
        processingTimeoutRef.current = undefined
      }
      setProcessingDisplay('scanning')
    } else {
      if (processingDisplay !== 'ready') {
        processingTimeoutRef.current = window.setTimeout(() => {
          setProcessingDisplay('ready')
          processingTimeoutRef.current = undefined
        }, 900)
      }
    }

    return () => {
      if (processingTimeoutRef.current !== undefined) {
        window.clearTimeout(processingTimeoutRef.current)
        processingTimeoutRef.current = undefined
      }
    }
  }, [detectionState.isProcessing, processingDisplay])

  const statusLabel = processingDisplay === 'scanning' ? 'Procesando…' : 'Activo'
  const camerasOnline = useMemo(
    () =>
      activeCameraIds.map((cameraId) => {
        const config = cameraConfigs[cameraId]
        const detection = cameraDetections[cameraId]
        const runtime = cameraRuntime[cameraId]
        const persons = detection?.detections.persons ?? 0
        const faces = detection?.detections.faces ?? 0
        const objects = detection?.detections.objects.length ?? 0
        const fps = detection?.currentFPS ?? 0
        const isStreaming = runtime?.isStreaming ?? false
        const isVideoReady = runtime?.isVideoReady ?? false
        const isHealthy = isStreaming && isVideoReady && fps >= 18
        const hasWarning = isStreaming && (!isVideoReady || fps < 18)

        let status: 'offline' | 'warning' | 'ok' = 'offline'
        if (isHealthy) status = 'ok'
        else if (hasWarning) status = 'warning'

        return {
          id: cameraId,
          label: config?.label ?? 'Cámara sin nombre',
          location: config?.location,
          persons,
          faces,
          objects,
          fps: fps.toFixed(0),
          status,
          isStreaming,
          isVideoReady,
          models: config?.models,
        }
      }),
    [activeCameraIds, cameraConfigs, cameraDetections, cameraRuntime],
  )

  const cardVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 },
    exit: { opacity: 0, y: -20 }
  }

  return (
    <div className="neo-stack">
      <motion.div
        variants={cardVariants}
        initial="hidden"
        animate="visible"
        className="card"
      >
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <Video className="text-pine" size={20} />
              <h6 className="mb-0 text-forest font-semibold">Resumen de Cámaras</h6>
            </div>
            <span className="badge badge-inactive">
              {aggregated.camerasActive}/{activeCameraIds.length > 0 ? activeCameraIds.length : 0}
            </span>
          </div>
          <div className="flex flex-col gap-2 text-moss text-sm">
            <div className="flex justify-between">
              <span>Cámaras Procesando:</span>
              <span className="text-forest font-semibold">{aggregated.camerasProcessing}</span>
            </div>
            <div className="flex justify-between">
              <span>Personas Totales:</span>
              <span className="text-forest font-semibold">{aggregated.totalPersons}</span>
            </div>
            <div className="flex justify-between">
              <span>Rostros Totales:</span>
              <span className="text-forest font-semibold">{aggregated.totalFaces}</span>
            </div>
            <div className="flex justify-between">
              <span>Objetos Totales:</span>
              <span className="text-forest font-semibold">{aggregated.totalObjects}</span>
            </div>
          </div>
      </motion.div>

      {camerasOnline.length > 0 && (
        <motion.div
          variants={cardVariants}
          initial="hidden"
          animate="visible"
          transition={{ delay: 0.05 }}
          className="card"
        >
            <div className="flex items-center gap-2 mb-3">
              <AlertCircle className="text-amber-600" size={20} />
              <h6 className="mb-0 text-forest font-semibold">Estado por Cámara</h6>
            </div>
            <div className="flex flex-col gap-2">
              {camerasOnline.map((camera) => (
                <div
                  key={camera.id}
                  className="p-2 rounded-lg bg-gray-50 border border-gray-100"
                >
                  <div className="flex justify-between items-center mb-2">
                    <div>
                      <div className="text-forest font-semibold">{camera.label}</div>
                      {camera.location && (
                        <div className="text-moss text-sm">{camera.location}</div>
                      )}
                    </div>
                    <div>
                      {camera.status === 'ok' && (
                        <span className="badge badge-active flex items-center gap-1">
                          <CheckCircle2 size={14} /> OK
                        </span>
                      )}
                      {camera.status === 'warning' && (
                        <span className="badge badge-warning flex items-center gap-1">
                          <AlertTriangle size={14} /> Atención
                        </span>
                      )}
                      {camera.status === 'offline' && (
                        <span className="badge badge-error flex items-center gap-1">
                          <AlertTriangle size={14} /> Sin señal
                        </span>
                      )}
                    </div>
                  </div>
                  <div className="flex flex-wrap gap-2 text-moss text-sm">
                    <span>FPS: <span className="text-forest font-semibold">{camera.fps}</span></span>
                    <span>Personas: <span className="text-forest font-semibold">{camera.persons}</span></span>
                    <span>Rostros: <span className="text-forest font-semibold">{camera.faces}</span></span>
                    <span>Objetos: <span className="text-forest font-semibold">{camera.objects}</span></span>
                  </div>
                </div>
              ))}
            </div>
        </motion.div>
      )}

      {/* Emociones */}
      <motion.div
        variants={cardVariants}
        initial="hidden"
        animate="visible"
        className="card"
      >
          <div className="flex items-center gap-2 mb-3">
            <Smile className="text-forest" size={20} />
            <h6 className="mb-0 text-forest font-semibold">Emociones Detectadas</h6>
        </div>
          <AnimatePresence mode="wait">
        {emotionsCount > 0 ? (
              <motion.div
                key="emotions-list"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="flex flex-col gap-2"
              >
            {detectionState.detections.emotions.map((emotion, idx) => {
              const emotionColors: Record<string, string> = {
                    happy: 'bg-emerald-50 border border-emerald-200 text-emerald-700',
                    sad: 'bg-blue-50 border border-blue-200 text-blue-700',
                    angry: 'bg-red-50 border border-red-200 text-red-700',
                    surprised: 'bg-amber-50 border border-amber-200 text-amber-700',
                    focused: 'bg-violet-50 border border-violet-200 text-violet-700',
                    neutral: 'bg-gray-50 border border-gray-200 text-gray-600',
              }
              const colorClass = emotionColors[emotion] || emotionColors.neutral

              return (
                    <motion.div
                      key={`${emotion}-${idx}`}
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: idx * 0.1 }}
                      className={`badge ${colorClass} p-2 capitalize`}
                >
                  {emotion}
                    </motion.div>
              )
            })}
              </motion.div>
        ) : (
              <motion.p
                key="no-emotions"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="text-moss text-sm mb-0"
              >
                No se detectaron emociones
              </motion.p>
        )}
          </AnimatePresence>
      </motion.div>

      {/* Actividad */}
      <motion.div
        variants={cardVariants}
        initial="hidden"
        animate="visible"
        transition={{ delay: 0.1 }}
        className="card"
      >
          <div className="flex items-center gap-2 mb-3">
            <Activity className="text-emerald-600" size={20} />
            <h6 className="mb-0 text-forest font-semibold">Actividad</h6>
        </div>
          <AnimatePresence mode="wait">
        {detectionState.detections.activity ? (
              <motion.div
                key="activity"
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.9 }}
                className={`badge p-2 capitalize ${
            detectionState.detections.activity === 'active'
                    ? 'bg-emerald-50 border border-emerald-200 text-emerald-700'
              : detectionState.detections.activity === 'inactive'
                    ? 'bg-amber-50 border border-amber-200 text-amber-700'
                    : 'bg-red-50 border border-red-200 text-red-700'
                }`}
              >
            {detectionState.detections.activity}
              </motion.div>
        ) : (
              <motion.p
                key="no-activity"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="text-moss text-sm mb-0"
              >
                No se detectó actividad
              </motion.p>
        )}
          </AnimatePresence>
      </motion.div>

      {/* Estado de Salud */}
      <motion.div
        variants={cardVariants}
        initial="hidden"
        animate="visible"
        transition={{ delay: 0.2 }}
        className="card"
      >
          <div className="flex items-center gap-2 mb-3">
            <Heart className="text-red-600" size={20} />
            <h6 className="mb-0 text-forest font-semibold">Estado de Salud</h6>
        </div>
          <AnimatePresence mode="wait">
        {detectionState.detections.healthStatus ? (
              <motion.div
                key="health"
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.9 }}
                className={`badge p-2 capitalize ${
            detectionState.detections.healthStatus === 'normal' || detectionState.detections.healthStatus === 'focused'
                    ? 'bg-emerald-50 border border-emerald-200 text-emerald-700'
              : detectionState.detections.healthStatus === 'tired' || detectionState.detections.healthStatus === 'stressed'
                    ? 'bg-amber-50 border border-amber-200 text-amber-700'
                    : 'bg-red-50 border border-red-200 text-red-700'
                }`}
              >
            {detectionState.detections.healthStatus}
              </motion.div>
        ) : (
              <motion.p
                key="no-health"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="text-moss text-sm mb-0"
              >
                No se pudo estimar
              </motion.p>
        )}
          </AnimatePresence>
      </motion.div>

      {/* Objetos */}
      <motion.div
        variants={cardVariants}
        initial="hidden"
        animate="visible"
        transition={{ delay: 0.3 }}
        className="card"
      >
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <AlertCircle className="text-amber-600" size={20} />
              <h6 className="mb-0 text-forest font-semibold">Objetos Detectados</h6>
            </div>
            <span className="tag-counter">{objectsCount}</span>
        </div>
          <AnimatePresence mode="wait">
        {objectsCount > 0 ? (
              <motion.div
                key="objects-list"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="flex flex-col gap-2"
                style={{ maxHeight: '200px', overflowY: 'auto' }}
              >
            {detectionState.detections.objects.map((obj, idx) => (
                  <motion.div
                    key={`${obj.label}-${idx}`}
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: idx * 0.05 }}
                    className="flex items-center justify-between p-2 rounded-lg bg-gray-50 border border-gray-100"
              >
                <div>
                      <div className="text-forest text-sm capitalize font-semibold">{obj.label}</div>
                      <div className="text-moss" style={{ fontSize: '0.7rem' }}>
                    Confianza: {Math.round(obj.confidence * 100)}%
                  </div>
                </div>
                    <div className="bg-warning rounded-circle" style={{ width: '8px', height: '8px' }}></div>
                  </motion.div>
            ))}
              </motion.div>
        ) : (
              <motion.p
                key="no-objects"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="text-moss text-sm text-center mb-0 py-3"
              >
            No se detectaron objetos aún
              </motion.p>
        )}
          </AnimatePresence>
        {config.objectDetection.enabled && (
            <div className="mt-3 pt-3 border-t border-gray-200">
              <p className="text-moss text-sm mb-0">
                YOLO puede detectar más de 80 tipos de objetos diferentes
              </p>
          </div>
        )}
      </motion.div>

      {/* Información de procesamiento */}
      <motion.div
        variants={cardVariants}
        initial="hidden"
        animate="visible"
        transition={{ delay: 0.4 }}
        className="card"
      >
          <div className="flex flex-col gap-2 text-sm text-moss">
            <div className="flex justify-between">
              <span>FPS:</span>
              <span className="text-forest font-bold">{fps}</span>
            </div>
            <div className="flex justify-between items-center">
              <span>Estado:</span>
              <span className={`badge ${processingDisplay === 'scanning' ? 'badge-info' : 'badge-active'}`}>
                {statusLabel}
              </span>
            </div>
            <div className="flex justify-between">
              <span>Personas:</span>
              <span className="text-forest font-bold">{detectionState.detections.persons}</span>
            </div>
            <div className="flex justify-between">
              <span>Rostros:</span>
              <span className="text-forest font-bold">{detectionState.detections.faces}</span>
        </div>
      </div>
      </motion.div>
    </div>
  )
}

export const DetectionPanel = memo(DetectionPanelComponent)
