"""
Router para generación de reportes
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional
from datetime import datetime, timedelta
import logging

from models import ReportRequest, ReportResponse
from supabase_client import get_supabase_client, Client

logger = logging.getLogger(__name__)

router = APIRouter()


def get_supabase() -> Client:
    """Dependency para obtener cliente de Supabase"""
    return get_supabase_client()


@router.post("/generate", response_model=ReportResponse)
async def generate_report(
    request: ReportRequest,
    supabase: Client = Depends(get_supabase),
):
    """
    Generar un reporte de eventos (PDF o JSON)
    Por ahora solo retorna JSON, la generación de PDF se implementará después
    """
    try:
        # Obtener eventos del período
        query = (
            supabase.table("vishum_events")
            .select("*")
            .gte("created_at", request.start_date.isoformat())
            .lte("created_at", request.end_date.isoformat())
        )

        if request.user_id:
            query = query.eq("user_id", request.user_id)
        if request.camera_id:
            query = query.eq("camera_id", request.camera_id)

        result = query.execute()

        # Por ahora retornamos un reporte JSON
        # TODO: Implementar generación de PDF con reportlab
        report_id = f"report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"

        return ReportResponse(
            report_id=report_id,
            url=None,  # URL se generará cuando se implemente el almacenamiento
            format=request.format,
            created_at=datetime.utcnow(),
        )
    except Exception as e:
        logger.exception("Error generating report")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/available")
async def list_available_reports(
    user_id: Optional[str] = Query(None, description="Filtrar por usuario"),
):
    """
    Listar reportes disponibles
    Por ahora retorna lista vacía, se implementará almacenamiento de reportes
    """
    return {
        "reports": [],
        "message": "Generación de reportes en desarrollo",
    }

