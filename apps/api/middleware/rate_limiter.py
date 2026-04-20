"""Simple in-memory rate limiter."""
import time
import logging
from collections import defaultdict
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

logger = logging.getLogger(__name__)

class RateLimiterMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, requests_per_minute: int = 60, burst: int = 10):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.burst = burst
        self.clients: dict[str, list[float]] = defaultdict(list)

    async def dispatch(self, request: Request, call_next) -> Response:
        client_ip = request.client.host if request.client else "unknown"
        now = time.time()
        window = 60.0

        # Clean old entries
        self.clients[client_ip] = [t for t in self.clients[client_ip] if now - t < window]

        if len(self.clients[client_ip]) >= self.requests_per_minute:
            logger.warning(f"Rate limit exceeded for {client_ip}")
            origin = request.headers.get("origin", "")
            cors_headers = {
                "Retry-After": "60",
                "Access-Control-Allow-Origin": origin,
                "Access-Control-Allow-Credentials": "true",
            }
            return Response(
                content='{"detail":"Rate limit exceeded. Try again later."}',
                status_code=429,
                media_type="application/json",
                headers=cors_headers,
            )

        self.clients[client_ip].append(now)
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(max(0, self.requests_per_minute - len(self.clients[client_ip])))
        return response
