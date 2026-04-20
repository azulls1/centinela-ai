"""Prometheus-compatible metrics endpoint."""
import time
from collections import defaultdict
from fastapi import APIRouter
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, PlainTextResponse

router = APIRouter()

# In-memory metrics counters
_request_count: dict[str, int] = defaultdict(int)
_request_duration: dict[str, list[float]] = defaultdict(list)
_error_count: dict[str, int] = defaultdict(int)
_active_requests = 0

class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        global _active_requests
        _active_requests += 1
        start = time.time()

        try:
            response = await call_next(request)
            duration = time.time() - start

            path = request.url.path
            method = request.method
            key = f"{method}_{path}_{response.status_code}"

            _request_count[key] += 1
            _request_duration[key].append(duration)
            # Keep only last 1000 durations per endpoint
            if len(_request_duration[key]) > 1000:
                _request_duration[key] = _request_duration[key][-500:]

            if response.status_code >= 400:
                _error_count[f"{method}_{path}"] += 1

            return response
        finally:
            _active_requests -= 1

def _percentile(data: list[float], p: float) -> float:
    if not data:
        return 0.0
    sorted_data = sorted(data)
    k = (len(sorted_data) - 1) * p / 100
    f = int(k)
    c = f + 1 if f + 1 < len(sorted_data) else f
    return sorted_data[f] + (k - f) * (sorted_data[c] - sorted_data[f])

@router.get("/metrics", response_class=PlainTextResponse)
async def prometheus_metrics():
    lines = ["# Vision Human Insight API Metrics", ""]

    lines.append("# HELP http_requests_total Total HTTP requests")
    lines.append("# TYPE http_requests_total counter")
    for key, count in _request_count.items():
        parts = key.rsplit("_", 1)
        lines.append(f'http_requests_total{{endpoint="{parts[0]}",status="{parts[1]}"}} {count}')

    lines.append("")
    lines.append("# HELP http_request_duration_seconds HTTP request duration")
    lines.append("# TYPE http_request_duration_seconds summary")
    for key, durations in _request_duration.items():
        if durations:
            lines.append(f'http_request_duration_p50{{endpoint="{key}"}} {_percentile(durations, 50):.4f}')
            lines.append(f'http_request_duration_p95{{endpoint="{key}"}} {_percentile(durations, 95):.4f}')
            lines.append(f'http_request_duration_p99{{endpoint="{key}"}} {_percentile(durations, 99):.4f}')

    lines.append("")
    lines.append(f"# HELP active_requests Current active requests")
    lines.append(f"active_requests {_active_requests}")

    lines.append("")
    lines.append("# HELP http_errors_total Total HTTP errors")
    lines.append("# TYPE http_errors_total counter")
    for key, count in _error_count.items():
        lines.append(f'http_errors_total{{endpoint="{key}"}} {count}')

    return "\n".join(lines)
