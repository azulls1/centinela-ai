import { useEffect, useMemo, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { ShieldCheck, Send, Loader2, Building, Mail, User, Target } from 'lucide-react'

interface SessionStartModalProps {
  show: boolean
  onSubmit: (payload: {
    name: string
    email: string
    organization?: string
    plan: string
    purpose?: string
  }) => Promise<void>
  isSubmitting: boolean
  error: string | null
}

const DEFAULT_PLAN = 'Demo pública'

const purposeOptions = [
  'Evaluar detecciones y precisión',
  'Demostración para cliente',
  'Configuración de pruebas internas',
  'Investigación / benchmark',
  'Otro',
]

export function SessionStartModal({ show, onSubmit, isSubmitting, error }: SessionStartModalProps) {
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [organization, setOrganization] = useState('')
  const [purpose, setPurpose] = useState(purposeOptions[0]!)
  const [formError, setFormError] = useState<string | null>(null)

  useEffect(() => {
    if (!show) {
      setFormError(null)
      setName('')
      setEmail('')
      setOrganization('')
      setPurpose(purposeOptions[0]!)
    }
  }, [show])

  const isValidEmail = useMemo(() => {
    if (!email) return false
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)
  }, [email])

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault()
    setFormError(null)

    if (!name.trim()) {
      setFormError('Ingresa tu nombre para personalizar la demo.')
      return
    }

    if (!isValidEmail) {
      setFormError('Ingresa un correo válido para continuar.')
      return
    }

    try {
      await onSubmit({
        name: name.trim(),
        email: email.trim(),
        organization: organization.trim() || undefined,
        plan: DEFAULT_PLAN,
        purpose,
      })
    } catch (submitError: unknown) {
      const message =
        submitError instanceof Error
          ? submitError.message
          : 'No se pudo iniciar la sesión. Intenta nuevamente.'
      setFormError(message)
    }
  }

  return (
    <AnimatePresence>
      {show && (
        <motion.div
          className="session-modal-backdrop"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
        >
          <motion.div
            className="session-modal-card"
            initial={{ opacity: 0, y: 32 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 16 }}
            transition={{ duration: 0.35, ease: 'easeOut' }}
          >
            <header className="session-modal-header">
              <div className="flex items-center gap-3">
                <ShieldCheck size={42} className="text-forest shrink-0" />
                <div>
                  <h2 className="text-forest font-semibold mb-1">Activa tu demo Vision Human Insight</h2>
                  <p className="text-moss mb-0">
                    Cuéntanos quién eres para personalizar la experiencia, registrar métricas y compartirte mejoras.
                  </p>
                </div>
              </div>
            </header>

            <form className="session-modal-form" onSubmit={handleSubmit}>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                <div>
                  <label className="label">Nombre / Alias *</label>
                  <div className="flex items-center border border-gray-200 rounded-lg overflow-hidden">
                    <span className="px-3 text-moss">
                      <User size={16} />
                    </span>
                    <input
                      type="text"
                      className="input border-0 flex-1"
                      value={name}
                      onChange={(event) => setName(event.target.value)}
                      placeholder="Ej. María Sánchez"
                      required
                    />
                  </div>
                </div>
                <div>
                  <label className="label">Correo electrónico *</label>
                  <div className="flex items-center border border-gray-200 rounded-lg overflow-hidden">
                    <span className="px-3 text-moss">
                      <Mail size={16} />
                    </span>
                    <input
                      type="email"
                      className="input border-0 flex-1"
                      value={email}
                      onChange={(event) => setEmail(event.target.value)}
                      placeholder="correo@empresa.com"
                      required
                    />
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                <div>
                  <label className="label">Empresa / Organización</label>
                  <div className="flex items-center border border-gray-200 rounded-lg overflow-hidden">
                    <span className="px-3 text-moss">
                      <Building size={16} />
                    </span>
                    <input
                      type="text"
                      className="input border-0 flex-1"
                      value={organization}
                      onChange={(event) => setOrganization(event.target.value)}
                      placeholder="Opcional"
                    />
                  </div>
                </div>
                <div>
                  <label className="label">Objetivo principal</label>
                  <div className="flex items-center border border-gray-200 rounded-lg overflow-hidden">
                    <span className="px-3 text-moss">
                      <Target size={16} />
                    </span>
                    <select
                      className="select border-0 flex-1"
                      value={purpose}
                      onChange={(event) => setPurpose(event.target.value)}
                    >
                      {purposeOptions.map((option) => (
                        <option key={option} value={option}>
                          {option}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>
              </div>

              {(formError || error) && (
                <div className="alert alert-error">
                  {formError || error}
                </div>
              )}

              <div className="flex justify-end gap-3 items-center mt-3">
                <span className="text-moss text-sm">
                  Al continuar aceptas el uso de datos técnicos para monitorear tu sesión.
                </span>
                <button
                  type="submit"
                  className="btn btn-primary inline-flex items-center gap-2"
                  disabled={isSubmitting}
                >
                  {isSubmitting ? (
                    <>
                      <Loader2 size={16} className="spin" />
                      Iniciando…
                    </>
                  ) : (
                    <>
                      <Send size={16} />
                      Comenzar demo
                    </>
                  )}
                </button>
              </div>
            </form>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}
