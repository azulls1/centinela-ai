import { describe, it, expect, vi, beforeEach } from 'vitest'
import { CircuitBreaker, withRetry, withTimeout } from '../../lib/resilience'

describe('CircuitBreaker', () => {
  let breaker: CircuitBreaker

  beforeEach(() => {
    breaker = new CircuitBreaker({ failureThreshold: 3, resetTimeout: 100 })
  })

  it('starts in CLOSED state', () => {
    expect(breaker.getState()).toBe('CLOSED')
  })

  it('allows successful calls', async () => {
    const result = await breaker.execute(() => Promise.resolve('ok'))
    expect(result).toBe('ok')
    expect(breaker.getState()).toBe('CLOSED')
  })

  it('opens after threshold failures', async () => {
    const fail = () => Promise.reject(new Error('fail'))
    for (let i = 0; i < 3; i++) {
      await breaker.execute(fail).catch(() => {})
    }
    expect(breaker.getState()).toBe('OPEN')
  })

  it('rejects calls when OPEN', async () => {
    const fail = () => Promise.reject(new Error('fail'))
    for (let i = 0; i < 3; i++) await breaker.execute(fail).catch(() => {})
    await expect(breaker.execute(() => Promise.resolve('ok'))).rejects.toThrow('OPEN')
  })

  it('recovers after reset timeout', async () => {
    const fail = () => Promise.reject(new Error('fail'))
    for (let i = 0; i < 3; i++) await breaker.execute(fail).catch(() => {})
    await new Promise(r => setTimeout(r, 150))
    const result = await breaker.execute(() => Promise.resolve('recovered'))
    expect(result).toBe('recovered')
    expect(breaker.getState()).toBe('CLOSED')
  })
})

describe('withRetry', () => {
  it('succeeds on first attempt', async () => {
    const fn = vi.fn().mockResolvedValue('ok')
    expect(await withRetry(fn, { maxRetries: 3, baseDelay: 10 })).toBe('ok')
    expect(fn).toHaveBeenCalledTimes(1)
  })

  it('retries on failure then succeeds', async () => {
    const fn = vi.fn().mockRejectedValueOnce(new Error('fail')).mockResolvedValue('ok')
    expect(await withRetry(fn, { maxRetries: 3, baseDelay: 10 })).toBe('ok')
    expect(fn).toHaveBeenCalledTimes(2)
  })

  it('throws after max retries', async () => {
    const fn = vi.fn().mockRejectedValue(new Error('always fails'))
    await expect(withRetry(fn, { maxRetries: 2, baseDelay: 10 })).rejects.toThrow('always fails')
    expect(fn).toHaveBeenCalledTimes(3)
  })
})

describe('withTimeout', () => {
  it('resolves if within timeout', async () => {
    expect(await withTimeout(() => Promise.resolve('fast'), 1000)).toBe('fast')
  })

  it('rejects if exceeds timeout', async () => {
    const slow = () => new Promise(r => setTimeout(() => r('slow'), 500))
    await expect(withTimeout(slow, 50)).rejects.toThrow('Timeout')
  })
})
