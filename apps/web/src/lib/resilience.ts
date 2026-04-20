/**
 * Resilience patterns: Circuit Breaker, Retry, Timeout
 */

type CircuitState = 'CLOSED' | 'OPEN' | 'HALF_OPEN'

interface CircuitBreakerOptions {
  failureThreshold: number
  resetTimeout: number
  halfOpenRequests: number
}

class CircuitBreaker {
  private state: CircuitState = 'CLOSED'
  private failures = 0
  private lastFailure = 0
  private halfOpenAttempts = 0
  private options: CircuitBreakerOptions

  constructor(options: Partial<CircuitBreakerOptions> = {}) {
    this.options = {
      failureThreshold: options.failureThreshold ?? 5,
      resetTimeout: options.resetTimeout ?? 30000,
      halfOpenRequests: options.halfOpenRequests ?? 2,
    }
  }

  async execute<T>(fn: () => Promise<T>): Promise<T> {
    if (this.state === 'OPEN') {
      if (Date.now() - this.lastFailure > this.options.resetTimeout) {
        this.state = 'HALF_OPEN'
        this.halfOpenAttempts = 0
      } else {
        throw new Error('Circuit breaker is OPEN')
      }
    }

    if (this.state === 'HALF_OPEN' && this.halfOpenAttempts >= this.options.halfOpenRequests) {
      throw new Error('Circuit breaker HALF_OPEN limit reached')
    }

    try {
      if (this.state === 'HALF_OPEN') this.halfOpenAttempts++
      const result = await fn()
      this.onSuccess()
      return result
    } catch (error) {
      this.onFailure()
      throw error
    }
  }

  private onSuccess() {
    this.failures = 0
    this.state = 'CLOSED'
  }

  private onFailure() {
    this.failures++
    this.lastFailure = Date.now()
    if (this.failures >= this.options.failureThreshold) {
      this.state = 'OPEN'
    }
  }

  getState(): CircuitState { return this.state }
  reset() { this.state = 'CLOSED'; this.failures = 0 }
}

async function withRetry<T>(
  fn: () => Promise<T>,
  options: { maxRetries?: number; baseDelay?: number; maxDelay?: number } = {}
): Promise<T> {
  const { maxRetries = 3, baseDelay = 1000, maxDelay = 10000 } = options
  let lastError: Error | undefined

  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      return await fn()
    } catch (error) {
      lastError = error instanceof Error ? error : new Error(String(error))
      if (attempt < maxRetries) {
        const delay = Math.min(baseDelay * Math.pow(2, attempt) + Math.random() * 500, maxDelay)
        await new Promise(resolve => setTimeout(resolve, delay))
      }
    }
  }
  throw lastError
}

async function withTimeout<T>(fn: () => Promise<T>, ms: number): Promise<T> {
  return Promise.race([
    fn(),
    new Promise<never>((_, reject) =>
      setTimeout(() => reject(new Error(`Timeout after ${ms}ms`)), ms)
    ),
  ])
}

// Pre-configured circuit breakers for different services
const supabaseBreaker = new CircuitBreaker({ failureThreshold: 5, resetTimeout: 30000 })
const apiBreaker = new CircuitBreaker({ failureThreshold: 3, resetTimeout: 15000 })

export async function resilientFetch(url: string, options?: RequestInit, config?: {
  timeout?: number
  retries?: number
  breaker?: 'supabase' | 'api'
}): Promise<Response> {
  const timeout = config?.timeout ?? 10000
  const retries = config?.retries ?? 2
  const breaker = config?.breaker === 'supabase' ? supabaseBreaker : apiBreaker

  return breaker.execute(() =>
    withRetry(
      () => withTimeout(() => fetch(url, options), timeout),
      { maxRetries: retries }
    )
  )
}

export { CircuitBreaker, withRetry, withTimeout, supabaseBreaker, apiBreaker }
