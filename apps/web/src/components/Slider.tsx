interface SliderProps {
  label: string // Etiqueta del slider
  value: number // Valor actual
  onChange: (value: number) => void // Callback cuando cambia
  min: number // Valor mínimo
  max: number // Valor máximo
  step: number // Incremento
}

/**
 * Componente de slider (deslizador) reutilizable
 */
export function Slider({ label, value, onChange, min, max, step }: SliderProps) {
  return (
    <div>
      <div className="flex items-center justify-between mb-1">
        <label className="text-sm text-forest">{label}</label>
        <span className="text-sm text-moss font-mono">{value.toFixed(2)}</span>
      </div>
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(e) => onChange(parseFloat(e.target.value))} // Actualizar valor
        className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-[#04202C]"
      />
    </div>
  )
}

