import { useMemo } from 'react'
import { MAX_ACTIVE_CAMERAS, useAppStore } from '../store/appStore'
import { Toggle } from './Toggle'
import type { PerformancePreset } from '../types'

const presetOptions: Array<{
  value: PerformancePreset
  label: string
  description: string
}> = [
  {
    value: 'performance',
    label: 'Rendimiento',
    description: 'Prioriza FPS altos. Desactiva emociones y objetos, usa baja resolución.',
  },
  {
    value: 'balanced',
    label: 'Equilibrado',
    description: 'Compensa calidad y velocidad. Recomendado por defecto.',
  },
  {
    value: 'quality',
    label: 'Calidad',
    description: 'Máxima resolución y todos los modelos activos. Requiere GPU potente.',
  },
]

export function PerformancePanel() {
  const performancePreset = useAppStore((state) => state.performancePreset)
  const autoPerformanceManagement = useAppStore((state) => state.autoPerformanceManagement)
  const setPerformancePreset = useAppStore((state) => state.setPerformancePreset)
  const toggleAutoPerformanceManagement = useAppStore((state) => state.toggleAutoPerformanceManagement)
  const aggregated = useAppStore((state) => state.aggregatedDetections)
  const activeCameraIds = useAppStore((state) => state.activeCameraIds)

  const avgFPS = useMemo(() => aggregated.averageFPS.toFixed(1), [aggregated.averageFPS])

  return (
    <section className="card mb-4">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-3 mb-3">
        <div>
          <h3 className="text-forest font-semibold mb-1">Gestión de Rendimiento</h3>
          <p className="text-moss text-sm mb-0">
            Ajusta resolución, FPS y modelos activos para equilibrar calidad y fluidez (máx. {MAX_ACTIVE_CAMERAS} cámaras).
          </p>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-moss text-sm">Auto</span>
          <Toggle
            enabled={autoPerformanceManagement}
            onChange={(value) => toggleAutoPerformanceManagement(value)}
          />
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-3 items-center mb-3">
        <div>
          <label className="label text-moss text-sm mb-1">Preset</label>
          <select
            className="select"
            value={performancePreset}
            onChange={(event) => setPerformancePreset(event.target.value as PerformancePreset)}
          >
            {presetOptions.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </div>
        <div>
          <div className="p-2 rounded-lg bg-gray-50 border border-gray-100 rounded-lg">
            <div className="flex justify-between text-moss text-sm">
              <span>FPS promedio</span>
              <span className="text-forest font-semibold">{avgFPS}</span>
            </div>
            <div className="flex justify-between text-moss text-sm">
              <span>Cámaras activas</span>
              <span className="text-forest font-semibold">{activeCameraIds.length}</span>
            </div>
          </div>
        </div>
      </div>

      <div className="flex flex-col gap-2">
        {presetOptions.map((option) => (
          <div
            key={option.value}
            className={`p-2 rounded-lg ${option.value === performancePreset ? 'border-2 border-forest text-forest' : 'border border-gray-200 text-moss'}`}
          >
            <div className="flex justify-between items-center mb-1">
              <span className="font-semibold">{option.label}</span>
              {option.value === performancePreset && <span className="badge badge-info">Activo</span>}
            </div>
            <span className="text-sm">{option.description}</span>
          </div>
        ))}
      </div>
    </section>
  )
}
