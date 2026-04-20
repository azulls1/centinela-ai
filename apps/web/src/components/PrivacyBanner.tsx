import { useAppStore } from '../store/appStore'

/**
 * Banner de privacidad que se muestra al inicio
 * El usuario debe aceptar antes de usar la aplicación
 */
export function PrivacyBanner() {
  const setPrivacyAccepted = useAppStore((state) => state.setPrivacyAccepted)

  const handleAccept = () => {
    setPrivacyAccepted(true) // Marcar privacidad como aceptada
  }

  return (
    <div className="fixed top-0 left-0 right-0 z-50 bg-white border-b border-gray-200 p-4 shadow-forest-lg">
      <div className="max-w-4xl mx-auto flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        {/* Contenido del banner */}
        <div className="flex-1">
          <h3 className="text-lg font-semibold text-forest mb-2">
            🔒 Aviso de Privacidad
          </h3>
          <p className="text-sm text-moss">
            Esta aplicación utiliza visión por computadora para analizar video en tiempo real.
            El procesamiento se realiza <strong>localmente en tu navegador</strong> (edge AI).
            No se almacenan imágenes por defecto. Solo se guardan metadatos de detecciones
            cuando superan los umbrales configurados. Al continuar, aceptas el procesamiento
            de datos biométricos con fines de demostración.
          </p>
        </div>

        {/* Botón de aceptar */}
        <button
          onClick={handleAccept}
          className="btn btn-primary whitespace-nowrap"
        >
          Aceptar y Continuar
        </button>
      </div>
    </div>
  )
}

