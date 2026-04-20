import { Component, type ErrorInfo, type ReactNode } from 'react'
import { AlertTriangle } from 'lucide-react'

interface Props {
  children: ReactNode
}

interface State {
  hasError: boolean
  error: Error | null
  errorInfo: ErrorInfo | null
}

/**
 * Error Boundary global - captura errores de renderizado en componentes hijos
 * y muestra una pantalla amigable en lugar de un crash completo.
 */
export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props)
    this.state = { hasError: false, error: null, errorInfo: null }
  }

  static getDerivedStateFromError(error: Error): Partial<State> {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    this.setState({ errorInfo })
    console.error('[ErrorBoundary]', error, errorInfo)
  }

  handleReload = () => {
    window.location.reload()
  }

  handleGoHome = () => {
    window.location.href = '/'
  }

  render() {
    if (!this.state.hasError) {
      return this.props.children
    }

    const isDev = import.meta.env.DEV

    return (
      <div className="min-h-screen flex items-center justify-center bg-[var(--color-bg-page,#F7F8F7)] dark:bg-gray-900 p-6">
        <div className="w-full max-w-md rounded-2xl bg-white dark:bg-gray-800 border border-[var(--color-gray-100,#EFF0EE)] shadow-[0_4px_24px_rgba(4,32,44,0.08)] p-8 text-center">
          {/* Icon */}
          <div className="mx-auto mb-5 flex h-16 w-16 items-center justify-center rounded-full bg-amber-50 dark:bg-amber-900/20">
            <AlertTriangle size={32} className="text-amber-500" />
          </div>

          {/* Title */}
          <h1 className="text-xl font-bold text-[var(--color-forest,#04202C)] dark:text-gray-100 mb-2">
            Algo salio mal
          </h1>

          {/* Message */}
          <p className="text-sm text-[var(--color-moss,#9EADA3)] dark:text-gray-400 mb-6">
            La aplicacion encontro un error inesperado.
          </p>

          {/* Actions */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-3">
            <button
              onClick={this.handleReload}
              className="w-full sm:w-auto px-5 py-2.5 rounded-lg text-sm font-semibold text-white bg-[var(--color-forest,#04202C)] hover:opacity-90 transition-opacity"
            >
              Recargar pagina
            </button>
            <button
              onClick={this.handleGoHome}
              className="w-full sm:w-auto px-5 py-2.5 rounded-lg text-sm font-semibold text-[var(--color-forest,#04202C)] dark:text-gray-200 bg-[var(--color-gray-50,#F7F8F7)] dark:bg-gray-700 border border-[var(--color-gray-200,#E0E2DE)] dark:border-gray-600 hover:bg-[var(--color-gray-100,#EFF0EE)] dark:hover:bg-gray-600 transition-colors"
            >
              Volver al inicio
            </button>
          </div>

          {/* Dev error details */}
          {isDev && this.state.error && (
            <details className="mt-6 text-left">
              <summary className="cursor-pointer text-xs font-medium text-[var(--color-moss,#9EADA3)] hover:text-[var(--color-forest,#04202C)] dark:hover:text-gray-200 transition-colors">
                Detalles del error (solo desarrollo)
              </summary>
              <div className="mt-3 rounded-lg bg-[var(--color-gray-50,#F7F8F7)] dark:bg-gray-900 border border-[var(--color-gray-200,#E0E2DE)] dark:border-gray-700 p-4 overflow-auto max-h-64">
                <p className="text-xs font-mono text-red-600 dark:text-red-400 break-words mb-2">
                  {this.state.error.message}
                </p>
                {this.state.error.stack && (
                  <pre className="text-[10px] font-mono text-[var(--color-moss,#9EADA3)] dark:text-gray-500 whitespace-pre-wrap break-words">
                    {this.state.error.stack}
                  </pre>
                )}
              </div>
            </details>
          )}
        </div>
      </div>
    )
  }
}
