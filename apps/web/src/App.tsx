import { lazy, Suspense, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate, useLocation } from 'react-router-dom'
import { PrivacyBanner } from './components/PrivacyBanner'
import { Navbar } from './components/Navbar'
import { ErrorBoundary } from './components/ErrorBoundary'

const LivePage = lazy(() => import('./pages/LivePage').then(m => ({ default: m.LivePage })))
const DashboardPage = lazy(() => import('./pages/DashboardPage').then(m => ({ default: m.DashboardPage })))
const SettingsPage = lazy(() => import('./pages/SettingsPage').then(m => ({ default: m.SettingsPage })))
const AdminPage = lazy(() => import('./pages/AdminPage').then(m => ({ default: m.AdminPage })))
const NotFoundPage = lazy(() => import('./pages/NotFoundPage'))
import { SESSION_STORAGE_KEY, useAppStore, applyThemeToDOM } from './store/appStore'
import { Footer } from './components/Footer'
import { logWarn } from './utils/logger'

/**
 * Componente principal de la aplicación
 * Maneja el enrutamiento y el banner de privacidad
 */
function App() {
  return (
    <ErrorBoundary>
      <Router future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
        <AppContent />
      </Router>
    </ErrorBoundary>
  )
}

function AppContent() {
  const location = useLocation()
  const { privacyAccepted, sessionInfo, setSessionInfo } = useAppStore((state) => ({
    privacyAccepted: state.privacyAccepted,
    sessionInfo: state.sessionInfo,
    setSessionInfo: state.setSessionInfo,
  }))
  const theme = useAppStore((state) => state.theme)
  const isAdminRoute = location.pathname.startsWith('/admin')

  // Initialize theme on mount and listen for system preference changes
  useEffect(() => {
    applyThemeToDOM(theme)

    if (theme === 'system') {
      const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
      const handleChange = () => applyThemeToDOM('system')
      mediaQuery.addEventListener('change', handleChange)
      return () => mediaQuery.removeEventListener('change', handleChange)
    }
  }, [theme])

  useEffect(() => {
    if (sessionInfo) {
      return
    }
    if (typeof window === 'undefined') {
      return
    }
    const stored = window.localStorage.getItem(SESSION_STORAGE_KEY)
    if (!stored) {
      return
    }

    try {
      const parsed = JSON.parse(stored)
      if (parsed?.session_id) {
        setSessionInfo(parsed)
      }
    } catch (error) {
      logWarn('No se pudo restaurar la sesión almacenada', error)
      window.localStorage.removeItem(SESSION_STORAGE_KEY)
    }
  }, [sessionInfo, setSessionInfo])

  return (
    <div className="min-h-screen flex flex-col text-forest">
      {!isAdminRoute && !privacyAccepted && <PrivacyBanner />}
      {!isAdminRoute && <Navbar />}

      <div className={`grow ${isAdminRoute ? 'flex flex-col' : ''}`}>
        <Suspense fallback={<div className="flex items-center justify-center min-h-screen"><div className="loading-dots"><span></span><span></span><span></span></div></div>}>
          <Routes>
            <Route path="/" element={<LivePage />} />
            <Route path="/cameras" element={<Navigate to="/" replace />} />
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/settings" element={<SettingsPage />} />
            <Route path="/admin" element={<AdminPage />} />
            <Route path="*" element={<NotFoundPage />} />
          </Routes>
        </Suspense>
      </div>

      {!isAdminRoute && <Footer />}
    </div>
  )
}

export default App

