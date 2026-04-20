import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import { Navbar } from '../../components/Navbar'

const renderWithRouter = (ui: React.ReactElement) => render(<BrowserRouter>{ui}</BrowserRouter>)

describe('Navbar', () => {
  it('renders brand name', () => {
    renderWithRouter(<Navbar />)
    expect(screen.getByText('Vision Human Insight')).toBeTruthy()
  })

  it('renders navigation links', () => {
    renderWithRouter(<Navbar />)
    expect(screen.getByText('Live')).toBeTruthy()
    expect(screen.getByText('Dashboard')).toBeTruthy()
    expect(screen.getByText('Configuración')).toBeTruthy()
  })

  it('has correct link destinations', () => {
    renderWithRouter(<Navbar />)
    expect(screen.getByText('Live').closest('a')?.getAttribute('href')).toBe('/')
    expect(screen.getByText('Dashboard').closest('a')?.getAttribute('href')).toBe('/dashboard')
    expect(screen.getByText('Configuración').closest('a')?.getAttribute('href')).toBe('/settings')
  })
})
