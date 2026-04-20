import { describe, it, expect, beforeEach } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { PrivacyBanner } from '../../components/PrivacyBanner'
import { useAppStore } from '../../store/appStore'

describe('PrivacyBanner', () => {
  beforeEach(() => {
    useAppStore.setState({ privacyAccepted: false })
  })

  it('renders privacy notice', () => {
    render(<PrivacyBanner />)
    expect(screen.getByText(/Aviso de Privacidad/)).toBeTruthy()
  })

  it('renders accept button', () => {
    render(<PrivacyBanner />)
    expect(screen.getByText('Aceptar y Continuar')).toBeTruthy()
  })

  it('sets privacy accepted on click', () => {
    render(<PrivacyBanner />)
    fireEvent.click(screen.getByText('Aceptar y Continuar'))
    expect(useAppStore.getState().privacyAccepted).toBe(true)
  })
})
