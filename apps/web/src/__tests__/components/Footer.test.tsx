import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { Footer } from '../../components/Footer'

describe('Footer', () => {
  it('renders copyright with current year', () => {
    render(<Footer />)
    expect(screen.getByText(new RegExp(new Date().getFullYear().toString()))).toBeTruthy()
  })

  it('renders technology list', () => {
    render(<Footer />)
    expect(screen.getByText(/React \+ Vite/)).toBeTruthy()
  })

  it('renders contact email', () => {
    render(<Footer />)
    const link = screen.getByText('azull.samael@gmail.com')
    expect(link.getAttribute('href')).toBe('mailto:azull.samael@gmail.com')
  })

  it('renders policy links', () => {
    render(<Footer />)
    expect(screen.getByText(/Política de privacidad/)).toBeTruthy()
  })
})
