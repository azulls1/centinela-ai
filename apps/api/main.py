"""
FastAPI Backend para IAGENTEK Vision Human Insight
Maneja endpoints para eventos, estadísticas, reportes y análisis
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Optional
from datetime import datetime, timedelta
import os
import logging
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

from models import Event, EventCreate, EventStats, HealthSummary
from supabase_client import get_supabase_client
from routers import events, analytics, reports, ai_summary, external_cameras, sessions
from middleware.rate_limiter import RateLimiterMiddleware
from middleware.audit import AuditMiddleware
from middleware.metrics import MetricsMiddleware, router as metrics_router

# Cargar variables de entorno
load_dotenv()

# Crear aplicación FastAPI
app = FastAPI(
    title="Vision Human Insight API",
    description="API backend para la plataforma de visión por computadora",
    version="1.0.0",
)

# Configurar CORS para permitir peticiones del frontend
frontend_url = os.getenv("FRONTEND_URL", "http://localhost:9300").rstrip("/")

allowed_origins = {
    "http://localhost:9300",
    "http://localhost:3000",
    frontend_url,
}

# Agregar esquema alternativo si aplica (http <-> https) para el mismo host
if frontend_url.startswith("https://"):
    allowed_origins.add(frontend_url.replace("https://", "http://", 1))
elif frontend_url.startswith("http://"):
    allowed_origins.add(frontend_url.replace("http://", "https://", 1))

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(allowed_origins),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
)

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' data: blob:; connect-src 'self' https://*.iagentek.com.mx http://localhost:* ws://localhost:*"
        return response


app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(MetricsMiddleware)
app.add_middleware(RateLimiterMiddleware, requests_per_minute=600, burst=50)
app.add_middleware(AuditMiddleware)

# Incluir routers
app.include_router(events.router, prefix="/api/events", tags=["events"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])
app.include_router(reports.router, prefix="/api/reports", tags=["reports"])
app.include_router(ai_summary.router, prefix="/api/ai", tags=["ai"])
app.include_router(external_cameras.router, prefix="/api/external-cameras", tags=["external_cameras"])
app.include_router(sessions.router, prefix="/api/sessions", tags=["sessions"])
app.include_router(metrics_router, tags=["metrics"])


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Catch-all so that 500s still carry CORS headers."""
    origin = request.headers.get("origin", "")
    headers = {}
    if origin in allowed_origins:
        headers["Access-Control-Allow-Origin"] = origin
        headers["Access-Control-Allow-Credentials"] = "true"
    logger.exception("Unhandled error: %s", exc)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
        headers=headers,
    )


@app.get("/")
async def root():
    """Endpoint raíz - información de la API"""
    return {
        "message": "IAGENTEK Vision Human Insight API",
        "version": "1.0.0",
        "status": "running",
    }


@app.get("/api/health")
async def health_check():
    """Endpoint de salud - verificar que la API esté funcionando"""
    try:
        # Verificar conexión con Supabase
        supabase = get_supabase_client()
        # Hacer una query simple para verificar conexión
        result = supabase.table("vishum_events").select("id").limit(1).execute()
        
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.exception("Health check failed")
        raise HTTPException(
            status_code=503,
            detail="Service unhealthy"
        )


@app.get("/api/info")
async def api_info():
    """Información sobre la API y capacidades"""
    return {
        "name": "Vision Human Insight API",
        "version": "1.0.0",
        "features": [
            "Event tracking",
            "Analytics",
            "Health summaries",
            "Report generation",
        ],
        "endpoints": {
            "events": "/api/events",
            "analytics": "/api/analytics",
            "reports": "/api/reports",
            "health": "/api/health",
        },
    }


if __name__ == "__main__":
    import uvicorn
    import sys
    import os
    
    # Asegurar que el directorio actual esté en el path
    sys.path.insert(0, os.path.dirname(__file__))
    
    # Ejecutar servidor con uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=9301,
        reload=True,  # Auto-reload en desarrollo
    )

