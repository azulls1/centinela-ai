import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { Toggle } from '../../components/Toggle'

describe('Toggle', () => {
  it('renders in off state', () => {
    const onChange = vi.fn()
    render(<Toggle enabled={false} onChange={onChange} />)
    const button = screen.getByRole('button')
    expect(button).toHaveClass('bg-gray-300')
  })

  it('renders in on state', () => {
    const onChange = vi.fn()
    render(<Toggle enabled={true} onChange={onChange} />)
    const button = screen.getByRole('button')
    expect(button).toHaveClass('bg-forest')
  })

  it('calls onChange when clicked', () => {
    const onChange = vi.fn()
    render(<Toggle enabled={false} onChange={onChange} />)
    fireEvent.click(screen.getByRole('button'))
    expect(onChange).toHaveBeenCalledWith(true)
  })

  it('does not call onChange when disabled', () => {
    const onChange = vi.fn()
    render(<Toggle enabled={false} onChange={onChange} disabled />)
    fireEvent.click(screen.getByRole('button'))
    expect(onChange).not.toHaveBeenCalled()
  })
})
