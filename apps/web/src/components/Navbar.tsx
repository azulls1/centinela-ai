import { Link, useLocation } from 'react-router-dom'
import { Camera, BarChart3, Settings, Sun, Moon } from 'lucide-react'
import { motion } from 'framer-motion'
import { useAppStore } from '../store/appStore'

/**
 * Barra de navegación - Forest Design System
 */
export function Navbar() {
  const location = useLocation()
  const isActive = (path: string) => location.pathname === path
  const theme = useAppStore((state) => state.theme)
  const setTheme = useAppStore((state) => state.setTheme)

  const isDark = theme === 'dark' || (theme === 'system' && typeof window !== 'undefined' && window.matchMedia('(prefers-color-scheme: dark)').matches)

  const toggleTheme = () => {
    setTheme(isDark ? 'light' : 'dark')
  }

  const navLinkClass = (path: string) =>
    `flex items-center gap-2 px-3 py-2 rounded-lg text-sm transition-colors ${
      isActive(path)
        ? isDark
          ? 'bg-[#5B7065] text-white font-semibold shadow-forest'
          : 'bg-forest text-white font-semibold shadow-forest'
        : isDark
          ? 'text-pine hover:bg-[#243044] hover:text-forest'
          : 'text-pine hover:bg-gray-100 hover:text-forest'
    }`

  return (
    <nav className="navbar">
      <div className="w-full px-6 flex items-center justify-between">
        {/* Brand */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
        >
          <Link to="/" className="flex items-center gap-2.5 group">
            <img
              src="/images/logo-iagentek.webp"
              alt="IAGENTEK"
              className={`h-7 w-auto transition-opacity group-hover:opacity-80 ${isDark ? 'brightness-0 invert' : 'brightness-0'}`}
            />
            <div className="flex flex-col leading-tight">
              <span className="text-sm font-bold text-forest tracking-tight font-display">
                Vision Human Insight
              </span>
              <span className="text-[10px] uppercase tracking-widest text-moss font-medium">
                IAGENTEK
              </span>
            </div>
          </Link>
        </motion.div>

        {/* Navigation */}
        <div className="flex items-center gap-1">
          <motion.div whileHover={{ scale: 1.03 }} whileTap={{ scale: 0.97 }}>
            <Link
              to="/"
              className={navLinkClass('/')}
            >
              <Camera size={16} />
              <span>Live</span>
            </Link>
          </motion.div>

          <motion.div whileHover={{ scale: 1.03 }} whileTap={{ scale: 0.97 }}>
            <Link
              to="/dashboard"
              className={navLinkClass('/dashboard')}
            >
              <BarChart3 size={16} />
              <span>Dashboard</span>
            </Link>
          </motion.div>

          <motion.div whileHover={{ scale: 1.03 }} whileTap={{ scale: 0.97 }}>
            <Link
              to="/settings"
              className={navLinkClass('/settings')}
            >
              <Settings size={16} />
              <span>Configuracion</span>
            </Link>
          </motion.div>

          <div className="ml-2 border-l border-current/10 pl-2">
            <motion.button
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
              onClick={toggleTheme}
              className="btn-icon flex items-center justify-center"
              title={isDark ? 'Cambiar a modo claro' : 'Cambiar a modo oscuro'}
              aria-label={isDark ? 'Cambiar a modo claro' : 'Cambiar a modo oscuro'}
            >
              {isDark ? <Sun size={18} /> : <Moon size={18} />}
            </motion.button>
          </div>
        </div>
      </div>
    </nav>
  )
}
