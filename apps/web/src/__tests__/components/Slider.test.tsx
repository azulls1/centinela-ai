import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { Slider } from '../../components/Slider'

describe('Slider', () => {
  const defaultProps = { label: 'Test Slider', value: 0.5, onChange: vi.fn(), min: 0, max: 1, step: 0.1 }

  it('renders with label and value', () => {
    render(<Slider {...defaultProps} />)
    expect(screen.getByText('Test Slider')).toBeTruthy()
    expect(screen.getByText('0.50')).toBeTruthy()
  })

  it('renders range input with correct attributes', () => {
    render(<Slider {...defaultProps} />)
    const input = screen.getByRole('slider')
    expect(input.getAttribute('min')).toBe('0')
    expect(input.getAttribute('max')).toBe('1')
    expect(input.getAttribute('step')).toBe('0.1')
  })

  it('calls onChange when value changes', () => {
    const onChange = vi.fn()
    render(<Slider {...defaultProps} onChange={onChange} />)
    fireEvent.change(screen.getByRole('slider'), { target: { value: '0.8' } })
    expect(onChange).toHaveBeenCalledWith(0.8)
  })
})
