"""
Router para endpoints de análisis y estadísticas
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional
from datetime import datetime, timedelta
import logging

from models import HealthSummary
from supabase_client import get_supabase_client, Client

logger = logging.getLogger(__name__)

router = APIRouter()


def get_supabase() -> Client:
    """Dependency para obtener cliente de Supabase"""
    return get_supabase_client()


@router.get("/health-summary", response_model=HealthSummary)
async def get_health_summary(
    hours: int = Query(24, ge=1, le=168, description="Horas hacia atrás"),
    user_id: Optional[str] = Query(None, description="Filtrar por usuario"),
    camera_id: Optional[str] = Query(None, description="Filtrar por cámara"),
    supabase: Client = Depends(get_supabase),
):
    """
    Obtener resumen de estado de salud basado en eventos
    """
    try:
        # Calcular fechas
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(hours=hours)

        # Obtener eventos del período
        query = (
            supabase.table("vishum_events")
            .select("payload, camera_id, created_at")
            .gte("created_at", start_date.isoformat())
            .lte("created_at", end_date.isoformat())
        )

        if user_id:
            query = query.eq("user_id", user_id)
        if camera_id:
            query = query.eq("camera_id", camera_id)

        result = query.execute()

        # Procesar eventos para extraer información
        emotions = {}
        activities = {}
        health_status = {}
        alerts = []
        detections_by_camera = {}

        for item in result.data:
            payload = item.get("payload", {})
            camera_key = item.get("camera_id") or "default_camera"
            detections_by_camera[camera_key] = detections_by_camera.get(camera_key, 0) + 1
            
            # Extraer emociones
            if "emotions" in payload:
                for emotion in payload["emotions"]:
                    emotions[emotion] = emotions.get(emotion, 0) + 1

            # Extraer actividad
            if "activity" in payload:
                activity = payload["activity"]
                activities[activity] = activities.get(activity, 0) + 1

            # Extraer estado de salud
            if "healthStatus" in payload:
                status = payload["healthStatus"]
                health_status[status] = health_status.get(status, 0) + 1

            # Generar alertas si hay estados preocupantes
            if payload.get("healthStatus") in ["tired", "stressed"]:
                alerts.append(f"Estado de salud detectado: {payload.get('healthStatus')}")

        return HealthSummary(
            total_detections=len(result.data),
            emotions=emotions,
            activities=activities,
            health_status=health_status,
            alerts=alerts,
            period_hours=hours,
            by_camera=detections_by_camera,
        )
    except Exception as e:
        logger.exception("Error in analytics endpoint")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/trends")
async def get_trends(
    hours: int = Query(24, ge=1, le=168, description="Horas hacia atrás"),
    user_id: Optional[str] = Query(None, description="Filtrar por usuario"),
    camera_id: Optional[str] = Query(None, description="Filtrar por cámara"),
    supabase: Client = Depends(get_supabase),
):
    """
    Obtener tendencias de eventos en el tiempo
    """
    try:
        # Calcular fechas
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(hours=hours)

        # Obtener eventos
        query = (
            supabase.table("vishum_events")
            .select("event_type, camera_id, created_at")
            .gte("created_at", start_date.isoformat())
            .lte("created_at", end_date.isoformat())
        )

        if user_id:
            query = query.eq("user_id", user_id)
        if camera_id:
            query = query.eq("camera_id", camera_id)

        result = query.execute()

        # Agrupar por hora
        hourly_data = {}
        for item in result.data:
            created_at = datetime.fromisoformat(item["created_at"].replace("Z", "+00:00"))
            hour_key = created_at.strftime("%Y-%m-%d %H:00")
            
            if hour_key not in hourly_data:
                hourly_data[hour_key] = {}
            
            event_type = item["event_type"]
            hourly_data[hour_key][event_type] = hourly_data[hour_key].get(event_type, 0) + 1

        return {
            "period_hours": hours,
            "hourly_trends": hourly_data,
        }
    except Exception as e:
        logger.exception("Error in analytics endpoint")
        raise HTTPException(status_code=500, detail="Internal server error")

