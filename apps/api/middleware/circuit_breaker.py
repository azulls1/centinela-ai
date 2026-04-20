"""Circuit breaker pattern for backend external service calls."""
import time
import logging
from enum import Enum
from typing import Callable, TypeVar, Any
from functools import wraps

logger = logging.getLogger(__name__)
T = TypeVar('T')

class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, reset_timeout: float = 30.0, name: str = "default"):
        self.name = name
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout
        self.state = CircuitState.CLOSED
        self.failures = 0
        self.last_failure_time = 0.0
        self.half_open_attempts = 0

    def __call__(self, func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            if self.state == CircuitState.OPEN:
                if time.time() - self.last_failure_time > self.reset_timeout:
                    self.state = CircuitState.HALF_OPEN
                    self.half_open_attempts = 0
                    logger.info(f"Circuit breaker [{self.name}] transitioning to HALF_OPEN")
                else:
                    raise Exception(f"Circuit breaker [{self.name}] is OPEN")

            try:
                result = await func(*args, **kwargs)
                self._on_success()
                return result
            except Exception as e:
                self._on_failure()
                raise

        wrapper.breaker = self
        return wrapper

    def _on_success(self):
        if self.state == CircuitState.HALF_OPEN:
            logger.info(f"Circuit breaker [{self.name}] recovered -> CLOSED")
        self.failures = 0
        self.state = CircuitState.CLOSED

    def _on_failure(self):
        self.failures += 1
        self.last_failure_time = time.time()
        if self.failures >= self.failure_threshold:
            self.state = CircuitState.OPEN
            logger.warning(f"Circuit breaker [{self.name}] -> OPEN after {self.failures} failures")

# Pre-configured breakers
supabase_breaker = CircuitBreaker(failure_threshold=5, reset_timeout=30, name="supabase")
openai_breaker = CircuitBreaker(failure_threshold=3, reset_timeout=60, name="openai")
stream_gateway_breaker = CircuitBreaker(failure_threshold=3, reset_timeout=15, name="stream-gateway")
