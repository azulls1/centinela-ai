import { Link } from 'react-router-dom'
import { Search } from 'lucide-react'
import { motion } from 'framer-motion'

/**
 * Pagina 404 - ruta no encontrada
 */
export function NotFoundPage() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, ease: 'easeOut' }}
      className="min-h-screen flex items-center justify-center bg-[var(--color-bg-page,#F7F8F7)] dark:bg-gray-900 p-6"
    >
      <div className="text-center">
        {/* Icon */}
        <div className="mx-auto mb-6 flex h-20 w-20 items-center justify-center rounded-full bg-[var(--color-gray-50,#F7F8F7)] dark:bg-gray-800 border border-[var(--color-gray-200,#E0E2DE)] dark:border-gray-700">
          <Search size={36} className="text-[var(--color-moss,#9EADA3)]" />
        </div>

        {/* 404 */}
        <h1 className="text-7xl font-bold text-[var(--color-forest,#04202C)] dark:text-gray-100 mb-3 tracking-tight">
          404
        </h1>

        {/* Title */}
        <h2 className="text-xl font-semibold text-[var(--color-forest,#04202C)] dark:text-gray-200 mb-2">
          Pagina no encontrada
        </h2>

        {/* Subtitle */}
        <p className="text-sm text-[var(--color-moss,#9EADA3)] dark:text-gray-400 mb-8 max-w-sm mx-auto">
          La pagina que buscas no existe o fue movida.
        </p>

        {/* Action */}
        <Link
          to="/"
          className="inline-flex items-center gap-2 px-6 py-2.5 rounded-lg text-sm font-semibold text-white bg-[var(--color-forest,#04202C)] hover:opacity-90 transition-opacity"
        >
          Volver al inicio
        </Link>
      </div>
    </motion.div>
  )
}

export default NotFoundPage
