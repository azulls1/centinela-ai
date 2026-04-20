import { useState } from 'react'
import { useAppStore } from '../store/appStore'
import { Toggle } from '../components/Toggle'
import { Slider } from '../components/Slider'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Shield,
  SlidersHorizontal,
  Zap,
  Scale,
  Sparkles,
  ChevronDown,
  RotateCcw,
} from 'lucide-react'
import type { PerformancePreset, AppConfig } from '../types'

/* ------------------------------------------------------------------ */
/*  Preset definitions (what each preset writes to the global config) */
/* ------------------------------------------------------------------ */

const PRESET_CONFIGS: Record<PerformancePreset, Partial<AppConfig>> = {
  performance: {
    personDetection: { enabled: true, threshold: 0.6, fps: 5 },
    faceDetection: { enabled: true, threshold: 0.7, fps: 5 },
    emotionDetection: { enabled: false, threshold: 0.6, fps: 5 },
    poseDetection: { enabled: false, threshold: 0.6, fps: 5 },
    handDetection: { enabled: false, threshold: 0.6, fps: 5 },
    movementDetection: { enabled: false, threshold: 0.5, fps: 5 },
    objectDetection: { enabled: false, threshold: 0.5, fps: 5 },
  },
  balanced: {
    personDetection: { enabled: true, threshold: 0.5, fps: 7 },
    faceDetection: { enabled: true, threshold: 0.6, fps: 10 },
    emotionDetection: { enabled: true, threshold: 0.6, fps: 5 },
    poseDetection: { enabled: false, threshold: 0.6, fps: 5 },
    handDetection: { enabled: false, threshold: 0.6, fps: 5 },
    movementDetection: { enabled: true, threshold: 0.45, fps: 10 },
    objectDetection: { enabled: true, threshold: 0.45, fps: 7 },
  },
  quality: {
    personDetection: { enabled: true, threshold: 0.35, fps: 15 },
    faceDetection: { enabled: true, threshold: 0.4, fps: 15 },
    emotionDetection: { enabled: true, threshold: 0.4, fps: 10 },
    poseDetection: { enabled: true, threshold: 0.4, fps: 10 },
    handDetection: { enabled: true, threshold: 0.4, fps: 10 },
    movementDetection: { enabled: true, threshold: 0.3, fps: 15 },
    objectDetection: { enabled: true, threshold: 0.3, fps: 15 },
  },
}

const PRESET_META: {
  key: PerformancePreset
  label: string
  icon: typeof Zap
  description: string
  badge?: string
}[] = [
  {
    key: 'performance',
    label: 'Rendimiento',
    icon: Zap,
    description: 'Prioriza fluidez. Ideal para equipos con pocos recursos.',
  },
  {
    key: 'balanced',
    label: 'Equilibrado',
    icon: Scale,
    description: 'Balance entre precision y rendimiento. Recomendado.',
    badge: 'Recomendado',
  },
  {
    key: 'quality',
    label: 'Calidad',
    icon: Sparkles,
    description: 'Maxima precision. Requiere equipo potente.',
  },
]

/* ------------------------------------------------------------------ */
/*  Helpers                                                            */
/* ------------------------------------------------------------------ */

function thresholdZone(value: number): { label: string; color: string } {
  if (value < 0.4) return { label: 'Muy sensible (mas falsos positivos)', color: 'text-amber-600' }
  if (value <= 0.7) return { label: 'Equilibrado', color: 'text-emerald-600' }
  return { label: 'Estricto (puede perder detecciones)', color: 'text-red-500' }
}

/* ------------------------------------------------------------------ */
/*  Component                                                          */
/* ------------------------------------------------------------------ */

