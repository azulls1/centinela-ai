interface ToggleProps {
  enabled: boolean // Estado actual del toggle
  onChange: (enabled: boolean) => void // Callback cuando cambia
  disabled?: boolean // Deshabilitar interacción
}

/**
 * Componente de toggle (switch) reutilizable
 */
export function Toggle({ enabled, onChange, disabled = false }: ToggleProps) {
  return (
    <button
      type="button"
      onClick={() => {
        if (!disabled) {
          onChange(!enabled)
        }
      }}
      disabled={disabled}
      className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
        enabled ? 'bg-forest' : 'bg-gray-300'
      } ${disabled ? 'opacity-50 cursor-not-allowed' : ''}`}
    >
      <span
        className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
          enabled ? 'translate-x-6' : 'translate-x-1'
        }`}
      />
    </button>
  )
}


