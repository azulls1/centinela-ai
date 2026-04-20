"""Audit trail middleware for tracking all API access."""
import time
import logging
import json
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

audit_logger = logging.getLogger("audit")
audit_logger.setLevel(logging.INFO)

class AuditMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        start_time = time.time()
        client_ip = request.client.host if request.client else "unknown"

        response = await call_next(request)

        duration_ms = round((time.time() - start_time) * 1000, 2)

        audit_entry = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "method": request.method,
            "path": str(request.url.path),
            "query": str(request.url.query) if request.url.query else None,
            "client_ip": client_ip,
            "user_agent": request.headers.get("user-agent", ""),
            "status_code": response.status_code,
            "duration_ms": duration_ms,
            "api_key": "***" if request.headers.get("x-api-key") else None,
            "admin": bool(request.headers.get("authorization")),
        }

        audit_logger.info(json.dumps(audit_entry))
        return response