export function SettingsPage() {
  const config = useAppStore((state) => state.config)
  const updateConfig = useAppStore((state) => state.updateConfig)
  const performancePreset = useAppStore((state) => state.performancePreset)
  const setPerformancePreset = useAppStore((state) => state.setPerformancePreset)

  const [activePreset, setActivePreset] = useState<PerformancePreset>(performancePreset)
  const [advancedOpen, setAdvancedOpen] = useState(false)

  const applyPreset = (preset: PerformancePreset) => {
    setActivePreset(preset)
    updateConfig(PRESET_CONFIGS[preset])
    setPerformancePreset(preset)
  }

  const resetToBalanced = () => {
    applyPreset('balanced')
    updateConfig({ anonymizeData: false, saveImages: false })
    setAdvancedOpen(false)
  }

  return (
    <div className="page-shell container-xxl py-4">
      {/* Hero */}
      <motion.section
        initial={{ opacity: 0, y: -12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="card-hero mb-4"
      >
        <div>
          <span className="badge--on-dark mb-3 inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold">
            <SlidersHorizontal size={16} />
            Laboratorio de Ajustes
          </span>
          <h1 className="card-hero__title font-display">Configuracion Inteligente</h1>
          <p className="card-hero__desc text-lg mb-0">
            Elige un perfil de rendimiento o ajusta cada modelo de forma individual.
          </p>
        </div>
        <div className="text-on-dark-muted text-sm">
          Todos los ajustes se aplican en tiempo real en tu navegador.
        </div>
      </motion.section>

      {/* ── Preset cards ───────────────────────────────────────────── */}
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.08 }}
        className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-4"
      >
        {PRESET_META.map((preset) => {
          const Icon = preset.icon
          const isActive = activePreset === preset.key
          return (
            <button
              key={preset.key}
              onClick={() => applyPreset(preset.key)}
              className={`card text-left transition-all duration-200 cursor-pointer relative ${
                isActive
                  ? 'ring-2 ring-[#04202C] border-[#04202C] shadow-lg'
                  : 'hover:shadow-md'
              }`}
            >
              {preset.badge && (
                <span className="absolute top-3 right-3 bg-[#04202C] text-white text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full">
                  {preset.badge}
                </span>
              )}
              <div className="flex items-center gap-3 mb-3">
                <div
                  className={`p-2 rounded-lg ${
                    isActive ? 'bg-[#04202C] text-white' : 'bg-gray-100 text-[#04202C]'
                  }`}
                >
                  <Icon size={22} />
                </div>
                <h3 className="text-forest font-semibold text-lg mb-0">{preset.label}</h3>
              </div>
              <p className="text-moss text-sm mb-0">{preset.description}</p>
            </button>
          )
        })}
      </motion.div>

      {/* ── Privacy & general settings ─────────────────────────────── */}
      <div className="neo-grid neo-grid--settings mb-4">
        <motion.section
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.12 }}
          className="card"
        >
          <h3 className="text-forest font-semibold mb-4 flex items-center gap-2">
            <Shield size={20} />
            Privacidad y datos
          </h3>
          <div className="neo-stack">
            <div className="flex items-start justify-between">
              <div>
                <h4 className="text-forest font-semibold mb-1">Anonimizar datos</h4>
                <p className="text-moss text-sm mb-0">Oculta tags sensibles en los eventos y resumenes.</p>
              </div>
              <Toggle
                enabled={config.anonymizeData}
                onChange={(enabled) => updateConfig({ anonymizeData: enabled })}
              />
            </div>
            <div className="flex items-start justify-between">
              <div>
                <h4 className="text-forest font-semibold mb-1">Guardar imagenes</h4>
                <p className="text-moss text-sm mb-0">
                  Almacena capturas junto con los eventos. Por defecto solo se guardan metadatos.
                </p>
              </div>
              <Toggle
                enabled={config.saveImages}
                onChange={(enabled) => updateConfig({ saveImages: enabled })}
              />
            </div>
          </div>
        </motion.section>

        <motion.aside
          initial={{ opacity: 0, x: 18 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.6, delay: 0.16 }}
          className="card bg-gray-50"
        >
          <h3 className="text-forest font-semibold mb-3 flex items-center gap-2">
            <Shield size={20} />
            Privacidad y seguridad
          </h3>
          <ul className="text-moss text-sm mb-0 pl-3">
            <li>Procesamiento 100 % local en el navegador.</li>
            <li>No se almacenan imagenes por defecto; solo metadatos.</li>
            <li>Puedes habilitar anonimizacion de eventos en un clic.</li>
            <li>Revisa el footer para politicas y lineamientos de sensibilidad.</li>
          </ul>
        </motion.aside>
      </div>

      {/* ── Advanced settings (collapsed) ──────────────────────────── */}
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.2 }}
        className="card mb-4"
      >
        <button
          type="button"
          onClick={() => setAdvancedOpen((prev) => !prev)}
          className="w-full flex items-center justify-between text-left"
        >
          <h3 className="text-forest font-semibold mb-0 flex items-center gap-2">
            <SlidersHorizontal size={20} />
            Configuracion avanzada
          </h3>
          <motion.span
            animate={{ rotate: advancedOpen ? 180 : 0 }}
            transition={{ duration: 0.25 }}
          >
            <ChevronDown size={20} className="text-moss" />
          </motion.span>
        </button>

        <AnimatePresence initial={false}>
          {advancedOpen && (
            <motion.div
              key="advanced-content"
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              transition={{ duration: 0.35, ease: 'easeInOut' }}
              className="overflow-hidden"
            >
              <div className="neo-stack mt-4">
                {/* ── Person detection ── */}
                <section className="card bg-gray-50">
                  <div className="flex items-start justify-between mb-3">
                    <div>
                      <h4 className="text-forest font-semibold mb-1">Deteccion de Personas</h4>
                      <p className="text-moss text-sm mb-0">YOLO basado en COCO-SSD optimizado para WebGL.</p>
                    </div>
                    <Toggle
                      enabled={config.personDetection.enabled}
                      onChange={(enabled) =>
                        updateConfig({ personDetection: { ...config.personDetection, enabled } })
                      }
                    />
                  </div>
                  {config.personDetection.enabled && (
                    <div className="neo-stack">
                      <div>
                        <Slider
                          label="Umbral de confianza"
                          value={config.personDetection.threshold}
                          onChange={(value) =>
                            updateConfig({ personDetection: { ...config.personDetection, threshold: value } })
                          }
                          min={0}
                          max={1}
                          step={0.1}
                        />
                        <p className="text-xs text-moss mt-1 mb-0">
                          Que tan seguro debe estar el modelo para reportar una persona.{' '}
                          <span className={thresholdZone(config.personDetection.threshold).color}>
                            {thresholdZone(config.personDetection.threshold).label}
                          </span>
                        </p>
                      </div>
                      <Slider
                        label="Frecuencia (FPS)"
                        value={config.personDetection.fps}
                        onChange={(value) =>
                          updateConfig({ personDetection: { ...config.personDetection, fps: value } })
                        }
                        min={1}
                        max={30}
                        step={1}
                      />
                    </div>
                  )}
                </section>

                {/* ── Face detection ── */}
                <section className="card">
                  <div className="flex items-start justify-between mb-3">
                    <div>
                      <h4 className="text-forest font-semibold mb-1">Deteccion de Rostros</h4>
                      <p className="text-moss text-sm mb-0">MediaPipe Face Landmarker con procesamiento optimizado.</p>
                    </div>
                    <Toggle
                      enabled={config.faceDetection.enabled}
                      onChange={(enabled) =>
                        updateConfig({ faceDetection: { ...config.faceDetection, enabled } })
                      }
                    />
                  </div>
                  {config.faceDetection.enabled && (
                    <div className="neo-stack">
                      <div>
                        <Slider
                          label="Umbral de confianza"
                          value={config.faceDetection.threshold}
                          onChange={(value) =>
                            updateConfig({ faceDetection: { ...config.faceDetection, threshold: value } })
                          }
                          min={0}
                          max={1}
                          step={0.1}
                        />
                        <p className="text-xs text-moss mt-1 mb-0">
                          Sensibilidad de deteccion de rostros.{' '}
                          <span className={thresholdZone(config.faceDetection.threshold).color}>
                            {thresholdZone(config.faceDetection.threshold).label}
                          </span>
                        </p>
                      </div>
                      <Slider
                        label="Frecuencia (FPS)"
                        value={config.faceDetection.fps}
                        onChange={(value) =>
                          updateConfig({ faceDetection: { ...config.faceDetection, fps: value } })
                        }
                        min={1}
                        max={30}
                        step={1}
                      />
                    </div>
                  )}
                </section>

                {/* ── Emotion detection ── */}
                <section className="card">
                  <div className="flex items-start justify-between mb-3">
                    <div>
                      <h4 className="text-forest font-semibold mb-1">Clasificacion de Emociones</h4>
                      <p className="text-moss text-sm mb-0">Clasificador TensorFlow.js sobre landmarks faciales.</p>
                    </div>
                    <Toggle
                      enabled={config.emotionDetection.enabled}
                      onChange={(enabled) =>
                        updateConfig({ emotionDetection: { ...config.emotionDetection, enabled } })
                      }
                    />
                  </div>
                  {config.emotionDetection.enabled && (
                    <div>
                      <Slider
                        label="Umbral de confianza"
                        value={config.emotionDetection.threshold}
                        onChange={(value) =>
                          updateConfig({ emotionDetection: { ...config.emotionDetection, threshold: value } })
                        }
                        min={0}
                        max={1}
                        step={0.1}
                      />
                      <p className="text-xs text-moss mt-1 mb-0">
                        Sensibilidad de deteccion de emociones.{' '}
                        <span className={thresholdZone(config.emotionDetection.threshold).color}>
                          {thresholdZone(config.emotionDetection.threshold).label}
                        </span>
                      </p>
                    </div>
                  )}
                </section>

                {/* ── Pose detection ── */}
                <section className="card">
                  <div className="flex items-start justify-between mb-3">
                    <div>
                      <h4 className="text-forest font-semibold mb-1">Deteccion de Pose</h4>
                      <p className="text-moss text-sm mb-0">MediaPipe Pose Landmarker para postura corporal.</p>
                    </div>
                    <Toggle
                      enabled={config.poseDetection.enabled}
                      onChange={(enabled) =>
                        updateConfig({ poseDetection: { ...config.poseDetection, enabled } })
                      }
                    />
                  </div>
                  {config.poseDetection.enabled && (
                    <div>
                      <Slider
                        label="Umbral de confianza"
                        value={config.poseDetection.threshold}
                        onChange={(value) =>
                          updateConfig({ poseDetection: { ...config.poseDetection, threshold: value } })
                        }
                        min={0}
                        max={1}
                        step={0.1}
                      />
                      <p className="text-xs text-moss mt-1 mb-0">
                        Sensibilidad de deteccion de postura.{' '}
                        <span className={thresholdZone(config.poseDetection.threshold).color}>
                          {thresholdZone(config.poseDetection.threshold).label}
                        </span>
                      </p>
                    </div>
                  )}
                </section>

                {/* ── Hand detection ── */}
                <section className="card">
                  <div className="flex items-start justify-between mb-3">
                    <div>
                      <h4 className="text-forest font-semibold mb-1">Deteccion de Manos</h4>
                      <p className="text-moss text-sm mb-0">MediaPipe Hand Landmarker para gestos.</p>
                    </div>
                    <Toggle
                      enabled={config.handDetection.enabled}
                      onChange={(enabled) =>
                        updateConfig({ handDetection: { ...config.handDetection, enabled } })
                      }
                    />
                  </div>
                  {config.handDetection.enabled && (
                    <div>
                      <Slider
                        label="Umbral de confianza"
                        value={config.handDetection.threshold}
                        onChange={(value) =>
                          updateConfig({ handDetection: { ...config.handDetection, threshold: value } })
                        }
                        min={0}
                        max={1}
                        step={0.1}
                      />
                      <p className="text-xs text-moss mt-1 mb-0">
                        Sensibilidad de deteccion de manos.{' '}
                        <span className={thresholdZone(config.handDetection.threshold).color}>
                          {thresholdZone(config.handDetection.threshold).label}
                        </span>
                      </p>
                    </div>
                  )}
                </section>

                {/* ── Movement detection ── */}
                <section className="card">
                  <div className="flex items-start justify-between mb-3">
                    <div>
                      <h4 className="text-forest font-semibold mb-1">Deteccion de Movimiento</h4>
                      <p className="text-moss text-sm mb-0">Analisis por diferencias de frame con OpenCV.js.</p>
                    </div>
                    <Toggle
                      enabled={config.movementDetection.enabled}
                      onChange={(enabled) =>
                        updateConfig({ movementDetection: { ...config.movementDetection, enabled } })
                      }
                    />
                  </div>
                  {config.movementDetection.enabled && (
                    <div>
                      <Slider
                        label="Umbral de movimiento"
                        value={config.movementDetection.threshold}
                        onChange={(value) =>
                          updateConfig({ movementDetection: { ...config.movementDetection, threshold: value } })
                        }
                        min={0}
                        max={1}
                        step={0.1}
                      />
                      <p className="text-xs text-moss mt-1 mb-0">
                        Sensibilidad de deteccion de movimiento.{' '}
                        <span className={thresholdZone(config.movementDetection.threshold).color}>
                          {thresholdZone(config.movementDetection.threshold).label}
                        </span>
                      </p>
                    </div>
                  )}
                </section>

                {/* ── Object detection ── */}
                <section className="card">
                  <div className="flex items-start justify-between mb-3">
                    <div>
                      <h4 className="text-forest font-semibold mb-1">Deteccion de Objetos</h4>
                      <p className="text-moss text-sm mb-0">
                        COCO-SSD identifica mas de 80 categorias (personas, dispositivos, muebles, etc.).
                      </p>
                    </div>
                    <Toggle
                      enabled={config.objectDetection.enabled}
                      onChange={(enabled) =>
                        updateConfig({ objectDetection: { ...config.objectDetection, enabled } })
                      }
                    />
                  </div>
                  {config.objectDetection.enabled && (
                    <div className="neo-stack">
                      <div>
                        <Slider
                          label="Umbral de confianza"
                          value={config.objectDetection.threshold}
                          onChange={(value) =>
                            updateConfig({ objectDetection: { ...config.objectDetection, threshold: value } })
                          }
                          min={0}
                          max={1}
                          step={0.1}
                        />
                        <p className="text-xs text-moss mt-1 mb-0">
                          Sensibilidad de deteccion de objetos.{' '}
                          <span className={thresholdZone(config.objectDetection.threshold).color}>
                            {thresholdZone(config.objectDetection.threshold).label}
                          </span>
                        </p>
                      </div>
                      <Slider
                        label="Frecuencia (FPS)"
                        value={config.objectDetection.fps}
                        onChange={(value) =>
                          updateConfig({ objectDetection: { ...config.objectDetection, fps: value } })
                        }
                        min={1}
                        max={30}
                        step={1}
                      />
                      <div className="text-sm text-moss">
                        Objetos soportados: dispositivos electronicos, muebles, utensilios, ropa, transporte, animales, herramientas y mas.
                      </div>
                    </div>
                  )}
                </section>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>

      {/* ── Reset button ───────────────────────────────────────────── */}
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.25 }}
        className="flex justify-center"
      >
        <button
          type="button"
          onClick={resetToBalanced}
          className="btn btn-ghost flex items-center gap-2 text-moss hover:text-forest transition-colors"
        >
          <RotateCcw size={16} />
          Restablecer valores
        </button>
      </motion.div>
    </div>
  )
}
